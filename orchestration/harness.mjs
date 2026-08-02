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
// Stop a child and WAIT for it to be gone.
//
// SIGINT, not SIGTERM: python's default SIGTERM handler terminates the process
// outright — no stack unwind, no finally blocks, no atexit — so a harness that
// removes its containers in a finally never gets to. SIGINT raises
// KeyboardInterrupt, which unwinds.
//
// And waiting matters: kill() only delivers the signal and returns, so exiting
// straight afterwards gives the child no time to tear anything down. SIGKILL
// only after the grace period, when it has had its chance.
export const stopChild = (child, graceMs = 15_000) => new Promise((resolve) => {
  if (!child || child.exitCode !== null || child.signalCode !== null) return resolve();
  const done = () => { clearTimeout(timer); resolve(); };
  const timer = setTimeout(() => { child.kill('SIGKILL'); done(); }, graceMs);
  child.once('exit', done);
  child.kill('SIGINT');
});

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
  const hardStop = async (sig, code = 130) => {
    if (firing) return;
    firing = true;
    console.error(`\n[run] ${sig} — hard stop, tearing down...`);
    try {
      await Promise.allSettled(cleanups.map((fn) => fn()));
    } finally {
      process.exit(code);
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
  // A crash is not a signal, so none of the above fires for one — Node runs
  // its default handler and exits, the cleanups never run, and every spawned
  // child is reparented and left alive. That is worse than a Ctrl-C: the
  // children outlive the proxy they were talking to, so with a long retry
  // budget they sit hammering a closed port for days. It happened: an
  // ERR_HTTP_HEADERS_SENT in the proxy orphaned two runs and twelve
  // containers, and only the containers' CPU gave it away.
  //
  // The exception is still fatal — continuing after an unknown fault means
  // running in an undefined state — but the children go down with it.
  for (const event of ['uncaughtException', 'unhandledRejection']) {
    process.on(event, (err) => {
      console.error(`\n[run] ${event}:`, err?.stack ?? err);
      hardStop(event, 1); // 130 means interrupted; a crash is not that
    });
  }
};
