#!/usr/bin/env node
// SWE-bench Pro pilot: Opus 4.8 vs Sonnet 5 on the frozen TypeScript set
// (instances-pro.txt: 10 tutao/tutanota instances drawn by draw-instances-pro.py).
//
// Declared inputs: datasets/swe-bench-pro.jsonl (snapshot; mini loads the file,
// not HF), instances-pro.txt (frozen selection), image-manifest.txt (digests —
// run `node eval-experiment.mjs ensure` first so the images are verified local).
//
// Marking is NOT ours: Pro verdicts need Scale's harness (separate work).
// This run banks patches, trajectories, and wire captures.
//
// Output: runs/pro/<model>/pro/   Console logs: logs/pro-<model>.log
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { runExperiment } from './orchestration/experiment.mjs';
import { repoRoot } from './orchestration/harness.mjs';

const MODELS = [
  'anthropic/claude-opus-4-8',
  'anthropic/claude-sonnet-5',
  'anthropic/claude-fable-5',
];

// Own block, clear of the main experiment's 19100+ range.
const BASE_PORT = 19120;

mkdirSync(join(repoRoot, 'logs'), { recursive: true });

const legs = [];
for (let i = 0; i < MODELS.length; i++) {
  const model = MODELS[i];
  const short = model.split('/').pop().replace(/^claude-/, '');
  legs.push(
    runExperiment({
      model,
      out: `runs/pro/${short}`,
      sets: ['pro'],
      workers: 2,
      subset: 'datasets/swe-bench-pro.jsonl',
      configs: ['swebench-local.yaml', 'swebench-pro.yaml', 'thinking-adaptive.yaml'],
      port: BASE_PORT + i,
      log: `logs/pro-${short}.log`,
      label: `pro-${short}`,
    }).then(
      () => ({ short, ok: true }),
      (err) => ({ short, ok: false, err }),
    ),
  );
}

const results = await Promise.all(legs);
const failed = results.filter((r) => !r.ok);
for (const f of failed) {
  console.error(`FAILED: pro-${f.short} — ${f.err.message} (see logs/pro-${f.short}.log)`);
}
if (failed.length > 0) process.exit(1);
console.log('Pro pilot complete. Patches under runs/pro/; marking needs the Pro harness.');
