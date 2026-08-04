#!/usr/bin/env node
// Prepares a machine to run the sequence replay, and says what is wrong when
// it cannot. Written because the alternative was pasting hundred-character
// digest references by hand.
//
//   node analysis/tools/replay_setup.mjs              # print the plan, pull nothing
//   node analysis/tools/replay_setup.mjs --count 10 --apply
//
// Prints the plan and exits. `--apply` prints the same plan and then pulls it.
// Every other flag only narrows what is in the plan.
//
// Exit codes: 0 ready, 1 something is wrong and named, 64 the call is wrong.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const STATE = `${ROOT}/.sequence-replay-state`;
let CORPUS = `${STATE}/sequence_corpus.json`;

const argv = process.argv.slice(2);
const apply = argv.includes("--apply");
const countAt = argv.indexOf("--count");
const count = countAt >= 0 ? Number.parseInt(argv[countAt + 1], 10) : 5;
const corpusAt = argv.indexOf("--corpus");
if (!Number.isInteger(count) || count < 1) {
  console.error("--count takes a positive integer");
  process.exit(64);
}

const fail = (msg, fix) => {
  console.error(`not ready: ${msg}`);
  if (fix) console.error(`  ${fix}`);
  process.exit(1);
};

// A pointer file is valid text, so nothing downstream complains: it just finds
// no trajectories and says nothing about why.
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

const runs = `${ROOT}/runs`;
if (!existsSync(runs)) fail("no runs/ directory, so there is nothing to replay");
const sample = firstTrajectory(runs);
if (!sample) fail("runs/ holds no .traj.json files");
if (readFileSync(sample, "utf8").startsWith("version https://git-lfs")) {
  fail(
    "the trajectories are Git LFS pointers, not content",
    "git -c core.hooksPath=.git/hooks lfs install --local && git lfs pull",
  );
}

const docker = spawnSync("docker", ["version", "--format", "{{.Server.Version}}"], { encoding: "utf8" });
if (docker.status !== 0) fail("docker is not reachable", (docker.stderr ?? "").trim().split("\n")[0]);
console.log(`docker ${docker.stdout.trim()}, trajectories are real content`);

if (corpusAt >= 0) CORPUS = argv[corpusAt + 1];
if (!existsSync(CORPUS)) {
  fail("no corpus yet", "node analysis/tools/sequence_replay.mjs extract");
}
const corpus = JSON.parse(readFileSync(CORPUS, "utf8"));

// Asked of docker per reference, not read from the corpus and not parsed out
// of its listing. The corpus records what was true when it was extracted, and
// the listing's format differs between image stores.
const cache = new Map();
const isLocal = (ref) => {
  if (!cache.has(ref)) {
    cache.set(ref, spawnSync("docker", ["image", "inspect", "--format", "{{.Id}}", ref], { stdio: "ignore" }).status === 0);
  }
  return cache.get(ref);
};

const byImage = new Map();
for (const e of corpus) {
  const rec = byImage.get(e.image) ?? { trajectories: 0, commands: 0, local: isLocal(e.image) };
  rec.trajectories++;
  rec.commands += e.commands.length;
  byImage.set(e.image, rec);
}
const missing = [...byImage].filter(([, r]) => !r.local).sort((a, b) => b[1].commands - a[1].commands);
const local = [...byImage].filter(([, r]) => r.local);
const localCommands = local.reduce((a, [, r]) => a + r.commands, 0);
const allCommands = [...byImage.values()].reduce((a, r) => a + r.commands, 0);

console.log(`corpus: ${corpus.length} trajectories over ${byImage.size} images`);
console.log(`already local: ${local.length} images, ${localCommands} of ${allCommands} commands replayable`);

const plan = missing.slice(0, count);
if (plan.length === 0) {
  console.log("nothing to pull; every image the corpus needs is present");
  process.exit(0);
}

const planCommands = plan.reduce((a, [, r]) => a + r.commands, 0);
const planTrajectories = plan.reduce((a, [, r]) => a + r.trajectories, 0);
console.log(`\nplan: pull ${plan.length} images, unlocking ${planTrajectories} trajectories and ${planCommands} commands`);
for (const [image, r] of plan) console.log(`  ${r.trajectories} traj, ${r.commands} cmds  ${image}`);

if (!apply) {
  console.log(`\nnothing pulled. re-run with --apply to pull these, or --count N to change how many.`);
  process.exit(0);
}

let pulled = 0;
for (const [image] of plan) {
  console.log(`\npulling ${image}`);
  const r = spawnSync("docker", ["pull", image], { stdio: "inherit" });
  if (r.status !== 0) {
    console.error(`failed on ${image}; stopping with ${pulled} pulled`);
    process.exit(1);
  }
  pulled++;
}
console.log(`\npulled ${pulled}. now re-run extract so the corpus sees them, then start the replay:`);
console.log("  node analysis/tools/sequence_replay.mjs extract");
console.log("  node analysis/tools/sequence_replay.mjs run --sample 1.0 --parallel 4");
