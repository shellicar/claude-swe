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

// Commands that run on both sides but whose output is inherently
// nondeterministic — executed (state must advance) but not compared.
const NONDET_CMD = /\$RANDOM|\$\$|\$!|\bdate\b|\bmktemp\b|\btime\s|SECONDS|EPOCH|BASHPID|&\s*$|\bcurl\b|\bwget\b|\bpip3? (install|download)\b|\bsleep\s+\d+\s*(&&|;)|\bpgrep\b|\bpkill\b|\bps\s+(aux|ax|-)/m;

// A heredoc body is data, not command. `cat > f <<'EOF'` writing a file whose
// text mentions time, date or curl is perfectly deterministic, and testing the
// body excluded exactly the file-writing and `python - <<EOF` steps whose
// output matters most. Bodies are stripped before the test only; what runs is
// always the untouched command.
function withoutHeredocBodies(cmd) {
  const lines = cmd.split("\n");
  const kept = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    kept.push(line);
    const opens = [...line.matchAll(/<<(-?)\s*(?:'([^']*)'|"([^"]*)"|([A-Za-z_]\w*))/g)]
      // `<<<` is a here-string with no body, and its 2nd and 3rd `<` match here.
      .filter((m) => line[m.index - 1] !== "<")
      .map((m) => ({ dash: m[1] === "-", delim: m[2] ?? m[3] ?? m[4] }));
    for (const { dash, delim } of opens) {
      i++;
      while (i < lines.length && (dash ? lines[i].replace(/^\t+/, "") : lines[i]) !== delim) i++;
    }
  }
  return kept.join("\n");
}

const isNondet = (cmd) => NONDET_CMD.test(withoutHeredocBodies(cmd));

// Output noise both shells legitimately produce differently run-to-run.
function normalize(s) {
  return s
    .split("\n")
    .map((l) => {
      let t = l.trimStart();
      t = t.replace(/^bash-walker: /, "");
      const b = t.indexOf("bash: ");
      if (b >= 0 && b < 80) t = t.slice(b + 6);
      t = t.replace(/^line \d+: /, "");
      return t
        .replace(/\b\d+\.\d+ ?s(ec(onds)?)?\b/g, "TIME")
        .replace(/\b\d+(\.\d+)? ?ms\b/g, "TIME")
        .replace(/0x[0-9a-f]{4,}/gi, "ADDR")
        .replace(/\/tmp\/bash-walker[^\s'"]*/g, "TMPFILE")
        .replace(/\/tmp\/tmp[^\s'"]*/g, "TMPFILE")
        .replace(/\bpid \d+\b/g, "pid PID")
        .replace(/PYTHONHASHSEED=\d+/g, "PYTHONHASHSEED=SEED")
        .replace(/\brandom seed:\s*\d+/g, "random seed: SEED")
        .replace(/\b[0-9a-f]{40}\b/g, "SHA")
        .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, "UUID")
        .replace(/\b[0-9a-f]{16,}\b/g, "HEX")
        .replace(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?( [+-]\d{4})?/g, "TIMESTAMP")
        // Python's id(): a decimal memory address, e.g. Django/sympy repr
        // output like "GreaterThan(id=140737446409072)" — our hex-only
        // normalization above missed this decimal form entirely.
        .replace(/\bid=\d{8,}\b/g, "id=ID")
        .replace(/\bat 0x[0-9a-f]+\b/gi, "at ADDR");
    })
    .join("\n")
    .replace(/\n+$/, "");
}

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
  const manifest = new Map(
    readFileSync(`${ROOT}/image-manifest.txt`, "utf8")
      .trim()
      .split("\n")
      .map((l) => l.split(" "))
      .map(([inst]) => [inst, `swebench/sweb.eval.x86_64.${inst.replace("__", "_1776_")}:latest`]),
  );
  const local = new Set(
    execFileSync("docker", ["images", "--format", "{{.Repository}}:{{.Tag}}"], { encoding: "utf8" })
      .trim()
      .split("\n"),
  );
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
      imageLocal: local.has(image),
      commands,
    });
  }
  writeFileSync(CORPUS, JSON.stringify(entries));
  const localN = entries.filter((e) => e.imageLocal).length;
  const cmds = entries.reduce((a, e) => a + e.commands.length, 0);
  console.log(`${entries.length} trajectories (${localN} with local images), ${cmds} commands -> ${CORPUS}`);
}

function sh(args, input) {
  const r = spawnSync(args[0], args.slice(1), {
    input,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
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

function stepBash(name, cmd) {
  return sh(["docker", "exec", name, "sh", "-c", STEP_WRAP("bash -lc"), cmd]);
}
// Hidden (dotfile) and outside /opt: found live, `ls /opt` in a corpus
// command surfaced our own mounted binary as a spurious directory entry
// bash's container never has — a replay-harness artifact, not a walker
// divergence, but one worth not manufacturing.
const WALKER_MOUNT = "/root/.bash-walker";

function stepWalker(name, cmd, env) {
  return sh([
    "docker", "exec", ...env.flatMap((e) => ["-e", e]), name,
    "sh", "-c", STEP_WRAP(`${WALKER_MOUNT} -c`), cmd,
  ]);
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
  };
  const sortedLines = (s) => normalize(s).split("\n").sort().join("\n");
  try {
    const env = loginEnv(bashC);
    for (let i = 0; i < entry.commands.length; i++) {
      const cmd = entry.commands[i];
      const a = stepBash(bashC, cmd);
      const b = stepWalker(walkC, cmd, env);
      if (isNondet(cmd)) {
        result.skippedNondet++;
        continue;
      }
      result.compared++;
      if (a.code === b.code && normalize(a.out) === normalize(b.out)) continue;
      // Same lines, different order: concurrent writers (parallel test
      // runners, downloads, stdout/stderr buffering) — counted, not failed.
      if (a.code === b.code && sortedLines(a.out) === sortedLines(b.out)) {
        result.orderOnly.push({ step: i, cmd: cmd.slice(0, 160) });
        continue;
      }
      // Parallel-runner output sliced by a tail/head window: the window
      // lands differently per run even under bash-vs-bash. Status still
      // must match; content is uncomparable — counted and listed.
      if (a.code === b.code && /\|\s*(tail|head)\b/.test(cmd)) {
        result.windowNondet.push({ step: i, cmd: cmd.slice(0, 160) });
        continue;
      }
      // Both sides hit the step timeout: output truncated at an arbitrary
      // point on each side; only the status is comparable.
      if (a.code === 124 && b.code === 124) {
        result.windowNondet.push({ step: i, cmd: cmd.slice(0, 160) });
        continue;
      }
      // The self-test: rerun the step on the BASH side. If bash disagrees
      // with itself, this is run-to-run nondeterminism (unseeded random,
      // set ordering, live logs), not a walker divergence. The rerun may
      // mutate state, so the instance still stops here — classified, not
      // failed.
      const a2 = stepBash(bashC, cmd);
      if (a2.code !== a.code || normalize(a2.out) !== normalize(a.out)) {
        result.runNondet.push({ step: i, cmd: cmd.slice(0, 160) });
        break;
      }
      result.divergence = {
        step: i,
        cmd,
        bash: { code: a.code, out: a.out.slice(0, 2000) },
        walker: { code: b.code, out: b.out.slice(0, 2000) },
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
  let settle;
  const allDone = new Promise((res) => (settle = res));
  const flush = () => writeFileSync(resultsPath, JSON.stringify(results, null, 1));

  function startWorker() {
    const child = spawn(process.execPath, [process.argv[1], "worker"], { stdio: ["pipe", "pipe", "inherit"] });
    const w = { child, busy: null, retiring: false };
    workers.add(w);
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
    const target = Math.min(want, queue.length + busy);
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
    for (const w of workers) {
      if (queue.length === 0) break;
      if (w.busy || w.retiring) continue;
      w.busy = queue.shift();
      w.child.stdin.write(`${JSON.stringify(w.busy)}\n`);
    }
    if (queue.length === 0 && ![...workers].some((w) => w.busy)) {
      for (const w of workers) {
        if (!w.retiring) {
          w.retiring = true;
          w.child.stdin.end();
        }
      }
      if (workers.size === 0) settle();
    }
  }

  const timer = setInterval(() => {
    const next = readWorkerDial(want, ceiling);
    if (next !== want) {
      console.log(`workers: ${want} -> ${next}${next === 0 ? " (paused, progress kept)" : ""}`);
      want = next;
    }
    pump();
  }, 2000);

  pump();
  await allDone;
  clearInterval(timer);
  flush();
  summarize(results, resultsPath);
}

// A worker holds no share of the work: it replays whatever single trajectory
// the parent writes to its stdin and reports one JSON line per trajectory,
// which is what lets the pool grow and shrink mid-run. Progress goes to
// stderr so stdout carries results and nothing else.
async function worker() {
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
