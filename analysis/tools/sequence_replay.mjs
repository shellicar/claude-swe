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
// Containers are created, owned, and removed by this script.

import { execFileSync, spawnSync, spawn } from "node:child_process";
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const CORPUS = "/tmp/sequence_corpus.json";
const WALKER = `${ROOT}/rust/target-linux/release/bash-walker`;
const STEP_TIMEOUT_S = 90;

// Commands that run on both sides but whose output is inherently
// nondeterministic — executed (state must advance) but not compared.
const NONDET_CMD = /\$RANDOM|\$\$|\$!|\bdate\b|\bmktemp\b|\btime\s|SECONDS|EPOCH|BASHPID|&\s*$|\bcurl\b|\bwget\b|\bpip3? (install|download)\b|\bsleep\s+\d+\s*(&&|;)|\bpgrep\b|\bpkill\b|\bps\s+(aux|ax|-)/m;

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
        .replace(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?( [+-]\d{4})?/g, "TIMESTAMP");
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
function stepWalker(name, cmd, env) {
  return sh([
    "docker", "exec", ...env.flatMap((e) => ["-e", e]), name,
    "sh", "-c", STEP_WRAP("/opt/bash-walker -c"), cmd,
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
    [...common, "--name", walkC, "-v", `${WALKER}:/opt/bash-walker:ro`, entry.image, "sleep", "infinity"],
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
      if (NONDET_CMD.test(cmd)) {
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

async function run(argv) {
  const arg = (n, d) => {
    const i = argv.indexOf(n);
    return i >= 0 ? argv[i + 1] : d;
  };
  const sample = parseFloat(arg("--sample", "0.01"));
  const seed = parseInt(arg("--seed", "1"), 10);
  const limit = parseInt(arg("--limit", "0"), 10);
  const parallel = parseInt(arg("--parallel", "1"), 10);
  const shard = arg("--shard", "");
  const resultsPath = arg("--results", "/tmp/sequence_replay_results.json");
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

  // Parent mode: shard the picked set across N copies of this script — the
  // per-trajectory work stays simple and synchronous inside each shard.
  if (parallel > 1 && !shard) {
    console.log(`replaying ${picked.length}/${all.length} trajectories across ${parallel} shards (sample=${sample}, seed=${seed})`);
    const kids = [];
    for (let k = 0; k < parallel; k++) {
      const kidArgs = [
        process.argv[1], "run",
        "--sample", String(sample), "--seed", String(seed),
        ...(limit > 0 ? ["--limit", String(limit)] : []),
        ...(argv.includes("--resume") ? ["--resume"] : []),
        "--shard", `${k}/${parallel}`,
        "--results", `/tmp/sequence_replay_results-${k}.json`,
      ];
      kids.push(new Promise((res) => {
        const c = spawn(process.execPath, kidArgs, { stdio: ["ignore", "inherit", "inherit"] });
        c.on("exit", res);
      }));
    }
    await Promise.all(kids);
    const merged = [];
    for (let k = 0; k < parallel; k++) {
      merged.push(...JSON.parse(readFileSync(`/tmp/sequence_replay_results-${k}.json`, "utf8")));
    }
    writeFileSync(resultsPath, JSON.stringify(merged, null, 1));
    summarize(merged, resultsPath);
    return;
  }

  if (shard) {
    const [k, n] = shard.split("/").map(Number);
    picked = picked.filter((_, i) => i % n === k);
  } else {
    console.log(`replaying ${picked.length}/${all.length} trajectories (sample=${sample}, seed=${seed})`);
  }
  // Resume: keep prior completed results (same sample/seed/parallel), replay
  // only what's missing.
  let results = [];
  if (argv.includes("--resume") && existsSync(resultsPath)) {
    results = JSON.parse(readFileSync(resultsPath, "utf8"));
  }
  const done = new Set(results.map((r) => r.id));
  const tag = shard ? `[shard ${shard}] ` : "";
  for (const [i, e] of picked.entries()) {
    if (done.has(e.id)) continue;
    process.stdout.write(`${tag}[${i + 1}/${picked.length}] ${e.id} (${e.commands.length} cmds) ... `);
    const t0 = Date.now();
    const r = replayOne(e, `${process.pid}-${i}`);
    results.push(r);
    // Flush after every trajectory so an interrupted run loses nothing.
    writeFileSync(resultsPath, JSON.stringify(results, null, 1));
    const secs = ((Date.now() - t0) / 1000).toFixed(0);
    const extras = `${r.orderOnly.length} order-only, ${r.windowNondet.length} window-nondet`;
    const verdict = r.divergence
      ? `DIVERGED at step ${r.divergence.step}`
      : r.runNondet.length
        ? `stopped run-nondet at step ${r.runNondet[0].step}, ${r.compared} compared (${extras})`
        : `ok ${r.compared} compared (${extras}), ${r.skippedNondet} nondet-skipped`;
    console.log(`${tag}${verdict} (${secs}s)`);
  }
  writeFileSync(resultsPath, JSON.stringify(results, null, 1));
  if (!shard) summarize(results, resultsPath);
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
else {
  console.error("usage: sequence_replay.mjs extract | run [--sample F] [--seed N] [--limit N] [--parallel N] [--resume]");
  process.exit(2);
}
