#!/usr/bin/env node
// Fable 5 repeat run (2026-07-02): "has Fable 5 changed since the first run?"
//
// Same experiment as the main Fable 5 leg — same frozen instance sets, same
// swebench-local.yaml + thinking-adaptive.yaml, 3 workers — run again under a
// new name so it sits beside the original (runs/main/fable-5/) instead of being
// skipped.
//
// One deliberate difference from the first run: effort is pinned to `high`
// EXPLICITLY. `high` is the API default (identical to omitting it), so behaviour
// matches the first run today — but pinning stops a shifted server-side default
// from silently confounding a comparison whose whole point is detecting a model
// change. The first run didn't pin it because it wasn't trying to detect one.
//
// All orchestration lives in runExperiment(); this file is only the parameters.
import { runExperiment } from './orchestration/experiment.mjs';

runExperiment({
  model: 'anthropic/claude-fable-5',
  out: 'runs/main/fable-5-high-2026-07-02',
  effort: 'high',
}).catch((err) => {
  console.error(`[run] failed: ${err.message}`);
  process.exit(1);
});
