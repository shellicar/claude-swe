// Shared run-orchestration helpers, kept separate from any single run's config
// so every run script composes the same building blocks: build the instance
// filter, spawn-and-await a child, wire a clean shutdown.
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
export const repoRoot = join(here, '..');

// Build the anchored alternation mini-extra expects from instances-<set>.txt,
// e.g. ^(id-a|id-b|id-c)$ — the frozen set, identical across runs.
export const instanceFilter = (set) => {
  const ids = readFileSync(join(repoRoot, `instances-${set}.txt`), 'utf8')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
  if (ids.length === 0) throw new Error(`instances-${set}.txt is empty`);
  return `^(${ids.join('|')})$`;
};

// Spawn a child with inherited stdio, resolve on exit 0, reject otherwise.
// onChild hands the live process back so the caller can kill it on shutdown.
// Args are passed as an array (no shell), so the filter regex needs no escaping.
export const spawnAwait = (program, args, { env, onChild } = {}) =>
  new Promise((resolve, reject) => {
    const child = spawn(program, args, { cwd: repoRoot, env: { ...process.env, ...env }, stdio: 'inherit' });
    onChild?.(child);
    child.on('error', reject);
    child.on('exit', (code, signal) =>
      code === 0 ? resolve() : reject(new Error(`${program} exited (code ${code}, signal ${signal})`)));
  });

// Wire SIGINT/SIGTERM to a cleanup fn, then exit 130 — matches the sh
// convention and guarantees the proxy and in-flight run come down together,
// with no orphan left spending.
export const onShutdown = (cleanup) => {
  let firing = false;
  const handle = async (sig) => {
    if (firing) return;
    firing = true;
    console.error(`\n[run] ${sig} received — tearing down...`);
    try {
      await cleanup();
    } finally {
      process.exit(130);
    }
  };
  process.on('SIGINT', () => handle('SIGINT'));
  process.on('SIGTERM', () => handle('SIGTERM'));
};
