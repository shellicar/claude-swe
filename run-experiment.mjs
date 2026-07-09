#!/usr/bin/env node
// THE experiment: 7 models x 2 sets (standard, hard), one pass, one invocation.
// Every leg runs through its own timing proxy (one per model, distinct ports —
// a shared proxy scrambles per-instance attribution, learned 2026-06-10), so
// api-timing.jsonl lands in each model's run dir alongside the trajectories.
//
// Completed legs skip finished instances on rerun, so adding a model only runs
// the new one. Interrupt-safe: Ctrl-C tears down every child and proxy together
// (onShutdown in the harness), and a rerun resumes where it left off.
//
// Output: runs/main/<model>/<set>/   Console logs: logs/<model>.log
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { runExperiment } from './orchestration/experiment.mjs';
import { repoRoot } from './orchestration/harness.mjs';

const MODELS = [
  'anthropic/claude-opus-4-6',
  'anthropic/claude-opus-4-7',
  'anthropic/claude-opus-4-8',
  'anthropic/claude-fable-5',
  'anthropic/claude-haiku-4-5',
  'anthropic/claude-sonnet-4-6',
  'anthropic/claude-sonnet-5',
];

// Deliberately NOT 18899 (the proxy's standalone default, and what a stale
// ANTHROPIC_BASE_URL in .env points at). A request aimed at the old port gets
// connection-refused — a loud failure — instead of silently going through the
// wrong leg's proxy and contaminating its timing log (seen 2026-07-07).
const BASE_PORT = 19100;

mkdirSync(join(repoRoot, 'logs'), { recursive: true });

const legs = MODELS.map((model, i) => {
  const short = model.split('/').pop().replace(/^claude-/, '');
  return runExperiment({
    model,
    out: `runs/main/${short}`,
    port: BASE_PORT + i,
    log: `logs/${short}.log`,
    label: short,
    // Adaptive thinking for every model except Haiku 4.5, which rejects it
    // ("adaptive thinking is not supported on this model", proven 2026-06-10).
    ...(model.includes('haiku') ? { configs: ['swebench-local.yaml'] } : {}),
  }).then(
    () => ({ short, ok: true }),
    (err) => ({ short, ok: false, err }),
  );
});

const results = await Promise.all(legs);
const failed = results.filter((r) => !r.ok);
for (const f of failed) {
  console.error(`FAILED: ${f.short} — ${f.err.message} (see logs/${f.short}.log)`);
}
if (failed.length > 0) process.exit(1);
console.log('Experiment complete. Mark it with ./eval-experiment.sh');
