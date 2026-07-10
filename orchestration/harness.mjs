// Shared run-orchestration helpers, kept separate from any single run's config
// so every run script composes the same building blocks: build the instance
// filter, spawn-and-await a child, wire a clean shutdown.
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
export const repoRoot = join(here, '..');

// Build the anchored alternation mini-extra expects from the selection file,
// e.g. ^(id-a|id-b|id-c)$ — the frozen set, identical across runs.
// The file must come from the dataset declaration when sets share a name
// across datasets: the instances-<set>.txt naming convention once routed
// multi/cpp to Multilingual's cpp list (8 stray instances ran, 2026-07-11).
export const instanceFilter = (set, file) => {
  const path = file ?? `instances-${set}.txt`;
  const ids = readFileSync(join(repoRoot, path), 'utf8')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
  if (ids.length === 0) throw new Error(`${path} is empty`);
  return `^(${ids.join('|')})$`;
};

// Spawn a child, resolve on exit 0, reject otherwise. stdio defaults to
// inherit; parallel legs pass their own fds so their output lands in per-leg
// log files instead of interleaving on one console.
// onChild hands the live process back so the caller can kill it on shutdown.
// Args are passed as an array (no shell), so the filter regex needs no escaping.
export const spawnAwait = (program, args, { env, onChild, stdio = 'inherit', cwd = repoRoot } = {}) =>
  new Promise((resolve, reject) => {
    const child = spawn(program, args, { cwd, env: { ...process.env, ...env }, stdio });
    onChild?.(child);
    child.on('error', reject);
    child.on('exit', (code, signal) =>
      code === 0 ? resolve() : reject(new Error(`${program} exited (code ${code}, signal ${signal})`)));
  });

// Shutdown semantics:
//   1st Ctrl-C  — drain. The terminal delivers SIGINT to the whole process
//                 group, so the mini children receive it directly and do their
//                 own graceful drain (finish in-flight instances, start no new
//                 ones). The orchestrator only flags drain mode — so legs stop
//                 starting further sets — and keeps the proxies up for the
//                 in-flight work.
//   2nd Ctrl-C  — hard stop: kill children, stop proxies, exit 130.
//   SIGTERM     — hard stop immediately (non-interactive kills don't drain).
//
// A registry, not one handler per caller: with parallel legs each registering
// its own cleanup, per-caller handlers would race — the first to finish would
// process.exit() while other legs' children were still alive (the orphaned-
// spend trap, learned 2026-06-10). One handler awaits every cleanup, then exits.
const cleanups = [];
let handlerInstalled = false;
let draining = false;
export const isDraining = () => draining;
export const onShutdown = (cleanup) => {
  cleanups.push(cleanup);
  if (handlerInstalled) return;
  handlerInstalled = true;
  let firing = false;
  const hardStop = async (sig) => {
    if (firing) return;
    firing = true;
    console.error(`\n[run] ${sig} — hard stop, tearing down...`);
    try {
      await Promise.allSettled(cleanups.map((fn) => fn()));
    } finally {
      process.exit(130);
    }
  };
  process.on('SIGINT', () => {
    if (!draining) {
      draining = true;
      console.error('\n[run] Ctrl-C — draining: in-flight instances finish, nothing new starts. Ctrl-C again to stop now.');
      return; // children got their own SIGINT from the tty and drain themselves
    }
    hardStop('SIGINT (second)');
  });
  process.on('SIGTERM', () => hardStop('SIGTERM'));
};
