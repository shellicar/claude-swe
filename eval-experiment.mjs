#!/usr/bin/env node
// Evaluation as declared operations. Authority flows repo → machine: every
// operation is a function of inputs committed in this repo; the machine either
// conforms or the operation refuses. (Background: CLAUDE.md "SWE-bench —
// underlying design issues"; data flow: docs/diagrams/eval-pipeline.d2.)
//
//   resolve  frozen instance lists + naming rule → REGISTRY → image-manifest.txt
//            The one deliberate observation→specification promotion, done per
//            epoch, reviewed, committed. Queries Docker Hub for what each
//            instance's tag resolves to; never consults the local daemon.
//   ensure   image-manifest.txt → local Docker conforms: pull-by-digest what is
//            missing, verify what is present, refuse loudly on any mismatch.
//   mark     preds.json per leg + dataset snapshot + pinned harness → verdicts.
//            Runs with cwd=evals/ so ALL harness output (report JSONs, instance
//            logs) lands there instead of littering the repo root.
//   audit    verdicts vs frozen lists → completeness: every instance answered,
//            every patch marked, nothing silently skipped.
//
// Usage:
//   node eval-experiment.mjs resolve            # regenerate the declaration
//   node eval-experiment.mjs                    # ensure + mark + audit
//   node eval-experiment.mjs audit              # any subset, in given order
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnAwait, onShutdown, repoRoot } from './orchestration/harness.mjs';

const MANIFEST = join(repoRoot, 'image-manifest.txt');
const DATASET = join(repoRoot, 'datasets', 'swe-bench-verified.jsonl');
const EVALS_DIR = join(repoRoot, 'evals');

// The naming rule: dataset instance_id → published image repository.
// Docker forbids '__', so swebench substitutes the magic token '_1776_'.
const imageRepo = (iid) =>
  `docker.io/swebench/sweb.eval.x86_64.${iid.replace(/__/g, '_1776_')}`.toLowerCase();

const frozenInstanceIds = () => {
  const ids = [];
  for (const set of ['standard', 'hard']) {
    for (const line of readFileSync(join(repoRoot, `instances-${set}.txt`), 'utf8').split('\n')) {
      if (line.trim()) ids.push(line.trim());
    }
  }
  return ids;
};

const readManifest = () => {
  const entries = [];
  for (const line of readFileSync(MANIFEST, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const [iid, ref] = line.split(/\s+/);
    entries.push({ iid, ref });
  }
  return entries;
};

// ---- resolve ---------------------------------------------------------------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Hub's web API serves tag→digest under a much looser rate limit than the
// registry endpoint (whose anonymous allowance is ~100 manifest reads / 6 h —
// learned by burning it, 2026-07-09). Still the publisher, never the daemon.
async function hubDigest(repo) {
  const name = repo.replace('docker.io/', '');
  const url = `https://hub.docker.com/v2/repositories/${name}/tags/latest`;
  for (let attempt = 1; ; attempt++) {
    const resp = await fetch(url);
    if (resp.status === 429 && attempt < 8) {
      console.log(`[resolve] 429 from hub API — backing off 60s (attempt ${attempt}/8)`);
      await sleep(60_000);
      continue;
    }
    if (!resp.ok) throw new Error(`hub API ${resp.status} for ${name}`);
    const body = await resp.json();
    if (!body.digest) throw new Error(`hub API returned no digest for ${name}`);
    return body.digest;
  }
}

async function opResolve() {
  const ids = frozenInstanceIds();
  // Resume: keep already-declared entries so a partial run is never lost.
  const resolved = new Map();
  if (existsSync(MANIFEST)) {
    for (const { iid, ref } of readManifest()) resolved.set(iid, ref);
  }
  const todo = ids.filter((iid) => !resolved.has(iid));
  console.log(`[resolve] ${ids.length} instances — ${resolved.size} already declared, ${todo.length} to resolve`);
  const writeOut = () =>
    writeFileSync(MANIFEST, ids.filter((i) => resolved.has(i)).map((i) => `${i} ${resolved.get(i)}`).join('\n') + '\n');
  for (let i = 0; i < todo.length; i++) {
    const repo = imageRepo(todo[i]);
    const digest = await hubDigest(repo);
    resolved.set(todo[i], `${repo}@${digest}`);
    writeOut(); // incremental — progress survives any failure
    if ((i + 1) % 20 === 0) console.log(`[resolve] ${i + 1}/${todo.length}`);
  }
  console.log(`[resolve] ${resolved.size}/${ids.length} declarations in ${MANIFEST}`);
  console.log('[resolve] review and commit it — committing is the act that makes it the specification.');
}

// ---- ensure ----------------------------------------------------------------
function localDigests(repo) {
  // RepoDigests of the locally-present image for this repository, if any.
  try {
    const out = execFileSync('docker', ['image', 'inspect', `${repo}:latest`, '--format', '{{json .RepoDigests}}'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    return JSON.parse(out.trim());
  } catch {
    return [];
  }
}

// Docker reports RepoDigests without the default-registry prefix
// ('swebench/…', not 'docker.io/swebench/…'); normalise before comparing.
const canonical = (ref) => ref.replace(/^docker\.io\//, '');

async function opEnsure() {
  const entries = readManifest();
  console.log(`[ensure] verifying ${entries.length} images against ${MANIFEST}...`);
  const missing = [];
  const mismatched = [];
  for (const { iid, ref } of entries) {
    const repo = ref.split('@')[0];
    const digests = localDigests(repo).map(canonical);
    if (digests.includes(canonical(ref))) continue;
    if (digests.length > 0) { mismatched.push({ iid, ref, have: digests }); continue; }
    missing.push({ iid, ref });
  }
  for (const { iid, have, ref } of mismatched) {
    console.error(`[ensure] MISMATCH ${iid}: declared ${ref}, local has ${have.join(', ')}`);
  }
  if (mismatched.length > 0) {
    // A local image that contradicts the declaration is never auto-fixed:
    // deleting/replacing images is a decision, not a preflight side effect.
    throw new Error(`${mismatched.length} local images contradict the manifest — resolve manually`);
  }
  for (let i = 0; i < missing.length; i++) {
    const { iid, ref } = missing[i];
    console.log(`[ensure] pulling ${i + 1}/${missing.length} ${iid} by digest...`);
    await spawnAwait('docker', ['pull', '--platform', 'linux/amd64', ref]);
  }
  console.log(`[ensure] ok — ${entries.length - missing.length} present, ${missing.length} pulled, 0 mismatches`);
}

// ---- mark ------------------------------------------------------------------
function findLegs() {
  // runs/<experiment>/<leg>/<set>/preds.json
  const legs = [];
  const runsDir = join(repoRoot, 'runs');
  for (const experiment of readdirSync(runsDir)) {
    const expDir = join(runsDir, experiment);
    for (const leg of readdirSync(expDir)) {
      const legDir = join(expDir, leg);
      for (const set of ['standard', 'hard']) {
        const preds = join(legDir, set, 'preds.json');
        if (existsSync(preds)) {
          legs.push({ runId: `runs_${experiment}_${leg}_${set}`, preds, set });
        }
      }
    }
  }
  return legs;
}

async function opMark() {
  mkdirSync(EVALS_DIR, { recursive: true });
  const legs = findLegs();
  console.log(`[mark] ${legs.length} legs with predictions`);
  let current = null;
  onShutdown(async () => current?.kill('SIGTERM'));
  for (const { runId, preds } of legs) {
    console.log(`[mark] === ${runId} ===`);
    await spawnAwait(
      join(repoRoot, '.venv/bin/python'),
      [
        '-m', 'swebench.harness.run_evaluation',
        '--dataset_name', DATASET,
        '--predictions_path', preds,
        '--max_workers', '3',
        '--namespace', 'swebench',
        '--run_id', runId,
      ],
      // cwd=evals/: the harness writes everything cwd-relative (report JSONs,
      // logs/run_evaluation). Must stay constant or resume-skip breaks.
      { cwd: EVALS_DIR, onChild: (child) => { current = child; } },
    );
  }
  console.log('[mark] all legs marked');
}

// ---- audit -----------------------------------------------------------------
function opAudit() {
  const expected = { standard: 60, hard: 45 };
  const legs = findLegs();
  let problems = 0;
  for (const { runId, set } of legs) {
    const reports = readdirSync(EVALS_DIR).filter((f) => f.endsWith(`.${runId}.json`));
    if (reports.length !== 1) {
      console.error(`[audit] ${runId}: expected 1 report JSON in evals/, found ${reports.length}`);
      problems++;
      continue;
    }
    const rep = JSON.parse(readFileSync(join(EVALS_DIR, reports[0]), 'utf8'));
    const line = `submitted ${rep.submitted_instances}/${expected[set]}, completed ${rep.completed_instances}, resolved ${rep.resolved_instances}, errors ${rep.error_instances}, empty ${rep.empty_patch_instances}`;
    if (rep.submitted_instances !== expected[set] || rep.completed_instances !== rep.submitted_instances || rep.error_instances > 0) {
      console.error(`[audit] ${runId}: INCOMPLETE — ${line}`);
      problems++;
    } else {
      console.log(`[audit] ${runId}: ok — ${line}`);
    }
  }
  if (problems > 0) throw new Error(`${problems} legs incomplete or missing`);
  console.log('[audit] all legs complete');
}

// ---- main ------------------------------------------------------------------
const OPS = { resolve: opResolve, ensure: opEnsure, mark: opMark, audit: opAudit };
const requested = process.argv.slice(2);
const sequence = requested.length > 0 ? requested : ['ensure', 'mark', 'audit'];
for (const name of sequence) {
  if (!OPS[name]) {
    console.error(`unknown operation '${name}' — valid: ${Object.keys(OPS).join(', ')}`);
    process.exit(2);
  }
}
try {
  for (const name of sequence) {
    await OPS[name]();
  }
} catch (err) {
  console.error(`[eval] failed: ${err.message}`);
  process.exit(1);
}
