// Run one SWE-bench experiment leg end to end: bring up the timing proxy
// in-process, run each set through mini-extra pointed at it, tear the proxy down
// on completion or Ctrl-C. Timing lands in the run's own dir, so there is no
// shared log and no copy step.
//
// This is the entire orchestration. A run script is just config: it calls
// runExperiment() with parameters and nothing else.
import { mkdirSync, openSync, closeSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { startTimingProxy } from '../mitm/timing-mitm.mjs';
import { spawnAwait, instanceFilter, onShutdown, isDraining, repoRoot } from './harness.mjs';

// Anchored alternation from explicit ids — the caller's declaration is the
// single source of truth. (instanceFilter's filename convention remains only
// for the archived scripts; it once routed multi/cpp to Multilingual's list.)
const idsFilter = (ids) => {
  if (!ids?.length) throw new Error('empty instance id list');
  return `^(${ids.join('|')})$`;
};

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
 * @param {number}   [p.port]   proxy port (default 18899); parallel legs must each use their own
 * @param {string}   [p.log]    file (repo-relative) for the leg's mini-extra output; default inherits the console
 * @param {string}   [p.label]  tag for console lines (e.g. 'sonnet-5'), so parallel legs' output is attributable
 * @param {Object}   [p.selectionIds] set name → array of instance ids; when absent the instances-<set>.txt convention applies (archived scripts only)
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
  port,
  log,
  label,
  selectionIds,
}) {
  const tag = label ?? model;
  // The proxy appends here on first request, so the dir must exist first.
  mkdirSync(join(repoRoot, out), { recursive: true });

  // Which upstream the proxy forwards to, and which variable tells litellm
  // where the API lives, both follow from the model's provider prefix. The
  // proxy stays provider-neutral; only the host and the variable's name differ.
  const provider = model.includes('/') ? model.split('/')[0] : 'anthropic';
  const PROVIDERS = {
    anthropic: { host: 'api.anthropic.com', baseUrlVar: 'ANTHROPIC_BASE_URL' },
    moonshot: { host: 'api.moonshot.ai', baseUrlVar: 'MOONSHOT_API_BASE' },
  };
  const upstream = PROVIDERS[provider];
  if (!upstream) {
    throw new Error(
      `no proxy upstream declared for provider '${provider}' (model ${model}) `
      + `— add it to PROVIDERS in orchestration/experiment.mjs`,
    );
  }

  const proxy = await startTimingProxy({
    port, timingLog: join(repoRoot, out, 'api-timing.jsonl'), label, target: upstream.host,
  });
  console.log(`[${tag}] proxy up at ${proxy.baseUrl}, timing -> ${out}/api-timing.jsonl`);

  // Route the run's API traffic through the proxy. Retry for ~an hour
  // (60 attempts, 60s backoff cap) instead of the scaffold's ~8-minute
  // default, so instances sleep through API instability rather than dying
  // as InternalServerError — the container idles alive and waiting is free.
  const rig = JSON.parse(readFileSync(join(repoRoot, 'rig.json'), 'utf8'));
  const retries = ['xhigh', 'max'].includes(effort)
    ? rig.retryAttemptsHighEffort
    : rig.retryAttempts;
  const env = {
    [upstream.baseUrlVar]: proxy.baseUrl
      + (upstream.baseUrlVar === 'MOONSHOT_API_BASE' ? '/v1' : ''),
    MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT: String(retries),
  };

  // Track the live leg so Ctrl-C kills it and the proxy together.
  let current = null;
  onShutdown(async () => {
    current?.kill('SIGTERM');
    await proxy.stop();
  });

  const cfgArgs = configs.flatMap((c) => ['-c', c]);
  if (effort) cfgArgs.push('-c', `model.model_kwargs.output_config.effort=${effort}`);

  // Per-leg log file so parallel legs don't interleave on one console.
  const logFd = log ? openSync(join(repoRoot, log), 'a') : null;
  const stdio = logFd === null ? 'inherit' : ['ignore', logFd, logFd];

  try {
    for (const set of sets) {
      // Drain (first Ctrl-C): the running set finishes its in-flight instances
      // via mini's own SIGINT handling; starting the NEXT set is the one piece
      // of new work mini can't see, so it is gated here.
      if (isDraining()) {
        console.log(`[${tag}] draining — not starting ${set}`);
        break;
      }
      console.log(`[${tag}] === ${set} ===`);
      await spawnAwait(
        '.venv/bin/mini-extra',
        [
          'swebench',
          '--subset', subset,
          '--split', split,
          '--filter', selectionIds?.[set] ? idsFilter(selectionIds[set]) : instanceFilter(set),
          '-m', model,
          ...cfgArgs,
          '-o', `${out}/${set}`,
          '-w', String(workers),
        ],
        { env, stdio, onChild: (child) => { current = child; } },
      );
    }
    console.log(`[${tag}] leg complete`);
  } finally {
    current = null;
    if (logFd !== null) closeSync(logFd);
    await proxy.stop();
  }
}
