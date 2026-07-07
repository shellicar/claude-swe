// Run one SWE-bench experiment leg end to end: bring up the timing proxy
// in-process, run each set through mini-extra pointed at it, tear the proxy down
// on completion or Ctrl-C. Timing lands in the run's own dir, so there is no
// shared log and no copy step.
//
// This is the entire orchestration. A run script is just config: it calls
// runExperiment() with parameters and nothing else.
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { startTimingProxy } from '../mitm/timing-mitm.mjs';
import { spawnAwait, instanceFilter, onShutdown, repoRoot } from './harness.mjs';

/**
 * @param {object} p
 * @param {string}   p.model    e.g. 'anthropic/claude-fable-5'
 * @param {string}   p.out      output dir, e.g. 'runs/main/fable-5-high-2026-07-02'
 * @param {string[]} [p.sets]   defaults to ['standard', 'hard']
 * @param {number}   [p.workers] parallel workers per set (default 3)
 * @param {string}   [p.effort] pins model.model_kwargs.output_config.effort when set
 * @param {string[]} [p.configs] -c yaml overlays (default swebench-local + adaptive thinking)
 * @param {string}   [p.subset] default 'verified'
 * @param {string}   [p.split]  default 'test'
 */
export async function runExperiment({
  model,
  out,
  sets = ['standard', 'hard'],
  workers = 3,
  effort,
  configs = ['swebench-local.yaml', 'thinking-adaptive.yaml'],
  subset = 'verified',
  split = 'test',
}) {
  // The proxy appends here on first request, so the dir must exist first.
  mkdirSync(join(repoRoot, out), { recursive: true });

  const proxy = await startTimingProxy({ timingLog: join(repoRoot, out, 'api-timing.jsonl') });
  console.log(`[run] proxy up at ${proxy.baseUrl}, timing -> ${out}/api-timing.jsonl`);

  // Route the run's API traffic through the proxy.
  const env = { ANTHROPIC_BASE_URL: proxy.baseUrl };

  // Track the live leg so Ctrl-C kills it and the proxy together.
  let current = null;
  onShutdown(async () => {
    current?.kill('SIGTERM');
    await proxy.stop();
  });

  const cfgArgs = configs.flatMap((c) => ['-c', c]);
  if (effort) cfgArgs.push('-c', `model.model_kwargs.output_config.effort=${effort}`);

  try {
    for (const set of sets) {
      console.log(`[run] === ${set} ===`);
      await spawnAwait(
        '.venv/bin/mini-extra',
        [
          'swebench',
          '--subset', subset,
          '--split', split,
          '--filter', instanceFilter(set),
          '-m', model,
          ...cfgArgs,
          '-o', `${out}/${set}`,
          '-w', String(workers),
        ],
        { env, onChild: (child) => { current = child; } },
      );
    }
    console.log('[run] complete. Mark it with ./eval-experiment.sh');
  } finally {
    current = null;
    await proxy.stop();
  }
}
