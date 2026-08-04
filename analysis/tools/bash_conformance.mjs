#!/usr/bin/env node
// Runs GNU Bash's own test suite against bash-walker and reports where they
// differ.
//
//   node analysis/tools/bash_conformance.mjs [name...]
//
// Bash itself is the oracle, run here, rather than the shipped .right files:
// those were captured with `> file 2>&1`, so they have bash's stdio buffering
// baked in (stdout block-buffered to a file, stderr not), which no
// reimplementation can reproduce and which is not semantics. Running both
// shells with the streams kept apart compares what each decided, and leaves
// cross-stream ordering untested, deliberately.
//
// Exit 0 when every test matched, 1 otherwise, 64 on a bad call.

import { readdirSync, readFileSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = new URL("../..", import.meta.url).pathname.replace(/\/$/, "");
const BASH = `${process.env.HOME}/repos/gnu/bash/bash`;
const WALKER = `${ROOT}/rust/target/debug/bash-walker`;
const TESTS = `${process.env.HOME}/repos/gnu/bash/tests`;
const TIMEOUT = 20_000;

const only = process.argv.slice(2).filter((a) => !a.startsWith("-"));
const verbose = process.argv.includes("--verbose");

const names = readdirSync(TESTS)
  .filter((f) => f.endsWith(".tests"))
  .map((f) => f.replace(/\.tests$/, ""))
  .filter((n) => only.length === 0 || only.includes(n))
  .sort();

if (names.length === 0) {
  console.error("no matching tests");
  process.exit(64);
}

// Each run gets its own scratch directory, because the tests write files and
// a shared one lets an earlier test decide a later one's result.
function run(shell, name) {
  const tmp = mkdtempSync(join(tmpdir(), "bashconf-"));
  const r = spawnSync(shell, [`./${name}.tests`], {
    cwd: TESTS,
    encoding: "utf8",
    timeout: TIMEOUT,
    maxBuffer: 64 * 1024 * 1024,
    // `.` on PATH is how run-all finds bash's own helpers, recho, zecho and
    // printenv. Without them fourteen tests fail on "recho: command not
    // found", which says nothing about either shell. Build them with:
    //   cc -o tests/recho support/recho.c   (same for zecho, printenv)
    env: {
      ...process.env,
      PATH: `.:${process.env.PATH}`,
      TMPDIR: tmp,
      THIS_SH: shell,
      BUILD_DIR: `${process.env.HOME}/repos/gnu/bash`,
    },
  });
  return { out: r.stdout ?? "", err: r.stderr ?? "", status: r.status, timedOut: r.error?.code === "ETIMEDOUT" };
}

// Why a test failed, judged from the walker's own diagnostics rather than
// guessed. "unimplemented" is what the walker says it does not do; anything
// else is a divergence and needs reading.
function classify(w) {
  const text = w.err + w.out;
  if (w.timedOut) return "timeout";
  if (/not yet supported by this parser|is not supported by bash-walker|unsupported/i.test(text)) return "unimplemented";
  if (/bash-walker: syntax error/.test(text)) return "parse error";
  return "divergence";
}

const results = [];
for (const name of names) {
  const b = run(BASH, name);
  const w = run(WALKER, name);
  const outSame = b.out === w.out;
  const errSame = b.err === w.err;
  const statusSame = b.status === w.status;
  const verdict = outSame && errSame && statusSame ? "match" : classify(w);
  results.push({ name, verdict, outSame, errSame, statusSame, b, w });
  console.log(`${verdict.padEnd(14)} ${name}${verdict === "match" ? "" : `  (stdout ${outSame ? "=" : "≠"}, stderr ${errSame ? "=" : "≠"}, status ${b.status} vs ${w.status})`}`);
}

const tally = new Map();
for (const r of results) tally.set(r.verdict, (tally.get(r.verdict) ?? 0) + 1);
console.log(`\n${results.length} tests`);
for (const [k, v] of [...tally].sort((a, b) => b[1] - a[1])) console.log(`  ${String(v).padStart(3)}  ${k}`);

writeFileSync(`${ROOT}/.bash-conformance.json`, JSON.stringify(
  results.map((r) => ({
    name: r.name,
    verdict: r.verdict,
    outSame: r.outSame,
    errSame: r.errSame,
    bashStatus: r.b.status,
    walkerStatus: r.w.status,
    walkerErrHead: r.w.err.split("\n").slice(0, 3),
    bashOutHead: r.b.out.split("\n").slice(0, 3),
    walkerOutHead: r.w.out.split("\n").slice(0, 3),
  })),
  null,
  1,
));

if (verbose) {
  for (const r of results.filter((x) => x.verdict !== "match")) {
    console.log(`\n=== ${r.name} (${r.verdict})`);
    console.log(`  walker stderr: ${JSON.stringify(r.w.err.slice(0, 300))}`);
  }
}

process.exit(results.every((r) => r.verdict === "match") ? 0 : 1);
