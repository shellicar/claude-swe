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

import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const CORPUS = "/tmp/sequence_corpus.json";
const WALKER = `${ROOT}/rust/target-linux/release/bash-walker`;
const STEP_TIMEOUT_S = 90;

// Commands that run on both sides but whose output is inherently
// nondeterministic — executed (state must advance) but not compared.
const NONDET_CMD = /\$RANDOM|\$\$|\$!|\bdate\b|\bmktemp\b|\btime\s|SECONDS|EPOCH|BASHPID|&\s*$|\bcurl\b|\bwget\b|\bpip3? (install|download)\b/m;

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
        .replace(/\brandom seed:\s*\d+/g, "random seed: SEED");
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

// Both sides run under `sh -c '... "$0" 2>&1'` so output arrives as one
// combined stream, matching the walker's own contract.
function stepBash(name, cmd) {
  return sh([
    "docker", "exec", name,
    "sh", "-c", `timeout ${STEP_TIMEOUT_S} bash -lc "$0" 2>&1`, cmd,
  ]);
}
function stepWalker(name, cmd, env) {
  return sh([
    "docker", "exec", ...env.flatMap((e) => ["-e", e]), name,
    "sh", "-c", `timeout ${STEP_TIMEOUT_S} /opt/bash-walker -c "$0" 2>&1`, cmd,
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

function run(argv) {
  const arg = (n, d) => {
    const i = argv.indexOf(n);
    return i >= 0 ? argv[i + 1] : d;
  };
  const sample = parseFloat(arg("--sample", "0.01"));
  const seed = parseInt(arg("--seed", "1"), 10);
  const limit = parseInt(arg("--limit", "0"), 10);
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
  console.log(`replaying ${picked.length}/${all.length} trajectories (sample=${sample}, seed=${seed})`);
  const results = [];
  for (const [i, e] of picked.entries()) {
    process.stdout.write(`[${i + 1}/${picked.length}] ${e.id} (${e.commands.length} cmds) ... `);
    const t0 = Date.now();
    const r = replayOne(e, `${process.pid}-${i}`);
    results.push(r);
    const secs = ((Date.now() - t0) / 1000).toFixed(0);
    const extras = `${r.orderOnly.length} order-only, ${r.windowNondet.length} window-nondet`;
    console.log(r.divergence ? `DIVERGED at step ${r.divergence.step} (${secs}s)` : `ok ${r.compared} compared (${extras}), ${r.skippedNondet} nondet-skipped (${secs}s)`);
  }
  const diverged = results.filter((r) => r.divergence);
  const compared = results.reduce((a, r) => a + r.compared, 0);
  const skipped = results.reduce((a, r) => a + r.skippedNondet, 0);
  const orderOnly = results.reduce((a, r) => a + r.orderOnly.length, 0);
  const windowN = results.reduce((a, r) => a + r.windowNondet.length, 0);
  console.log(`\ntrajectories: ${results.length}  clean: ${results.length - diverged.length}  diverged: ${diverged.length}`);
  console.log(`steps compared: ${compared}  order-only: ${orderOnly}  window-nondet: ${windowN}  nondet-skipped: ${skipped}`);
  for (const r of diverged) {
    console.log(`---\n${r.id} step ${r.divergence.step}\nCMD: ${r.divergence.cmd.slice(0, 300)}`);
    console.log(`  bash   rc=${r.divergence.bash.code}: ${JSON.stringify(r.divergence.bash.out.slice(0, 400))}`);
    console.log(`  walker rc=${r.divergence.walker.code}: ${JSON.stringify(r.divergence.walker.out.slice(0, 400))}`);
  }
  writeFileSync("/tmp/sequence_replay_results.json", JSON.stringify(results, null, 1));
  console.log("\nfull results: /tmp/sequence_replay_results.json");
}

const [mode, ...rest] = process.argv.slice(2);
if (mode === "extract") extract();
else if (mode === "run") run(rest);
else {
  console.error("usage: sequence_replay.mjs extract | run [--sample F] [--seed N] [--limit N]");
  process.exit(2);
}
