#!/usr/bin/env node
// Sets a machine up and starts the replay. One command, everything.
//
//   node analysis/tools/replay_setup.mjs [--parallel N]
//
// Builds the corpus, pulls every image the corpus needs and does not have,
// rebuilds the corpus so it sees them, and starts the run. Safe to re-run: it
// pulls only what is missing and the replay resumes rather than restarting.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const SELF = `${ROOT}/analysis/tools/sequence_replay.mjs`;
const CORPUS = `${ROOT}/.sequence-replay-state/sequence_corpus.json`;
const RIG = JSON.parse(readFileSync(`${ROOT}/rig.json`, "utf8"));

const argv = process.argv.slice(2);
const at = argv.indexOf("--parallel");
const parallel = at >= 0 ? argv[at + 1] : String(RIG.replayParallel);

const die = (msg, fix) => {
  console.error(`stopped: ${msg}`);
  if (fix) console.error(`  ${fix}`);
  process.exit(1);
};

function firstTrajectory(dir) {
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) {
      const found = firstTrajectory(p);
      if (found) return found;
    } else if (e.endsWith(".traj.json")) {
      return p;
    }
  }
  return null;
}

// The two things that fail silently, checked before anything long starts.
const sample = existsSync(`${ROOT}/runs`) && firstTrajectory(`${ROOT}/runs`);
if (!sample) die("runs/ holds no trajectories, so there is nothing to replay");
if (readFileSync(sample, "utf8").startsWith("version https://git-lfs")) {
  die("the trajectories are Git LFS pointers, not content", "git -c core.hooksPath=.git/hooks lfs install --local && git lfs pull");
}
if (spawnSync("docker", ["version", "--format", "{{.Server.Version}}"], { stdio: "ignore" }).status !== 0) {
  die("docker is not reachable");
}
if (!existsSync(`${ROOT}/rust/target-linux/release/bash-walker`)) {
  die(
    "the walker binary is not built",
    "docker run --rm -v $PWD/rust:/src -w /src -e CARGO_TARGET_DIR=/src/target-linux rust:alpine sh -c 'apk add --no-cache musl-dev && cargo build --release -p bash-walker'",
  );
}

const extract = () => {
  const r = spawnSync(process.execPath, [SELF, "extract"], { stdio: "inherit" });
  if (r.status !== 0) die("extract failed");
  return JSON.parse(readFileSync(CORPUS, "utf8"));
};

let corpus = extract();

// Every image the corpus needs, heaviest coverage first so an interrupted or
// disk-limited pull still leaves the most replayable.
const byImage = new Map();
for (const e of corpus) {
  const rec = byImage.get(e.image) ?? { commands: 0, local: e.imageLocal };
  rec.commands += e.commands.length;
  byImage.set(e.image, rec);
}
const missing = [...byImage].filter(([, r]) => !r.local).sort((a, b) => b[1].commands - a[1].commands);

if (missing.length > 0) {
  console.log(`\npulling ${missing.length} images`);
  let n = 0;
  for (const [image] of missing) {
    n++;
    console.log(`\n[${n}/${missing.length}] ${image}`);
    const r = spawnSync("docker", ["pull", image], { stdio: "inherit" });
    if (r.status !== 0) {
      console.error(`\npull failed after ${n - 1} of ${missing.length}. Replaying what is present.`);
      break;
    }
  }
  corpus = extract();
}

const replayable = corpus.filter((e) => e.imageLocal).length;
if (replayable === 0) die("no image the corpus needs is present, so there is nothing to replay");

console.log(`\nstarting the replay: ${replayable} of ${corpus.length} trajectories, ${parallel} workers`);
console.log(`change workers while it runs: echo N > ${ROOT}/.sequence-replay-state/workers`);
const run = spawnSync(process.execPath, [SELF, "run", "--sample", "1.0", "--parallel", parallel, "--resume"], {
  stdio: "inherit",
});
process.exit(run.status ?? 1);
