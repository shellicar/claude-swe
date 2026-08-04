#!/usr/bin/env node
// Sets a machine up and starts the replay. One command, everything.
//
//   node analysis/tools/replay_setup.mjs [--parallel N] [--from user@host]
//
// Builds the corpus, fetches every image the corpus needs and does not have,
// rebuilds the corpus so it sees them, and starts the run. Safe to re-run: it
// fetches only what is missing and the replay resumes rather than restarting.
//
// `--from` streams images off another machine's docker over ssh instead of
// pulling from the registry, for when the LAN is faster than the internet.
// Nothing is written to disk in between. It moves more bytes than a registry
// pull, because `docker save` streams layers uncompressed.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawn, spawnSync } from "node:child_process";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const SELF = `${ROOT}/analysis/tools/sequence_replay.mjs`;
const CORPUS = `${ROOT}/.sequence-replay-state/sequence_corpus.json`;
const RIG = JSON.parse(readFileSync(`${ROOT}/rig.json`, "utf8"));

const argv = process.argv.slice(2);
const at = argv.indexOf("--parallel");
const parallel = at >= 0 ? argv[at + 1] : String(RIG.replayParallel);
const fromAt = argv.indexOf("--from");
const from = fromAt >= 0 ? argv[fromAt + 1] : null;

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
  // `docker pull` takes one reference and has no batch form, so several run at
  // once. Beyond a handful the daemon's own max-concurrent-downloads (3 by
  // default) is the real limit; raise it in daemon.json to go faster.
  const CONCURRENCY = 4;
  const queue = missing.map(([image]) => image);

  if (from) {
    // A non-interactive ssh gets a minimal PATH, so `docker` is not on it.
    // Ask a login shell where it lives once, then use that path directly.
    const which = spawnSync("ssh", [from, "sh", "-lc", "command -v docker"], { encoding: "utf8" });
    // A login shell runs the profile, which can print escape sequences before
    // the answer, so take the last line that actually looks like a path.
    const remoteDocker = (which.stdout ?? "")
      // eslint-disable-next-line no-control-regex
      .replace(/\u001b[^\u0007]*(?:\u0007|\u001b\\)/g, "")
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.startsWith("/"))
      .pop();
    if (which.status !== 0 || !remoteDocker) {
      die(`cannot find docker on ${from}`, (which.stderr ?? "").trim().split("\n")[0] || "is Remote Login enabled?");
    }
    console.log(`\nstreaming ${queue.length} images from ${from} (${remoteDocker})`);

    // One ssh per batch: a failure costs that batch, not the whole transfer,
    // and each batch reports rather than the stream going quiet for hours.
    const BATCH = 5;
    for (let i = 0; i < queue.length; i += BATCH) {
      const batch = queue.slice(i, i + BATCH);
      const status = await new Promise((res) => {
        let sshCode = 0;
        const ssh = spawn("ssh", [from, remoteDocker, "save", ...batch], { stdio: ["ignore", "pipe", "inherit"] });
        const load = spawn("docker", ["load"], { stdio: ["pipe", "inherit", "inherit"] });
        ssh.stdout.pipe(load.stdin);
        ssh.on("exit", (code) => (sshCode = code ?? 1));
        load.on("exit", (code) => res(sshCode !== 0 ? sshCode : (code ?? 1)));
      });
      console.log(`[${Math.min(i + BATCH, queue.length)}/${queue.length}] ${status === 0 ? "ok" : "FAILED"}`);
    }
    corpus = extract();
    if (corpus.filter((e) => e.imageLocal).length === 0) die("nothing arrived over ssh");
  } else {

  console.log(`\npulling ${missing.length} images, ${CONCURRENCY} at a time`);
  let done = 0;
  let failed = 0;
  const worker = async () => {
    for (;;) {
      const image = queue.shift();
      if (!image) return;
      const status = await new Promise((res) => {
        const c = spawn("docker", ["pull", image], { stdio: ["ignore", "ignore", "pipe"] });
        let err = "";
        c.stderr.on("data", (d) => (err += d));
        c.on("exit", (code) => {
          if (code !== 0) console.error(`  failed ${image}: ${err.trim().split("\n").pop()}`);
          res(code);
        });
      });
      done++;
      if (status !== 0) failed++;
      console.log(`[${done}/${missing.length}] ${status === 0 ? "ok" : "FAILED"} ${image}`);
    }
  };
  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, queue.length) }, worker));
  if (failed > 0) console.error(`\n${failed} pulls failed. Replaying what is present.`);
  corpus = extract();
  }
}

const replayable = corpus.filter((e) => e.imageLocal).length;
if (replayable === 0) die("no image the corpus needs is present, so there is nothing to replay");

console.log(`\nstarting the replay: ${replayable} of ${corpus.length} trajectories, ${parallel} workers`);
console.log(`change workers while it runs: echo N > ${ROOT}/.sequence-replay-state/workers`);
const run = spawnSync(process.execPath, [SELF, "run", "--sample", "1.0", "--parallel", parallel, "--resume"], {
  stdio: "inherit",
});
process.exit(run.status ?? 1);
