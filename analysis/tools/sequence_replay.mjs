#!/usr/bin/env node
// Sequence replay: differential validation of bash-walker against each
// instance image's own bash, over whole recorded trajectories.
//
// Two pristine containers per trajectory — one driven by `bash -lc` (the
// baseline interpreter), one by the walker — replay the same command
// sequence in order, comparing combined output + exit status at every step.
// State divergence is self-revealing: if a command writes differently, later
// commands read the difference. First compared mismatch stops the instance.
//
//   node analysis/tools/sequence_replay.mjs extract
//   node analysis/tools/sequence_replay.mjs run --sample 0.01 [--seed 1] [--limit N]
//
// Worker count is a live dial, not a launch-time decision: the parent holds a
// queue and hands out one trajectory at a time, so workers can join or retire
// mid-run. `echo N > .sequence-replay-state/workers` retunes a running job
// from another terminal, and 0 drains to idle and holds.
//
// Containers are created, owned, and removed by this script.

import { execFileSync, spawnSync, spawn } from "node:child_process";
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { createInterface } from "node:readline";

import { compareTraces } from "./trace_compare.mjs";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
// Machine capacity comes from the one place that declares it.
const RIG = JSON.parse(readFileSync(`${ROOT}/rig.json`, "utf8"));
// On the repo's own disk, not /tmp: macOS clears /tmp on reboot, which lost
// an entire multi-hour run's progress (and the corpus itself) to a restart.
const STATE_DIR = new URL("../../.sequence-replay-state", import.meta.url).pathname;
mkdirSync(STATE_DIR, { recursive: true });
const CORPUS = `${STATE_DIR}/sequence_corpus.json`;
const WALKER = `${ROOT}/rust/target-linux/release/bash-walker`;
const STEP_TIMEOUT_S = RIG.replayStepTimeoutS;


function* trajFiles(dir) {
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    const st = statSync(p);
    if (st.isDirectory()) yield* trajFiles(p);
    else if (e.endsWith(".traj.json")) yield p;
  }
}

function commandsOf(traj) {
  const out = [];
  for (const m of traj.messages ?? []) {
    if (m.role !== "assistant") continue;
    for (const ch of m.extra?.response?.choices ?? []) {
      for (const tc of ch.message?.tool_calls ?? []) {
        try {
          const args = JSON.parse(tc.function.arguments);
          if (typeof args.command === "string") out.push(args.command);
        } catch {}
      }
    }
  }
  return out;
}

function extract() {
  // The manifest's second column is the whole point of that file: a digest
  // pinned reference per instance, for every dataset. Rebuilding a name from
  // the instance id instead assumed the Verified pattern, so Pro
  // (jefzda/sweap-images) and Multi (mswebench/*) asked for tags that cannot
  // exist and dropped out as "no local image", and even Verified replayed
  // whatever :latest pointed at rather than the digest the rig pins.
  const manifest = new Map(
    readFileSync(`${ROOT}/image-manifest.txt`, "utf8")
      .trim()
      .split("\n")
      .map((l) => l.split(" ")),
  );
  // Ask docker about each reference rather than parsing its listing. The
  // listing's format differs between image stores, and getting it wrong looks
  // exactly like having pulled nothing.
  const isLocal = (ref) =>
    spawnSync("docker", ["image", "inspect", "--format", "{{.Id}}", ref], { stdio: "ignore" }).status === 0;
  const entries = [];
  for (const f of trajFiles(`${ROOT}/runs`)) {
    if (f.includes("/walker-")) continue; // walker runs are not ground truth
    let d;
    try {
      d = JSON.parse(readFileSync(f, "utf8"));
    } catch {
      continue;
    }
    const inst = d.instance_id;
    const image = manifest.get(inst);
    if (!image) continue;
    const commands = commandsOf(d);
    if (commands.length === 0) continue;
    entries.push({
      id: f.slice(ROOT.length + 1).replace(/\/[^/]*$/, ""),
      instance: inst,
      image,
      imageLocal: false,
      commands,
    });
  }

  // One inspect per distinct image, not per trajectory.
  const present = new Map();
  for (const e of entries) {
    if (!present.has(e.image)) present.set(e.image, isLocal(e.image));
    e.imageLocal = present.get(e.image);
  }
  writeFileSync(CORPUS, JSON.stringify(entries));
  const localN = entries.filter((e) => e.imageLocal).length;
  const cmds = entries.reduce((a, e) => a + e.commands.length, 0);
  console.log(`${entries.length} trajectories (${localN} with local images), ${cmds} commands -> ${CORPUS}`);
  if (localN === 0 && entries.length > 0) {
    console.log(`none of the ${present.size} images are present. one of them, to check by hand:`);
    console.log(`  docker image inspect ${entries[0].image}`);
  }
}

function sh(args, input) {
  const r = spawnSync(args[0], args.slice(1), {
    input,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
    // Own process group, so a terminal Ctrl-C does not reach these. Without
    // it the docker call in flight dies with the group and the step it was
    // running returns a truncated answer, which is worse than not stopping.
    detached: true,
  });
  return { out: (r.stdout ?? "") + (r.stderr ?? ""), code: r.status ?? 128 };
}

// Both sides write combined output to a FILE inside the container, then cat
// it — never a pipe held by the step's descendants. A backgrounded
// grandchild that outlives the 90s timeout then holds the file, not the
// exec stream, so `docker exec` always returns. (A pipe here hung two
// shards of the first 10% run for half an hour at 0% CPU.)
const STEP_WRAP = (interp) =>
  `timeout ${STEP_TIMEOUT_S} ${interp} "$0" > /tmp/.seqrep-step.out 2>&1 < /dev/null; ec=$?; cat /tmp/.seqrep-step.out; exit $ec`;

// What the shell decided, rather than what the programs it ran printed. The
// trace goes into the same combined stream, so it needs a prefix nothing else
// emits: a bare `+ ` collides with any diff. Both sides get the same PS4 and
// the same `set -x`, and bash repeats only PS4's first character per
// substitution level, which the walker reproduces.
const TRACE_MARK = "@@sqrp@@ ";
const TRACE_LINE = new RegExp(`^${TRACE_MARK[0]}+${TRACE_MARK.slice(1)}`);
// Set inside the command, not in the environment: a login shell sources the
// image's profile and does not end up with an inherited PS4, so `bash -lc`
// traced with a bare `+ ` and nothing was recognised as trace at all.
const traced = (cmd) => `PS4='${TRACE_MARK}'\nset -x\n${cmd}`;

/// The trace lines, and everything that is not trace, kept apart.
function split(out) {
  const trace = [];
  const rest = [];
  for (const line of out.split("\n")) (TRACE_LINE.test(line) ? trace : rest).push(line);
  return { trace, output: rest.join("\n") };
}

function stepBash(name, cmd) {
  return sh(["docker", "exec", name, "sh", "-c", STEP_WRAP("bash -lc"), traced(cmd)]);
}
// Hidden (dotfile) and outside /opt: found live, `ls /opt` in a corpus
// command surfaced our own mounted binary as a spurious directory entry
// bash's container never has — a replay-harness artifact, not a walker
// divergence, but one worth not manufacturing.
const WALKER_MOUNT = "/root/.bash-walker";

function stepWalker(name, cmd, env) {
  return sh([
    "docker", "exec", ...env.flatMap((e) => ["-e", e]), name,
    "sh", "-c", STEP_WRAP(`${WALKER_MOUNT} -c`), traced(cmd),
  ]);
}

/// How many adjacent trace lines may legitimately appear in any order: the
/// widest pipeline in this command, answered by the parser rather than by
/// counting bars in a string. Asked only when traces disagree, which is rare.
function pipelineWidth(walkC, cmd) {
  const r = sh(["docker", "exec", "-i", walkC, WALKER_MOUNT, "--pipeline-width"], cmd);
  const n = Number.parseInt(r.out.trim(), 10);
  return Number.isInteger(n) && n > 0 ? n : 1;
}

// The walker must see exactly the environment a login bash gets in this
// image (conda activation, cargo paths, whatever the profile sets) — read
// it from the bash-side container instead of assuming any image family.
function loginEnv(bashC) {
  const r = sh(["docker", "exec", bashC, "bash", "-lc", "printenv -0"]);
  return r.out
    .split("\0")
    .filter((e) => e.includes("=") && !/^(_|SHLVL|PWD|OLDPWD)=/.test(e));
}

function replayOne(entry, tag) {
  const bashC = `seqrep-bash-${tag}`;
  const walkC = `seqrep-walk-${tag}`;
  const common = ["run", "-d", "--platform", "linux/amd64", "--network", "none"];
  execFileSync("docker", [...common, "--name", bashC, entry.image, "sleep", "infinity"], { stdio: "pipe" });
  execFileSync(
    "docker",
    [...common, "--name", walkC, "-v", `${WALKER}:${WALKER_MOUNT}:ro`, entry.image, "sleep", "infinity"],
    { stdio: "pipe" },
  );
  const result = {
    id: entry.id,
    instance: entry.instance,
    steps: entry.commands.length,
    compared: 0,
    skippedNondet: 0,
    orderOnly: [],
    windowNondet: [],
    runNondet: [],
    divergence: null,
    // Kept as fields so a results file written before and after the switch to
    // trace comparison still reads; only orderOnly and windowNondet are
    // populated now, and both name a cause rather than a threshold.
  };
  try {
    const env = loginEnv(bashC);
    for (let i = 0; i < entry.commands.length; i++) {
      const cmd = entry.commands[i];
      const a = stepBash(bashC, cmd);
      const b = stepWalker(walkC, cmd, env);
      const at = split(a.out);
      const bt = split(b.out);

      // The exit status is the shell's own answer and is compared always.
      // The trace is the decisions. Program output is neither: it belongs to
      // whatever ran, and comparing it is what made this harness need a
      // normalizer, a nondeterminism filter, a window rule and a self-test.
      result.compared++;
      if (a.code === b.code) {
        const verdict = compareTraces(at.trace, bt.trace, 1);
        if (verdict.equal) continue;
        // Disagreed, so ask the parser how many adjacent lines this command
        // is allowed to permute. Only a pipeline starts things concurrently,
        // and bash disagrees with itself there about once in thirty runs.
        const scoped = compareTraces(at.trace, bt.trace, pipelineWidth(walkC, cmd));
        if (scoped.equal) {
          result.orderOnly.push({ step: i, cmd: cmd.slice(0, 160) });
          continue;
        }
        result.divergence = {
          step: i,
          cmd,
          bash: { code: a.code, out: at.trace.slice(Math.max(0, scoped.at - 3), scoped.at + 4).join("\n") },
          walker: { code: b.code, out: bt.trace.slice(Math.max(0, scoped.at - 3), scoped.at + 4).join("\n") },
        };
        break;
      }
      // Statuses differ. A step both sides cut off at the timeout says
      // nothing either way.
      if (a.code === 124 && b.code === 124) {
        result.windowNondet.push({ step: i, cmd: cmd.slice(0, 160) });
        continue;
      }
      result.divergence = {
        step: i,
        cmd,
        bash: { code: a.code, out: at.output.slice(0, 2000) },
        walker: { code: b.code, out: bt.output.slice(0, 2000) },
      };
      break;
    }
  } finally {
    sh(["docker", "rm", "-f", bashC, walkC]);
  }
  return result;
}

function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// The live worker dial: a plain number in a file, re-read between hand-outs.
// A number rather than a signal because it is settable from any terminal,
// readable with `cat`, and says what it means; zero is a pause, which is how a
// replay yields the machine to a paid run without discarding its progress.
const WORKERS_FILE = `${STATE_DIR}/workers`;
let lastDial = null;

function readWorkerDial(current, ceiling) {
  let raw;
  try {
    raw = readFileSync(WORKERS_FILE, "utf8").trim();
  } catch {
    return current;
  }
  if (raw === lastDial) return current;
  lastDial = raw;
  const n = Number.parseInt(raw, 10);
  if (!Number.isInteger(n) || n < 0 || String(n) !== raw) {
    console.log(`workers: ${JSON.stringify(raw.slice(0, 20))} is not a count, staying at ${current}`);
    return current;
  }
  if (n > ceiling) {
    console.log(`workers: ${n} is above this machine's ceiling ${ceiling}, using ${ceiling}`);
    return ceiling;
  }
  return n;
}

function verdictOf(r) {
  const extras = `${r.orderOnly.length} order-only, ${r.windowNondet.length} window-nondet`;
  if (r.divergence) return `DIVERGED at step ${r.divergence.step}`;
  if (r.runNondet.length) return `stopped run-nondet at step ${r.runNondet[0].step}, ${r.compared} compared (${extras})`;
  return `ok ${r.compared} compared (${extras}), ${r.skippedNondet} nondet-skipped`;
}

async function run(argv) {
  const arg = (n, d) => {
    const i = argv.indexOf(n);
    return i >= 0 ? argv[i + 1] : d;
  };
  const sample = parseFloat(arg("--sample", "0.01"));
  const seed = parseInt(arg("--seed", "1"), 10);
  const limit = parseInt(arg("--limit", "0"), 10);
  const parallel = parseInt(arg("--parallel", String(RIG.replayParallel)), 10);
  const idsFile = arg("--ids", "");
  const resultsPath = arg("--results", `${STATE_DIR}/sequence_replay_results.json`);
  if (!existsSync(CORPUS)) {
    console.error("no corpus; run `extract` first");
    process.exit(2);
  }
  const all = JSON.parse(readFileSync(CORPUS, "utf8")).filter((e) => e.imageLocal);
  const rnd = mulberry(seed);
  const shuffled = all
    .map((e) => [rnd(), e])
    .sort((x, y) => x[0] - y[0])
    .map(([, e]) => e);
  let picked = shuffled.slice(0, Math.max(1, Math.round(all.length * sample)));
  if (limit > 0) picked = picked.slice(0, limit);
  if (idsFile) {
    const ids = new Set(JSON.parse(readFileSync(idsFile, "utf8")));
    picked = picked.filter((e) => ids.has(e.id));
  }

  // Estimated seconds per trajectory: both sides pay every commanded sleep,
  // plus a few seconds of real work per step. Scheduling input only, the
  // commands themselves are never touched. Longest first is now the whole
  // scheduler: nothing is tied to a worker until that worker is free to take
  // it, so a slow trajectory delays only itself.
  const cost = (e) => {
    let sleep = 0;
    for (const c of e.commands) {
      for (const m of c.matchAll(/\bsleep\s+(\d+)\b/g)) sleep += parseInt(m[1], 10);
    }
    return 2 * sleep + 4 * e.commands.length;
  };
  picked = [...picked].sort((a, b) => cost(b) - cost(a));

  // Resume keeps prior completed results and replays only what is missing.
  // It no longer depends on the worker count, because no trajectory belongs
  // to a particular worker.
  let results = [];
  if (argv.includes("--resume") && existsSync(resultsPath)) {
    results = JSON.parse(readFileSync(resultsPath, "utf8"));
  }
  const done = new Set(results.map((r) => r.id));
  const queue = picked.filter((e) => !done.has(e.id));
  const total = picked.length;
  let finished = total - queue.length;

  const ceiling = Math.max(parallel, RIG.replayParallel);
  writeFileSync(WORKERS_FILE, `${parallel}\n`);
  lastDial = String(parallel);
  let want = parallel;

  console.log(`replaying ${total}/${all.length} trajectories (sample=${sample}, seed=${seed}); ${queue.length} to do, ${finished} already done`);
  console.log(`workers: ${want}, change live with \`echo N > ${WORKERS_FILE}\` (0 pauses, ceiling ${ceiling})`);

  const workers = new Set();
  const retried = new Set();
  // Every worker pid this run has spawned. Container names carry the pid that
  // made them, so abandoning a run can remove exactly its own containers and
  // nothing else on the machine.
  const spawnedPids = new Set();
  let draining = false;
  let settle;
  const allDone = new Promise((res) => (settle = res));
  const flush = () => writeFileSync(resultsPath, JSON.stringify(results, null, 1));

  function startWorker() {
    const child = spawn(process.execPath, [process.argv[1], "worker"], { stdio: ["pipe", "pipe", "inherit"] });
    const w = { child, busy: null, retiring: false };
    workers.add(w);
    spawnedPids.add(child.pid);
    let buf = "";
    child.stdout.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      buf += chunk;
      for (let nl = buf.indexOf("\n"); nl >= 0; nl = buf.indexOf("\n")) {
        const r = JSON.parse(buf.slice(0, nl));
        buf = buf.slice(nl + 1);
        w.busy = null;
        results.push(r);
        // Flush after every trajectory so an interrupted run loses nothing.
        flush();
        finished++;
        console.log(`[${finished}/${total}] ${r.id}: ${verdictOf(r)} (${r.seconds}s)`);
      }
      pump();
    });
    child.on("exit", () => {
      workers.delete(w);
      // A worker that dies mid-trajectory hands that work back once. A second
      // death on the same trajectory is reported rather than looped on.
      if (w.busy) {
        const e = w.busy;
        w.busy = null;
        if (retried.has(e.id)) {
          console.log(`worker died twice on ${e.id}, leaving it undone`);
        } else {
          retried.add(e.id);
          queue.unshift(e);
          console.log(`worker died on ${e.id}, requeued`);
        }
      }
      pump();
    });
  }

  function pump() {
    const busy = [...workers].filter((w) => w.busy).length;
    const target = draining ? 0 : Math.min(want, queue.length + busy);
    let live = [...workers].filter((w) => !w.retiring).length;
    while (live < target) {
      startWorker();
      live++;
    }
    // Only an idle worker is retired, so a trajectory is never abandoned and
    // its two containers are always removed by the worker that made them.
    for (const w of workers) {
      if (live <= target) break;
      if (!w.busy && !w.retiring) {
        w.retiring = true;
        w.child.stdin.end();
        live--;
      }
    }
    if (!draining) {
      for (const w of workers) {
        if (queue.length === 0) break;
        if (w.busy || w.retiring) continue;
        w.busy = queue.shift();
        w.child.stdin.write(`${JSON.stringify(w.busy)}\n`);
      }
    }
    if (draining ? workers.size === 0 : queue.length === 0 && ![...workers].some((w) => w.busy)) {
      for (const w of workers) {
        if (!w.retiring) {
          w.retiring = true;
          w.child.stdin.end();
        }
      }
      if (workers.size === 0) settle();
    }
  }

  // Ctrl-C drains rather than stops dead: a killed worker abandons two
  // containers mid-trajectory, and finding them afterwards is the reader's
  // problem. Everything already finished is on disk either way.
  process.on("SIGINT", () => {
    if (draining) {
      const stranded = [...workers].filter((w) => w.busy).length;
      console.log(`\nabandoning ${stranded} trajectories in flight`);
      for (const w of workers) w.child.kill();
      const filters = [...spawnedPids].flatMap((pid) => [
        "--filter", `name=seqrep-bash-${pid}-`,
        "--filter", `name=seqrep-walk-${pid}-`,
      ]);
      const ids = sh(["docker", "ps", "-aq", ...filters]).out.trim().split("\n").filter(Boolean);
      if (ids.length > 0) {
        sh(["docker", "rm", "-f", ...ids]);
      }
      console.log(`removed ${ids.length} containers this run created`);
      flush();
      process.exit(130);
    }
    draining = true;
    const busy = [...workers].filter((w) => w.busy).length;
    console.log(`\ndraining: ${busy} trajectories still running, each removes its own containers as it finishes`);
    console.log(`${queue.length} never started, kept for --resume. Ctrl-C again to abandon the ${busy} instead.`);
    pump();
  });

  const timer = setInterval(() => {
    if (!draining) {
      const next = readWorkerDial(want, ceiling);
      if (next !== want) {
        console.log(`workers: ${want} -> ${next}${next === 0 ? " (paused, progress kept)" : ""}`);
        want = next;
      }
    }
    pump();
  }, 2000);

  pump();
  await allDone;
  clearInterval(timer);
  flush();
  summarize(results, resultsPath);
  if (queue.length > 0) {
    console.log(`stopped early: ${queue.length} trajectories not replayed. Add --resume to the same command to continue.`);
  }
}

// A worker holds no share of the work: it replays whatever single trajectory
// the parent writes to its stdin and reports one JSON line per trajectory,
// which is what lets the pool grow and shrink mid-run. Progress goes to
// stderr so stdout carries results and nothing else.
async function worker() {
  // Ctrl-C reaches every process in the terminal's group, so a worker that
  // took the default action would die holding two containers. The parent
  // stops us by closing stdin instead, after the trajectory in hand is done.
  process.on("SIGINT", () => {});
  let n = 0;
  for await (const line of createInterface({ input: process.stdin })) {
    if (!line.trim()) continue;
    const entry = JSON.parse(line);
    process.stderr.write(`> ${entry.id} (${entry.commands.length} cmds)\n`);
    const t0 = Date.now();
    const r = replayOne(entry, `${process.pid}-${n++}`);
    r.seconds = Math.round((Date.now() - t0) / 1000);
    process.stdout.write(`${JSON.stringify(r)}\n`);
  }
}

function summarize(results, resultsPath) {
  const diverged = results.filter((r) => r.divergence);
  const compared = results.reduce((a, r) => a + r.compared, 0);
  const skipped = results.reduce((a, r) => a + r.skippedNondet, 0);
  const orderOnly = results.reduce((a, r) => a + r.orderOnly.length, 0);
  const windowN = results.reduce((a, r) => a + r.windowNondet.length, 0);
  const runN = results.reduce((a, r) => a + (r.runNondet?.length ?? 0), 0);
  console.log(`\ntrajectories: ${results.length}  clean: ${results.length - diverged.length}  diverged: ${diverged.length}`);
  console.log(`steps compared: ${compared}  order-only: ${orderOnly}  window-nondet: ${windowN}  run-nondet stops: ${runN}  nondet-skipped: ${skipped}`);
  for (const r of diverged) {
    console.log(`---\n${r.id} step ${r.divergence.step}\nCMD: ${r.divergence.cmd.slice(0, 300)}`);
    console.log(`  bash   rc=${r.divergence.bash.code}: ${JSON.stringify(r.divergence.bash.out.slice(0, 400))}`);
    console.log(`  walker rc=${r.divergence.walker.code}: ${JSON.stringify(r.divergence.walker.out.slice(0, 400))}`);
  }
  console.log(`\nfull results: ${resultsPath}`);
}

const [mode, ...rest] = process.argv.slice(2);
if (mode === "extract") extract();
else if (mode === "run") await run(rest);
else if (mode === "worker") await worker();
else {
  console.error("usage: sequence_replay.mjs extract | run [--sample F] [--seed N] [--limit N] [--parallel N] [--resume]");
  process.exit(2);
}
