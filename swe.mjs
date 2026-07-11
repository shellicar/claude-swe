#!/usr/bin/env node
// The system: one entry point, operations as verbs, worlds as declarations.
//
//   ./swe.mjs <target> [verb...] [flags]
//
//   target  a combination set (combinations/<name>.json) or dataset[/selection]
//   verbs   draw resolve ensure run mark status audit analyse — any subset, in
//           the given order, stopping at the first failure. Every verb is
//           idempotent/resumable, so rerunning a chain picks up where it died.
//           No verbs means status.
//   flags   --model <m> [--effort <e>] for an ad-hoc run without a combination
//
// Declarations (the authority; see docs/diagrams/operations.d2):
//   datasets/<name>.json      facts about a world: snapshot, image rule,
//                             marker, run configs, named selections
//   combinations/<name>.json  what to run: dataset, selections, legs
//   image-manifest.txt        instance -> image@digest (written by resolve)
//
// Records: runs/ (patches, trajectories, wire captures), evals/ (verdicts),
// analysis/ (derived figures). Paths come from the declarations.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, join } from 'node:path';
import { runExperiment } from './orchestration/experiment.mjs';
import { spawnAwait, onShutdown, repoRoot } from './orchestration/harness.mjs';

const MANIFEST = join(repoRoot, 'image-manifest.txt');
const EVALS_DIR = join(repoRoot, 'evals');

// ---- declarations ------------------------------------------------------------
const loadDataset = (name) => {
  const path = join(repoRoot, 'datasets', `${name}.json`);
  if (!existsSync(path)) throw new Error(`no such dataset: ${name} (${path})`);
  return JSON.parse(readFileSync(path, 'utf8'));
};

// A target is either a combination set or dataset[/selection].
const loadTarget = (t) => {
  const comboPath = join(repoRoot, 'combinations', `${t}.json`);
  if (existsSync(comboPath)) {
    const combo = JSON.parse(readFileSync(comboPath, 'utf8'));
    return { combo, ds: loadDataset(combo.dataset), selections: combo.selections };
  }
  const [dsName, sel] = t.split('/');
  const ds = loadDataset(dsName);
  if (sel && !ds.selections[sel]) throw new Error(`dataset ${dsName} has no selection '${sel}'`);
  return { combo: null, ds, selections: sel ? [sel] : Object.keys(ds.selections) };
};

const selectionIds = (ds, sel) =>
  readFileSync(join(repoRoot, ds.selections[sel].file), 'utf8').split('\n').map((l) => l.trim()).filter(Boolean);

const snapshotRows = (ds) =>
  readFileSync(join(repoRoot, ds.snapshot), 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));

// The dataset's image rule, applied to one row: returns { repo, tag }.
const imageRef = (ds, row) => {
  if (ds.image.source === 'row') return { repo: ds.image.repo, tag: row[ds.image.tagField] };
  if (ds.image.source === 'template') {
    // repo and tag both rendered from row fields: {org}, {repo}, {number}, ...
    const render = (tpl) => tpl.replace(/\{(\w+)\}/g, (_, f) => String(row[f]));
    return { repo: render(ds.image.repo).toLowerCase(), tag: render(ds.image.tag) };
  }
  // convention: template with {instance_id:FROM=TO} substitution
  const repo = ds.image.repo.replace(/\{instance_id:(.+)=(.+)\}/, (_, from, to) =>
    row.instance_id.replaceAll(from, to)).toLowerCase();
  return { repo, tag: ds.image.tag };
};

// ---- shared ------------------------------------------------------------------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Hub web API: far looser rate limit than the registry endpoint (whose
// anonymous allowance is ~100 manifest reads / 6 h — learned 2026-07-09).
async function hubDigest(repo, tag) {
  const url = `https://hub.docker.com/v2/repositories/${repo.replace('docker.io/', '')}/tags/${tag}`;
  for (let attempt = 1; ; attempt++) {
    const resp = await fetch(url);
    if (resp.status === 429 && attempt < 8) {
      console.log(`[resolve] 429 from hub API — backing off 60s (attempt ${attempt}/8)`);
      await sleep(60_000);
      continue;
    }
    if (!resp.ok) throw new Error(`hub API ${resp.status} for ${repo}:${tag}`);
    const body = await resp.json();
    if (!body.digest) throw new Error(`hub API returned no digest for ${repo}:${tag}`);
    return body.digest;
  }
}

const readManifest = () => {
  const entries = new Map();
  if (!existsSync(MANIFEST)) return entries;
  for (const line of readFileSync(MANIFEST, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const [iid, ref] = line.split(/\s+/);
    entries.set(iid, ref);
  }
  return entries;
};

const legs = ({ combo, ds }, flags) => {
  if (combo) return combo.legs;
  if (!flags.model) throw new Error('no combination set and no --model: nothing to run');
  const short = flags.model.split('/').pop().replace(/^claude-/, '');
  return [{ model: flags.model, effort: flags.effort, out: `runs/adhoc/${ds.name}-${short}` }];
};

// Scale-marker output dir for one leg × selection. The 'pro' selection keeps
// the original evals/pro/<model> layout (committed history, possibly being
// written by a live marking); later selections get a -<sel> suffix so two
// selections of the same model can never overwrite each other's verdicts.
const scaleOutDir = (ds, leg, sel) =>
  join(EVALS_DIR, ds.name, `${basename(leg.out)}${sel === 'pro' ? '' : `-${sel}`}`);

// Multi-SWE marker: verdicts (final_report.json) live per leg × selection; the
// harness's scratch (workdir, repos, logs) goes under evals/logs/, which is
// gitignored as regenerable.
const multiSweOutDir = (ds, leg, sel) => join(EVALS_DIR, ds.name, `${basename(leg.out)}-${sel}`);

const legConfigs = (ds, model, combo) => {
  // A combination may override the dataset's config list — configs are a knob
  // (that is what makes prompt/timeout variations declarable, not code).
  if (combo?.configs) return combo.configs;
  for (const [needle, configs] of Object.entries(ds.run.configExceptions ?? {})) {
    if (model.includes(needle)) return configs;
  }
  return ds.run.configs;
};

// ---- verbs ---------------------------------------------------------------------
// Deterministic PRNG (mulberry32) for seeded draws: same seed + same sorted
// population = same sample, forever. The committed selection file remains the
// actual freeze; the seed is provenance for how it was produced.
const mulberry32 = (seed) => {
  let a = seed | 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const seededSample = (ids, n, seed) => {
  const rand = mulberry32(seed);
  const pool = [...ids];
  // partial Fisher-Yates: shuffle the first n positions, take them
  for (let i = 0; i < n; i++) {
    const j = i + Math.floor(rand() * (pool.length - i));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, n).sort();
};

async function draw({ ds, selections }) {
  for (const sel of selections) {
    const decl = ds.selections[sel];
    if (!decl.rule) {
      console.log(`[draw] ${ds.name}/${sel}: hand-frozen (${decl.file}), nothing to draw`);
      continue;
    }
    const rows = snapshotRows(ds).filter((r) => r[decl.rule.field] === decl.rule.equals);
    let ids = rows.map((r) => r.instance_id).sort();
    if (decl.rule.n && decl.rule.n < ids.length) {
      ids = seededSample(ids, decl.rule.n, decl.rule.seed ?? 42);
      console.log(`[draw] ${ds.name}/${sel}: sampled ${ids.length} of ${rows.length} (seed ${decl.rule.seed ?? 42})`);
    }
    writeFileSync(join(repoRoot, decl.file), ids.join('\n') + '\n');
    console.log(`[draw] ${ds.name}/${sel}: wrote ${ids.length} ids to ${decl.file}`);
  }
}

async function resolve({ ds, selections }) {
  const manifest = readManifest();
  const rowsById = new Map(snapshotRows(ds).map((r) => [r.instance_id, r]));
  let added = 0;
  for (const sel of selections) {
    for (const iid of selectionIds(ds, sel)) {
      if (manifest.has(iid)) continue;
      const row = rowsById.get(iid);
      if (!row) throw new Error(`[resolve] ${iid} not in snapshot ${ds.snapshot}`);
      const { repo, tag } = imageRef(ds, row);
      const digest = await hubDigest(repo, tag);
      manifest.set(iid, `${repo}@${digest}`);
      added++;
      // incremental: progress survives any failure
      writeFileSync(MANIFEST, [...manifest.entries()].map(([i, r]) => `${i} ${r}`).join('\n') + '\n');
    }
  }
  console.log(`[resolve] ${added} new declarations; ${manifest.size} total in ${MANIFEST}`);
  if (added > 0) console.log('[resolve] review and commit the manifest — committing makes it the specification.');
}

async function ensure({ ds, selections }) {
  const manifest = readManifest();
  const rowsById = new Map(snapshotRows(ds).map((r) => [r.instance_id, r]));
  const missing = [];
  const wanted = [];
  let present = 0;
  for (const sel of selections) {
    for (const iid of selectionIds(ds, sel)) {
      const ref = manifest.get(iid);
      if (!ref) throw new Error(`[ensure] ${iid} not in the manifest — run resolve first`);
      wanted.push({ iid, ref });
      try {
        execFileSync('docker', ['image', 'inspect', ref], { stdio: 'ignore' });
        present++;
      } catch {
        missing.push({ iid, ref });
      }
    }
  }
  for (let i = 0; i < missing.length; i++) {
    console.log(`[ensure] pulling ${i + 1}/${missing.length} ${missing[i].iid} by digest...`);
    await spawnAwait('docker', ['pull', '--platform', 'linux/amd64', missing[i].ref]);
  }
  // Digest pulls leave images UNTAGGED, but markers look images up by name
  // (e.g. Multi-SWE's harness would fall back to BUILDING — the unpinned path).
  // Stamp each verified digest with its declared name so name lookups resolve
  // to exactly the declared bytes.
  let tagged = 0;
  for (const { iid, ref } of wanted) {
    const row = rowsById.get(iid);
    if (!row) continue;
    const { repo, tag } = imageRef(ds, row);
    const named = `${repo.replace('docker.io/', '')}:${tag}`;
    try {
      execFileSync('docker', ['image', 'inspect', named], { stdio: 'ignore' });
    } catch {
      execFileSync('docker', ['tag', ref, named], { stdio: 'ignore' });
      tagged++;
    }
  }
  console.log(`[ensure] ok — ${present} present, ${missing.length} pulled, ${tagged} tagged`);
}

async function run(target, flags) {
  const { combo, ds, selections } = target;
  const theLegs = legs(target, flags);
  const basePort = combo?.basePort ?? 19180;
  const workers = combo?.workers ?? Number(flags.workers ?? 2);
  const results = [];
  const pending = [];
  for (let i = 0; i < theLegs.length; i++) {
    const leg = theLegs[i];
    const short = leg.model.split('/').pop().replace(/^claude-/, '');
    const label = `${combo?.name ?? ds.name}-${short}${leg.effort ? '-' + leg.effort : ''}`;
    const promise = runExperiment({
      model: leg.model,
      out: leg.out,
      sets: selections,
      workers,
      effort: leg.effort,
      configs: legConfigs(ds, leg.model, combo),
      subset: ds.run.subset,
      port: basePort + i,
      log: `logs/${label}.log`,
      label,
      // the declared selections' ids — never the instances-<set>.txt filename
      // convention, which collides when two datasets name a selection alike
      selectionIds: Object.fromEntries(selections.map((s) => [s, selectionIds(ds, s)])),
    }).then(
      () => ({ label, ok: true }),
      (err) => ({ label, ok: false, err }),
    );
    if (combo?.parallel === false) {
      results.push(await promise);
    } else {
      pending.push(promise);
    }
  }
  for (const r of await Promise.all(pending)) results.push(r);
  const failed = results.filter((r) => !r.ok);
  for (const f of failed) console.error(`[run] FAILED ${f.label} — ${f.err.message} (see logs/${f.label}.log)`);
  if (failed.length > 0) throw new Error(`${failed.length} legs failed`);
  // Tripwire: preds containing ids outside the selection means the filter and
  // the declaration disagree — exactly the accident of 2026-07-11. Say so.
  for (const leg of theLegs) {
    for (const sel of selections) {
      const preds = join(repoRoot, leg.out, sel, 'preds.json');
      if (!existsSync(preds)) continue;
      const idSet = new Set(selectionIds(ds, sel));
      const strays = Object.keys(JSON.parse(readFileSync(preds, 'utf8'))).filter((iid) => !idSet.has(iid));
      if (strays.length > 0) {
        console.error(`[run] ⚠️ ${leg.out}/${sel}: preds contains ${strays.length} instances OUTSIDE the selection (e.g. ${strays[0]})`);
      }
    }
  }
  console.log(`[run] ${results.length} legs complete`);
}

async function mark(target, flags) {
  const { ds, selections } = target;
  const theLegs = legs(target, flags);
  mkdirSync(EVALS_DIR, { recursive: true });
  let current = null;
  onShutdown(async () => current?.kill('SIGTERM'));
  for (const leg of theLegs) {
    for (const sel of selections) {
      const preds = join(repoRoot, leg.out, sel, 'preds.json');
      if (!existsSync(preds)) {
        console.log(`[mark] ${leg.out}/${sel}: no predictions yet, skipping`);
        continue;
      }
      if (ds.marker.type === 'swebench') {
        const runId = `${leg.out.replaceAll('/', '_')}_${sel}`;
        console.log(`[mark] === ${runId} ===`);
        await spawnAwait(join(repoRoot, '.venv/bin/python'), [
          '-m', 'swebench.harness.run_evaluation',
          '--dataset_name', join(repoRoot, ds.snapshot),
          '--predictions_path', preds,
          '--max_workers', process.env.MARK_WORKERS ?? '2',
          '--namespace', 'swebench',
          '--run_id', runId,
        ], { cwd: EVALS_DIR, onChild: (c) => { current = c; } });
      } else if (ds.marker.type === 'scale') {
        const outDir = scaleOutDir(ds, leg, sel);
        mkdirSync(outDir, { recursive: true });
        const predsData = JSON.parse(readFileSync(preds, 'utf8'));
        const patches = Object.values(predsData).map((p) => ({ instance_id: p.instance_id, patch: p.model_patch }));
        const patchPath = join(outDir, 'patches.json');
        writeFileSync(patchPath, JSON.stringify(patches, null, 2));
        console.log(`[mark] === ${ds.name}/${basename(leg.out)} (${patches.length} patches) ===`);
        await spawnAwait(join(repoRoot, '.venv/bin/python'), [
          'swe_bench_pro_eval.py',
          '--raw_sample_path', join(repoRoot, ds.snapshot),
          '--patch_path', patchPath,
          '--output_dir', outDir,
          '--dockerhub_username', ds.marker.dockerhubUsername,
          '--scripts_dir', 'run_scripts',
          '--use_local_docker',
          '--docker_platform', 'linux/amd64',
          '--num_workers', process.env.MARK_WORKERS ?? '2',
        ], { cwd: join(repoRoot, ds.marker.harness), onChild: (c) => { current = c; } });
      } else if (ds.marker.type === 'multi-swe') {
        const outDir = multiSweOutDir(ds, leg, sel);
        const scratch = join(EVALS_DIR, 'logs', 'multi-swe', `${basename(leg.out)}-${sel}`);
        mkdirSync(outDir, { recursive: true });
        mkdirSync(scratch, { recursive: true });
        // Their patches format: JSONL of {org, repo, number, fix_patch};
        // org/repo/number come from the snapshot row. Selection members only —
        // strays in preds are not part of the paper.
        const predsData = JSON.parse(readFileSync(preds, 'utf8'));
        const rowsById = new Map(snapshotRows(ds).map((r) => [r.instance_id, r]));
        const lines = [];
        for (const iid of selectionIds(ds, sel)) {
          const p = predsData[iid];
          if (!p) continue;
          const row = rowsById.get(iid);
          lines.push(JSON.stringify({ org: row.org, repo: row.repo, number: row.number, fix_patch: p.model_patch ?? '' }));
        }
        const patchPath = join(outDir, 'patches.jsonl');
        writeFileSync(patchPath, lines.join('\n') + '\n');
        const workers = Number(process.env.MARK_WORKERS ?? 2);
        const cfgPath = join(outDir, 'config.json');
        writeFileSync(cfgPath, JSON.stringify({
          mode: 'evaluation',
          workdir: join(scratch, 'workdir'),
          patch_files: [patchPath],
          dataset_files: [join(repoRoot, ds.snapshot)],
          force_build: false,
          output_dir: outDir,
          specifics: [],
          skips: [],
          repo_dir: join(scratch, 'repos'),
          need_clone: false,
          global_env: [],
          clear_env: true,
          stop_on_error: false,
          max_workers: workers,
          max_workers_build_image: workers,
          max_workers_run_instance: workers,
          log_dir: join(scratch, 'logs'),
          log_level: 'INFO',
        }, null, 2));
        console.log(`[mark] === ${ds.name}/${basename(leg.out)}-${sel} (${lines.length} patches) ===`);
        await spawnAwait(join(repoRoot, '.venv/bin/python'), [
          '-m', 'multi_swe_bench.harness.run_evaluation',
          '--config', cfgPath,
        ], { onChild: (c) => { current = c; } });
      } else {
        throw new Error(`unknown marker type: ${ds.marker.type}`);
      }
    }
  }
  console.log('[mark] done');
}

async function audit(target, flags) {
  const { ds, selections } = target;
  const theLegs = legs(target, flags);
  const { readdirSync } = await import('node:fs');
  let problems = 0;
  for (const leg of theLegs) {
    for (const sel of selections) {
      const expected = ds.selections[sel].expected;
      const name = `${leg.out}/${sel}`;
      if (ds.marker.type === 'swebench') {
        const runId = `${leg.out.replaceAll('/', '_')}_${sel}`;
        const reports = readdirSync(EVALS_DIR).filter((f) => f.endsWith(`.${runId}.json`));
        if (reports.length !== 1) {
          console.error(`[audit] ${name}: expected 1 report JSON in evals/, found ${reports.length}`);
          problems++;
          continue;
        }
        const rep = JSON.parse(readFileSync(join(EVALS_DIR, reports[0]), 'utf8'));
        const line = `submitted ${rep.submitted_instances}/${expected}, completed ${rep.completed_instances}, resolved ${rep.resolved_instances}, errors ${rep.error_instances}, empty ${rep.empty_patch_instances}`;
        // Empty patches are legitimate attempts the harness never runs: they
        // count toward completeness as automatic unresolveds.
        if (rep.submitted_instances !== expected || rep.completed_instances + rep.empty_patch_instances !== rep.submitted_instances || rep.error_instances > 0) {
          console.error(`[audit] ${name}: INCOMPLETE — ${line}`);
          problems++;
        } else {
          console.log(`[audit] ${name}: ok — ${line}`);
        }
      } else if (ds.marker.type === 'scale') {
        const resultsPath = join(scaleOutDir(ds, leg, sel), 'eval_results.json');
        if (!existsSync(resultsPath)) {
          console.error(`[audit] ${name}: no eval_results.json`);
          problems++;
          continue;
        }
        const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
        const ids = selectionIds(ds, sel);
        const missing = ids.filter((iid) => !(iid in results));
        const resolved = Object.values(results).filter(Boolean).length;
        const line = `${Object.keys(results).length}/${ids.length} verdicts, resolved ${resolved}`;
        if (missing.length > 0) {
          console.error(`[audit] ${name}: INCOMPLETE — ${line}; missing ${missing.length}`);
          problems++;
        } else {
          console.log(`[audit] ${name}: ok — ${line}`);
        }
      } else if (ds.marker.type === 'multi-swe') {
        const reportPath = join(multiSweOutDir(ds, leg, sel), 'final_report.json');
        if (!existsSync(reportPath)) {
          console.error(`[audit] ${name}: no final_report.json`);
          problems++;
          continue;
        }
        const rep = JSON.parse(readFileSync(reportPath, 'utf8'));
        const line = `submitted ${rep.submitted_instances}/${expected}, completed ${rep.completed_instances}, resolved ${rep.resolved_instances}, errors ${rep.error_instances}, incomplete ${rep.incomplete_instances}, empty ${rep.empty_patch_instances}`;
        if (rep.submitted_instances !== expected || rep.error_instances > 0 || rep.incomplete_instances > 0) {
          console.error(`[audit] ${name}: INCOMPLETE — ${line}`);
          problems++;
        } else {
          console.log(`[audit] ${name}: ok — ${line}`);
        }
      } else {
        // An unknown marker must fail the audit, not silently pass it.
        throw new Error(`audit has no reader for marker type '${ds.marker.type}'`);
      }
    }
  }
  if (problems > 0) throw new Error(`${problems} legs incomplete — analysis would be built on holes`);
  console.log('[audit] all legs complete');
}

// Read-only: where the target stands with EVERY verb, in pipeline order.
// Reports state without changing anything; audit is shown as would-pass/fail.
// Emoji key: ✅ complete / nothing to do · ⚠️ partial or issue · ℹ️ not
// started · ❌ error or missing prerequisite.
const mark3 = (have, want) => (have >= want ? '✅' : have > 0 ? '⚠️' : 'ℹ️');

async function status(target, flags) {
  const { ds, selections } = target;
  const theLegs = legs(target, flags);
  const manifest = readManifest();
  const { readdirSync, statSync } = await import('node:fs');

  // draw: is each selection frozen, how many ids
  for (const sel of selections) {
    const decl = ds.selections[sel];
    const file = join(repoRoot, decl.file);
    if (!existsSync(file)) {
      console.log(`[status] draw     ❌ ${ds.name}/${sel}: NOT DRAWN (${decl.file} missing)`);
      continue;
    }
    const n = selectionIds(ds, sel).length;
    const how = decl.rule ? 'drawn by rule' : 'hand-frozen';
    const mk = n === decl.expected ? '✅' : '⚠️';
    console.log(`[status] draw     ${mk} ${ds.name}/${sel}: ${n} ids (${how}, expected ${decl.expected})`);
  }

  // resolve: manifest coverage per selection
  for (const sel of selections) {
    const ids = selectionIds(ds, sel);
    const declared = ids.filter((iid) => manifest.has(iid)).length;
    console.log(`[status] resolve  ${mark3(declared, ids.length)} ${ds.name}/${sel}: ${declared}/${ids.length} in manifest`);
  }

  // ensure: images actually present locally
  for (const sel of selections) {
    const ids = selectionIds(ds, sel);
    let present = 0;
    let undeclared = 0;
    for (const iid of ids) {
      const ref = manifest.get(iid);
      if (!ref) { undeclared++; continue; }
      try {
        execFileSync('docker', ['image', 'inspect', ref], { stdio: 'ignore' });
        present++;
      } catch {}
    }
    const note = undeclared > 0 ? ` (${undeclared} unresolved)` : '';
    const mk = undeclared > 0 ? '❌' : mark3(present, ids.length);
    console.log(`[status] ensure   ${mk} ${ds.name}/${sel}: ${present}/${ids.length} images local${note}`);
  }

  // run + mark per leg × selection — gathered once, printed grouped by verb
  let auditProblems = 0;
  let newestVerdict = 0; // mtime of the freshest verdict file, for staleness
  const rows = [];
  for (const leg of theLegs) {
    for (const sel of selections) {
      const ids = selectionIds(ds, sel);
      let ran = 0;
      let empty = 0;
      const preds = join(repoRoot, leg.out, sel, 'preds.json');
      if (existsSync(preds)) {
        const data = JSON.parse(readFileSync(preds, 'utf8'));
        // count only instances in the selection — preds may carry strays from
        // the pre-fix naming collision, and they must not inflate progress
        const inSel = ids.filter((iid) => iid in data);
        ran = inSel.length;
        empty = inSel.filter((iid) => !(data[iid].model_patch ?? '').trim()).length;
      }
      let verdicts = 0;
      let resolved = 0;
      if (ds.marker.type === 'swebench') {
        const runId = `${leg.out.replaceAll('/', '_')}_${sel}`;
        const reports = existsSync(EVALS_DIR) ? readdirSync(EVALS_DIR).filter((f) => f.endsWith(`.${runId}.json`)) : [];
        if (reports.length === 1) {
          const repPath = join(EVALS_DIR, reports[0]);
          const rep = JSON.parse(readFileSync(repPath, 'utf8'));
          verdicts = rep.completed_instances + rep.empty_patch_instances;
          resolved = rep.resolved_instances;
          newestVerdict = Math.max(newestVerdict, statSync(repPath).mtimeMs);
        }
      } else if (ds.marker.type === 'scale') {
        const resultsPath = join(scaleOutDir(ds, leg, sel), 'eval_results.json');
        if (existsSync(resultsPath)) {
          const results = JSON.parse(readFileSync(resultsPath, 'utf8'));
          verdicts = Object.keys(results).length;
          resolved = Object.values(results).filter(Boolean).length;
          newestVerdict = Math.max(newestVerdict, statSync(resultsPath).mtimeMs);
        }
      } else if (ds.marker.type === 'multi-swe') {
        const reportPath = join(multiSweOutDir(ds, leg, sel), 'final_report.json');
        if (existsSync(reportPath)) {
          const rep = JSON.parse(readFileSync(reportPath, 'utf8'));
          verdicts = rep.completed_instances + rep.empty_patch_instances;
          resolved = rep.resolved_instances;
          newestVerdict = Math.max(newestVerdict, statSync(reportPath).mtimeMs);
        }
      }
      if (ran < ids.length || verdicts < ids.length) auditProblems++;
      rows.push({ name: `${leg.out}/${sel}`, total: ids.length, ran, empty, verdicts, resolved });
    }
  }
  for (const r of rows) {
    const emptyNote = r.empty > 0 ? ` (${r.empty} empty)` : '';
    // Empty patches are legitimate but always worth an eyebrow: ⚠️ even at n/n.
    const mk = r.empty > 0 && r.ran >= r.total ? '⚠️' : mark3(r.ran, r.total);
    console.log(`[status] run      ${mk} ${r.name}: ${r.ran}/${r.total}${emptyNote}`);
  }
  for (const r of rows) {
    console.log(`[status] mark     ${mark3(r.verdicts, r.total)} ${r.name}: ${r.verdicts}/${r.total} verdicts (${r.resolved} resolved)`);
  }

  // audit: would it pass right now
  console.log(`[status] audit    ${auditProblems === 0 ? '✅ would pass' : `❌ would FAIL: ${auditProblems} leg/selection pairs incomplete`}`);

  // analyse: do the outputs exist, and are they newer than the verdicts —
  // an analysis older than the freshest verdict is showing stale numbers.
  const analysisBase = join(repoRoot, 'analysis', ds.name === 'verified' ? 'verified' : ds.name);
  for (const ext of ['json', 'md']) {
    const p = `${analysisBase}.${ext}`;
    if (!existsSync(p)) {
      console.log(`[status] analyse  ℹ️ ${p.replace(repoRoot + '/', '')}: not written yet`);
      continue;
    }
    const st = statSync(p);
    if (newestVerdict > st.mtimeMs) {
      console.log(`[status] analyse  ⚠️ ${p.replace(repoRoot + '/', '')}: STALE — written ${st.mtime.toISOString()}, verdicts are newer`);
    } else {
      console.log(`[status] analyse  ✅ ${p.replace(repoRoot + '/', '')}: written ${st.mtime.toISOString()}`);
    }
  }
}

async function analyse({ ds }) {
  if (!ds.analyser) throw new Error(`dataset ${ds.name} declares no analyser yet`);
  // The audit gate: a chain places audit before analyse; running analyse alone
  // is allowed but the analyser only sees what exists — verdicts it cannot
  // find render as "—" in its output, never as invented numbers.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, ds.analyser)]);
}

// ---- main ----------------------------------------------------------------------
const VERBS = { draw, resolve, ensure, run, mark, status, audit, analyse };

const args = process.argv.slice(2);
const targetName = args.shift();
const verbs = [];
while (args.length > 0 && VERBS[args[0]]) verbs.push(args.shift());
if (verbs.length === 0) verbs.push('status');
const flags = {};
while (args.length > 0) {
  const a = args.shift();
  if (a.startsWith('--')) flags[a.slice(2)] = args.shift();
}

if (!targetName) {
  const { readdirSync } = await import('node:fs');
  const list = (dir) => {
    try {
      return readdirSync(join(repoRoot, dir)).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, ''));
    } catch {
      return [];
    }
  };
  const datasets = list('datasets');
  console.error('usage: ./swe.mjs <target> [verb...] [--model m] [--effort e] [--workers n]');
  console.error('verbs:        draw resolve ensure run mark status audit analyse (none = status)');
  console.error(`combinations: ${list('combinations').join(', ')}`);
  console.error(`datasets:     ${datasets.map((d) => {
    try {
      return `${d} (${Object.keys(loadDataset(d).selections).map((s) => `${d}/${s}`).join(', ')})`;
    } catch {
      return d;
    }
  }).join('; ')}`);
  process.exit(2);
}

try {
  const target = loadTarget(targetName);
  for (const verb of verbs) {
    await VERBS[verb](target, flags);
  }
} catch (err) {
  console.error(`[swe] failed: ${err.message}`);
  process.exit(1);
}
