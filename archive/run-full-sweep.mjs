#!/usr/bin/env node
// FULL sweep: every main-spread model x every effort level, both frozen sets.
// 35 legs. This is a LARGE spend — max ran ~6x high on Opus 4.8 — so make the
// decision to run this deliberately, not casually.
//
// Every level is pinned explicitly, including `high`: high is the API default
// today, but pinning stops a shifted server-side default from silently
// confounding the comparison (same reasoning as the Fable 5 repeat run).
//
// Layout mirrors the main experiment: models in parallel (each has its own
// API rate-limit bucket), effort levels sequential within a model (one bucket —
// parallel levels would 429-storm each other). One timing proxy per leg on its
// own port; a leg that fails (e.g. a model rejecting the effort parameter)
// is reported by name and the model's remaining levels still run.
//
// Resumable: completed instances are skipped on rerun.
// Marking: eval-experiment.sh already globs runs/*/*/*/, which covers these.
//
// Output: runs/full-sweep/<model>-<effort>/<set>/
// Logs:   logs/full-sweep-<model>-<effort>.log
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

const EFFORTS = ['low', 'medium', 'high', 'xhigh', 'max'];

// Off 18899 (stale ANTHROPIC_BASE_URLs point there) and off the main
// experiment's 19100 block, so both can never collide with this sweep.
// Each model owns a block of 10 ports; each effort level takes one.
const BASE_PORT = 19200;

mkdirSync(join(repoRoot, 'logs'), { recursive: true });

// Run one model's five effort legs in sequence; return the legs that failed.
async function sweepModel(model, mi) {
  const short = model.split('/').pop().replace(/^claude-/, '');
  const failed = [];
  for (let ei = 0; ei < EFFORTS.length; ei++) {
    const effort = EFFORTS[ei];
    const name = `${short}-${effort}`;
    try {
      await runExperiment({
        model,
        out: `runs/full-sweep/${name}`,
        effort,
        port: BASE_PORT + mi * 10 + ei,
        log: `logs/full-sweep-${name}.log`,
        label: name,
        // Adaptive thinking for every model except Haiku 4.5, which rejects it
        // ("adaptive thinking is not supported on this model", proven 2026-06-10).
        ...(model.includes('haiku') ? { configs: ['swebench-local.yaml'] } : {}),
      });
    } catch (err) {
      failed.push({ name, err });
    }
  }
  return failed;
}

const perModel = [];
for (let mi = 0; mi < MODELS.length; mi++) {
  perModel.push(sweepModel(MODELS[mi], mi));
}

const failures = [];
for (const modelFailures of await Promise.all(perModel)) {
  failures.push(...modelFailures);
}
for (const f of failures) {
  console.error(`FAILED: ${f.name} — ${f.err.message} (see logs/full-sweep-${f.name}.log)`);
}
if (failures.length > 0) process.exit(1);
console.log('Full sweep complete. Mark it with ./eval-experiment.sh');
