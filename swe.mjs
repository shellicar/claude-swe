#!/usr/bin/env node
// The system: one entry point, operations as verbs, worlds as declarations.
//
//   ./swe.mjs [verb...] [target...] [flags]   (any order — verbs × targets)
//
//   verbs    draw resolve ensure run mark status audit analyse — any subset,
//            chained in the given order per target, stopping at the first
//            failure. Every verb is idempotent/resumable. No verbs = status.
//   targets  combination names (combinations/*.json) or dataset[/selection].
//            No targets = every combination: bare `./swe.mjs` is the whole
//            dashboard; `./swe.mjs analyse` analyses everything.
//   flags    --model <m> [--effort <e>] for an ad-hoc run without a combination
//
// Declarations (the authority; see docs/diagrams/operations.d2):
//   datasets/<name>.json      facts about a world: snapshot, image rule,
//                             marker, run configs, named selections
//   combinations/<name>.json  what to run: dataset, selections, legs
//   image-manifest.txt        instance -> image@digest (written by resolve)
//
// Records: runs/ (patches, trajectories, wire captures), evals/ (verdicts),
// analysis/ (derived figures). Paths come from the declarations.
import { execFileSync, spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync,
} from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { runExperiment } from './orchestration/experiment.mjs';
import { spawnAwait, stopChild, onShutdown, repoRoot } from './orchestration/harness.mjs';

const MANIFEST = join(repoRoot, 'image-manifest.txt');
const EVALS_DIR = join(repoRoot, 'evals');

// Machine capacity, declared once. Experiment design stays per-combination;
// how much this box chews at once does not belong copied into 27 files.
const RIG = JSON.parse(readFileSync(join(repoRoot, 'rig.json'), 'utf8'));
const markWorkers = () => String(process.env.MARK_WORKERS ?? RIG.markWorkers);

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

// --model does one of two jobs depending on whether a combination was named:
// with one it FILTERS that combination's legs (a substring of the model id, so
// `--model opus-5` picks every effort leg of one model out of a big sweep);
// without one it declares the model for an ad-hoc run.
// Legs already on disk for these selections, read from what each recorded
// rather than guessed from its path: preds.json carries the model that
// produced it.
const discoverLegs = (ds, selections) => {
  const root = join(repoRoot, 'runs');
  const out = new Map();
  if (!existsSync(root)) return [];
  // Only combinations belonging to THIS dataset. Selection names collide
  // across datasets — `cpp` is 20 instances in multi and 11 fmtlib ones in
  // multilingual — so matching on the directory name alone dragged seven
  // multilingual legs into `status multi/cpp`, each reporting 0/20 against a
  // selection they never ran, and failing the audit for it.
  const mine = new Set(
    readdirSync(join(repoRoot, 'combinations'))
      .filter((f) => f.endsWith('.json'))
      .map((f) => JSON.parse(readFileSync(join(repoRoot, 'combinations', f), 'utf8')))
      .filter((c) => c.dataset === ds.name)
      .map((c) => c.name),
  );
  for (const combo of readdirSync(root)) {
    const comboDir = join(root, combo);
    if (!statSync(comboDir).isDirectory()) continue;
    // `adhoc` holds `<dataset>-<model>` legs rather than a combination's.
    if (combo === 'adhoc') {
      for (const leg of readdirSync(comboDir)) {
        if (!leg.startsWith(`${ds.name}-`)) continue;
        for (const sel of selections) {
          const preds = join(comboDir, leg, sel, 'preds.json');
          if (!existsSync(preds)) continue;
          const first = Object.values(JSON.parse(readFileSync(preds, 'utf8')))[0];
          out.set(`runs/adhoc/${leg}`, {
            model: first?.model_name_or_path ?? leg,
            out: `runs/adhoc/${leg}`,
          });
        }
      }
      continue;
    }
    if (!mine.has(combo)) continue;
    for (const leg of readdirSync(comboDir)) {
      const legDir = join(comboDir, leg);
      if (!statSync(legDir).isDirectory()) continue;
      for (const sel of selections) {
        const preds = join(legDir, sel, 'preds.json');
        if (!existsSync(preds)) continue;
        const first = Object.values(JSON.parse(readFileSync(preds, 'utf8')))[0];
        out.set(`runs/${combo}/${leg}`, {
          model: first?.model_name_or_path ?? leg,
          out: `runs/${combo}/${leg}`,
        });
      }
    }
  }
  return [...out.values()];
};

const legs = ({ combo, ds, selections }, flags, { forRun = false } = {}) => {
  if (combo) {
    let wanted = combo.legs;
    if (flags.model) wanted = wanted.filter((l) => l.model.includes(flags.model));
    // --effort narrows further, so one rung of a model's ladder can be run
    // on its own: the cheapest level first tells you whether the rest is
    // worth paying for.
    if (flags.effort) wanted = wanted.filter((l) => l.effort === flags.effort);
    if (wanted.length === 0) {
      const shown = [flags.model && `--model ${flags.model}`,
        flags.effort && `--effort ${flags.effort}`].filter(Boolean).join(' ');
      throw new Error(
        `${shown} matches no leg in ${combo.name} `
        + `(has ${[...new Set(combo.legs.map(
          (l) => l.model + (l.effort ? ` @${l.effort}` : ''),
        ))].join(', ')})`,
      );
    }
    if (flags.model || flags.effort) return wanted;
    return combo.legs;
  }
  // A bare dataset target (`verified/micro`) names no combination, so there is
  // no declared list of legs. --model supplies one for an ad-hoc RUN; without
  // it, the legs are whatever has already been run — which is exactly what
  // status, mark, audit and analyse want, and what --help has always said
  // those targets do.
  if (!flags.model) {
    // Never for `run`. Discovery answers "what has been done", which is what
    // the reading verbs want; handing that same list to `run` makes a bare
    // dataset target start work on every leg it finds — it did, spending real
    // calls on five walker legs before anyone asked for anything.
    if (forRun) {
      throw new Error(
        `${ds.name}: run needs a combination or --model. A bare dataset target`
        + ' reads (status, mark, audit, analyse); it does not decide what to run.');
    }
    const found = discoverLegs(ds, selections);
    if (found.length === 0) {
      throw new Error(
        `no combination set, no --model, and nothing under runs/ for `
        + `${ds.name}/${selections.join(',')} — name a combination, or pass`
        + ' --model to start an ad-hoc run');
    }
    return found;
  }
  const short = flags.model.split('/').pop().replace(/^claude-/, '');
  // Effort is part of the path: without it, `--model X --effort low` and
  // `--model X --effort max` share one directory, so the second silently
  // overwrites the first's preds.json and both claim one provenance record.
  const suffix = flags.effort ? `${short}-${flags.effort}` : short;
  return [{ model: flags.model, effort: flags.effort, out: `runs/adhoc/${ds.name}-${suffix}` }];
};

// Scale-marker output dir for one leg × selection. The 'pro' selection keeps
// the original evals/pro/<model> layout (committed history, possibly being
// written by a live marking); later selections get a -<sel> suffix so two
// selections of the same model can never overwrite each other's verdicts.
const scaleOutDir = (ds, leg, sel) =>
  join(EVALS_DIR, ds.name, `${basename(leg.out)}${sel === 'pro' ? '' : `-${sel}`}`);

// Multi-SWE marker: verdicts (final_report.json) live per leg × selection; the
// harness's scratch (workdir, repos, logs) goes under evals/logs/, which is
// gitignored as regenerable. The key is the leg's FULL out path, not the model
// basename — two combinations sharing dataset, selection and model (control vs
// variation) collided on basename alone and the later mark overwrote the
// earlier one's verdicts (2026-07-11).
const multiSweKey = (leg, sel) =>
  `${leg.out.replace(/^runs\//, '').replaceAll('/', '-')}-${sel}`;

const multiSweOutDir = (ds, leg, sel) => join(EVALS_DIR, ds.name, multiSweKey(leg, sel));

// The harness's scratch, keyed the same way and for the same reason. It was
// keyed on the model basename alone, so runs/multi/opus-4-8/cpp and
// runs/cpp-variation/opus-4-8/cpp shared one directory: two legs writing over
// each other's working state, and anything counting per-instance progress from
// it saw one leg's work twice and reported an unmarked leg as complete.
const multiSweScratch = (leg, sel) =>
  join(EVALS_DIR, 'logs', 'multi-swe', multiSweKey(leg, sel));

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
    // The tag must point at the DIGEST the manifest pins, not merely exist. A
    // tag left by an earlier pull resolves fine and silently shadows the pin,
    // so instances get graded against different bytes while provenance records
    // the manifest sha — wrong verdicts that look entirely normal. Compare ids
    // and retag when they differ.
    let current = null;
    try {
      current = execFileSync('docker', ['image', 'inspect', named, '--format', '{{.Id}}'],
        { encoding: 'utf8' }).trim();
    } catch {
      current = null;
    }
    const pinned = execFileSync('docker', ['image', 'inspect', ref, '--format', '{{.Id}}'],
      { encoding: 'utf8' }).trim();
    if (current !== pinned) {
      execFileSync('docker', ['tag', ref, named], { stdio: 'ignore' });
      tagged++;
      if (current) console.log(`[ensure] ${named} pointed elsewhere — retagged to the pinned digest`);
    }
  }
  console.log(`[ensure] ok — ${present} present, ${missing.length} pulled, ${tagged} tagged`);
}

async function run(target, flags) {
  const { combo, ds, selections } = target;
  const theLegs = legs(target, flags, { forRun: true });
  // Preflight: refuse to start when declared images are not local. Without
  // this, docker run's implicit pull races mini's 120s container-start
  // timeout and every instance dies as an empty preds entry (pro/go,
  // 2026-07-14). ensure is the pull path — pinned by digest, no races.
  const manifest = readManifest();
  const missingImages = [];
  for (const sel of selections) {
    for (const iid of selectionIds(ds, sel)) {
      const ref = manifest.get(iid);
      if (!ref) { missingImages.push(`${sel}/${iid} (unresolved)`); continue; }
      try {
        execFileSync('docker', ['image', 'inspect', ref], { stdio: 'ignore' });
      } catch {
        missingImages.push(`${sel}/${iid}`);
      }
    }
  }
  if (missingImages.length > 0) {
    throw new Error(`run refused: ${missingImages.length} declared images not local (e.g. ${missingImages[0]}) — run ensure first`);
  }
  const basePort = combo?.basePort ?? RIG.basePort;
  const workers = Number(flags.workers ?? combo?.workers ?? RIG.agentWorkers);
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

// What produced a verdict, beyond the patch itself. A verdict can change
// without the patch changing: the marker is an EDITABLE install of
// vendor/swebench, the dataset snapshot pins the tests, and the image manifest
// pins what they run against. CLAUDE.md notes the harness version is silently
// part of any experiment — this is what stops it being silent, so a card built
// from legs marked by different graders can be spotted rather than trusted.
const sha256 = (p) => (existsSync(p)
  ? createHash('sha256').update(readFileSync(p)).digest('hex').slice(0, 16)
  : null);

const gitDescribe = (dir) => {
  const at = join(repoRoot, dir);
  if (!existsSync(at)) return null;
  const run = (args) => {
    const r = spawnSync('git', ['-C', at, ...args], { encoding: 'utf8' });
    return r.status === 0 ? r.stdout.trim() : null;
  };
  return {
    commit: run(['rev-parse', 'HEAD']),
    // A dirty marker means the verdicts came from code that exists nowhere
    // else — not reproducible, and worth seeing in the record.
    dirty: run(['status', '--porcelain']) !== '',
  };
};

// Where a marker package ACTUALLY lives, asked of the interpreter rather than
// assumed from pyproject.toml. The venv drifted once: pyproject declared
// swebench editable from vendor/, the venv held PyPI 4.1.0, and provenance
// dutifully recorded the submodule's commit for grading that commit never did.
// Only the installed module knows.
const installedAt = (module_) => {
  const r = spawnSync(join(repoRoot, '.venv/bin/python'), [
    '-c', `import ${module_},os;print(os.path.dirname(os.path.dirname(${module_}.__file__)))`,
  ], { encoding: 'utf8' });
  if (r.status !== 0) return null;
  const at = r.stdout.trim();
  return at.startsWith(repoRoot) ? at.slice(repoRoot.length + 1) : at;
};

function writeProvenance(ds, leg, sel, extra) {
  const module_ = ds.marker.type === 'swebench' ? 'swebench'
    : ds.marker.type === 'scale' ? null : 'multi_swe_bench';
  const marker = (module_ && installedAt(module_))
    ?? (ds.marker.harness ?? `vendor/${ds.marker.type}`);
  const record = {
    marked_at: new Date().toISOString(),
    leg: leg.out,
    selection: sel,
    // `vendored` false means the package came from an index, so the commit
    // below is null and the fork's patches are NOT what graded this.
    marker: {
      type: ds.marker.type,
      path: marker,
      vendored: marker.startsWith('vendor/'),
      ...gitDescribe(marker),
    },
    dataset: { snapshot: ds.snapshot, sha256: sha256(join(repoRoot, ds.snapshot)) },
    image_manifest_sha256: sha256(MANIFEST),
    rig: gitDescribe('.'),
    mark_workers: markWorkers(),
    ...extra,
  };
  const path = join(EVALS_DIR, 'provenance',
    `${leg.out.replaceAll('/', '_')}_${sel}.json`);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(record, null, 2));
  const m = record.marker;
  console.log(`[mark] provenance: ${ds.marker.type} @ ${m.commit?.slice(0, 8) ?? '?'}`
    + `${m.dirty ? ' (DIRTY)' : ''} -> ${path.slice(repoRoot.length + 1)}`);
}

// pyproject.toml declares every marker as an editable install from vendor/,
// but a venv can drift from its declaration and nothing complains: swebench
// sat as PyPI 4.1.0 for weeks while the fork's fixes went unused and every
// verdict was attributed to a commit that never ran. Check before grading,
// because a wrong marker produces plausible verdicts, not errors.
function requireVendoredMarker(ds) {
  const module_ = ds.marker.type === 'swebench' ? 'swebench'
    : ds.marker.type === 'scale' ? null : 'multi_swe_bench';
  if (!module_) return;
  const at = installedAt(module_);
  if (!at) throw new Error(`${module_} is not installed — run \`uv sync\``);
  if (!at.startsWith('vendor/')) {
    throw new Error(
      `${module_} resolves to ${at}, not the vendored fork in vendor/.\n`
      + '       Verdicts would come from an unpatched package while provenance\n'
      + '       claims the submodule. Run `uv sync` to restore the declared\n'
      + '       editable installs, then re-mark.',
    );
  }
}

// Marking writes one log directory per graded instance, so that count only
// stops rising when nothing is happening. A stall is otherwise silent: the
// harness's progress bar keeps displaying its last frame, so a laptop that
// slept mid-run showed "41 seconds remaining" for thirteen hours.
function watchProgress(label, everyMs = 5 * 60_000) {
  // The most recent write anywhere under evals/, which covers every marker:
  // multi-swe and Scale write their own directories and never touch
  // evals/logs, so watching only that reports a stall through an hour of
  // healthy work. An mtime is the right signal — an earlier version compared
  // the character length of a `find` listing, which is equal for two
  // different sets of equal-length paths, and walked 111k entries
  // synchronously on the event loop every tick.
  const newest = () => {
    try {
      const out = execFileSync('find', [EVALS_DIR, '-newermt', '-10 minutes',
        '-type', 'f', '-print', '-quit'], { encoding: 'utf8' });
      return out.trim() ? Date.now() : 0;
    } catch {
      return 0;
    }
  };
  let since = Date.now();
  const timer = setInterval(() => {
    if (newest()) {
      since = Date.now();
      return;
    }
    console.error(
      `[mark] ${label}: nothing written under evals/ for `
      + `${Math.round((Date.now() - since) / 60_000)} min — stalled? A slept`
      + ' machine leaves the harness waiting on a container that no longer'
      + ' exists. Stop and re-run: marking resumes from what is already graded.');
  }, everyMs);
  timer.unref?.();
  return () => clearInterval(timer);
}

// Containers the SWEBENCH marker leaves behind. They belong to dockerd, not to
// the process tree, so no signal reaches them: killing the harness kills the
// thing that WOULD have removed them and nothing else. swebench names its own
// `sweb.eval.<instance>.<run_id>` and the run ids are ours, so they can be
// attributed exactly.
//
// multi-swe and Scale are NOT covered: their containers take docker's random
// names, carrying nothing that ties them to a leg. Removing every container on
// an mswebench image was the alternative, and it took out the harness's own
// tooling container the first time it ran. So they are reported instead —
// `./swe.mjs cleanup` lists them and leaves the judgement to a human.
// `./swe.mjs cleanup` — for containers already stranded by an interrupted mark
// before the reaping above existed, or by a crash that outran it. Lists what it
// would remove and why, then removes it: eval containers are disposable, but a
// container this rig did not start is left alone.
let cleanedUp = false;

async function cleanup() {
  if (cleanedUp) return; // no target, so once per invocation, not once per target
  cleanedUp = true;
  const listed = spawnSync('docker', ['ps', '-a', '--format', '{{.Names}}\t{{.Image}}\t{{.Status}}'],
    { encoding: 'utf8' });
  if (listed.status !== 0) throw new Error('docker ps failed');
  const rows = listed.stdout.trim().split('\n').filter(Boolean).map((l) => l.split('\t'));
  // ONLY names this rig creates. Matching the multi-swe harness by image
  // instead swept up its own tooling container (mswebench/nix_swe), which
  // nothing here started — a container whose provenance is unclear is reported,
  // never removed.
  const ours = rows.filter(([name]) =>
    name.startsWith('sweb.eval.') || name.startsWith('minisweagent-'));
  const ourNames = new Set(ours.map(([name]) => name));
  const unattributable = rows.filter(([name, image]) =>
    !ourNames.has(name) && (image ?? '').includes('mswebench'));

  if (ours.length === 0) console.log('[cleanup] nothing of ours to remove');
  else {
    for (const [name, image, status] of ours) {
      console.log(`[cleanup] ${name}  ${status}  (${image})`);
    }
    spawnSync('docker', ['rm', '-f', ...ours.map(([n]) => n)], { stdio: 'ignore' });
    console.log(`[cleanup] removed ${ours.length}`);
  }

  for (const [name, image, status] of unattributable) {
    console.log(`[cleanup] left alone (not ours to judge): ${name}  ${status}  (${image})`);
  }
}

function reapMarkerContainers(runIds) {
  const listed = spawnSync('docker', ['ps', '-a', '--format', '{{.Names}}\t{{.Image}}'],
    { encoding: 'utf8' });
  if (listed.status !== 0) return;
  // Names we created, for run ids we started. Not an image match: that swept
  // up the multi-swe harness's own tooling container.
  const doomed = listed.stdout.trim().split('\n').filter(Boolean)
    .map((l) => l.split('\t'))
    .filter(([name]) => runIds.some((id) => name.endsWith(`.${id}`)))
    .map(([name]) => name);
  if (doomed.length > 0) {
    console.error(`[mark] removing ${doomed.length} container(s) the marker left behind`);
    spawnSync('docker', ['rm', '-f', ...doomed], { stdio: 'ignore' });
  }
  // Say what was NOT handled, rather than leaving it to be discovered later.
  const strays = listed.stdout.trim().split('\n').filter(Boolean)
    .map((l) => l.split('\t'))
    .filter(([name, image]) => !doomed.includes(name) && (image ?? '').includes('mswebench'));
  if (strays.length > 0) {
    console.error(
      `[mark] ${strays.length} multi-swe container(s) cannot be attributed to a leg`
      + ' and were left: run `./swe.mjs cleanup` to see them');
  }
}

async function mark(target, flags) {
  const { ds, selections } = target;
  requireVendoredMarker(ds);
  const theLegs = legs(target, flags);
  mkdirSync(EVALS_DIR, { recursive: true });
  const stopWatch = watchProgress(ds.name);
  const startedRunIds = [];
  let current = null;
  // Order matters: stop the child and WAIT, then reap what it could not.
  // Removing containers while the harness still holds them races it.
  onShutdown(async () => {
    stopWatch();
    await stopChild(current);
    reapMarkerContainers(startedRunIds);
  });
  try {
  for (const leg of theLegs) {
    for (const sel of selections) {
      const preds = join(repoRoot, leg.out, sel, 'preds.json');
      if (!existsSync(preds)) {
        console.log(`[mark] ${leg.out}/${sel}: no predictions yet, skipping`);
        continue;
      }
      if (ds.marker.type === 'swebench') {
        const runId = `${leg.out.replaceAll('/', '_')}_${sel}`;
        startedRunIds.push(runId); // so an interrupted mark can reap its containers
        // Content-aware resume. swebench skips any instance whose log dir exists,
        // blind to whether the prediction changed — so a re-mark after fixing a
        // patch silently served the stale verdict (the recurring "re-mark did
        // nothing" trap). Drop the log for any instance whose stored patch no
        // longer matches what was marked, forcing swebench to re-evaluate it.
        const norm = (s) => (s ?? '').replace(/\n+$/, '');
        const logRoot = join(EVALS_DIR, 'logs', 'run_evaluation', runId);
        let stale = 0;
        for (const [iid, p] of Object.entries(JSON.parse(readFileSync(preds, 'utf8')))) {
          const dir = join(logRoot, (p.model_name_or_path ?? '').replaceAll('/', '__'), iid);
          if (existsSync(join(dir, 'patch.diff')) && norm(readFileSync(join(dir, 'patch.diff'), 'utf8')) !== norm(p.model_patch)) {
            rmSync(dir, { recursive: true, force: true });
            stale++;
          }
        }
        if (stale) console.log(`[mark] re-evaluating ${stale} instance(s) whose patch changed since last mark`);
        console.log(`[mark] === ${runId} ===`);
        await spawnAwait(join(repoRoot, '.venv/bin/python'), [
          '-m', 'swebench.harness.run_evaluation',
          '--dataset_name', join(repoRoot, ds.snapshot),
          '--predictions_path', preds,
          '--max_workers', markWorkers(),
          '--namespace', 'swebench',
          '--run_id', runId,
        ], { cwd: EVALS_DIR, onChild: (c) => { current = c; } });
        writeProvenance(ds, leg, sel, { run_id: runId });
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
          '--num_workers', markWorkers(),
        ], { cwd: join(repoRoot, ds.marker.harness), onChild: (c) => { current = c; } });
        writeProvenance(ds, leg, sel, { output_dir: outDir.slice(repoRoot.length + 1) });
      } else if (ds.marker.type === 'multi-swe') {
        const outDir = multiSweOutDir(ds, leg, sel);
        const scratch = multiSweScratch(leg, sel);
        mkdirSync(outDir, { recursive: true });
        // The harness validates these dirs at startup rather than creating them.
        for (const d of ['workdir', 'repos', 'logs']) mkdirSync(join(scratch, d), { recursive: true });
        // Their patches format: JSONL of {org, repo, number, fix_patch};
        // org/repo/number come from the snapshot row. Selection members only —
        // strays in preds are not part of the paper.
        const predsData = JSON.parse(readFileSync(preds, 'utf8'));
        const rowsById = new Map(snapshotRows(ds).map((r) => [r.instance_id, r]));
        const lines = [];
        const datasetLines = [];
        for (const iid of selectionIds(ds, sel)) {
          const p = predsData[iid];
          if (!p) continue;
          const row = rowsById.get(iid);
          lines.push(JSON.stringify({ org: row.org, repo: row.repo, number: row.number, fix_patch: p.model_patch ?? '' }));
          // The harness selects dataset rows by PR NUMBER ALONE, so feeding it
          // the full snapshot lets a number collision drag in foreign repos
          // (rayon pr-986 summoned fd#986 and json#986 as phantom errors).
          // Give it only the selection's own rows.
          datasetLines.push(JSON.stringify(row));
        }
        const patchPath = join(outDir, 'patches.jsonl');
        writeFileSync(patchPath, lines.join('\n') + '\n');
        const datasetPath = join(outDir, 'dataset.jsonl');
        writeFileSync(datasetPath, datasetLines.join('\n') + '\n');
        const workers = Number(markWorkers());
        const cfgPath = join(outDir, 'config.json');
        writeFileSync(cfgPath, JSON.stringify({
          mode: 'evaluation',
          workdir: join(scratch, 'workdir'),
          patch_files: [patchPath],
          dataset_files: [datasetPath],
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
        writeProvenance(ds, leg, sel, { output_dir: outDir.slice(repoRoot.length + 1) });
      } else {
        throw new Error(`unknown marker type: ${ds.marker.type}`);
      }
    }
  }
  } finally {
    // Without this the watcher outlives mark and warns about stalled marking
    // all the way through whatever verb runs next.
    stopWatch();
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
  for (const fname of ['data.json', 'table.html']) {
    const p = join(repoRoot, 'analysis', ds.name, fname);
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

// An analyser rebuilds every card for its dataset, so running it once per
// TARGET rebuilt `verified` twenty-odd times in one invocation — every arm and
// variation shares that dataset. Once per dataset per invocation is enough.
const analysedDatasets = new Set();

async function analyse({ ds, selections }) {
  if (!ds.analyser) throw new Error(`dataset ${ds.name} declares no analyser yet`);
  // Coverage check: each analyser declares which selections its sections
  // cover. A selection missing from the list means the tables just silently
  // omitted it (how element/tokio briefly vanished, 2026-07-12) — fail loudly.
  // Selections declared `"analyse": false` are smoke/utility sets (micro), not
  // experiments: nobody wants a table of three instances, so they are exempt
  // rather than crying wolf on every run.
  //
  // This runs for EVERY target even though the analyser itself runs once per
  // dataset: the de-dup below is about not rebuilding the same cards twenty
  // times, and folding the gate into it meant only the first target's
  // selections were ever checked.
  const checkCoverage = () => {
    const dataPath = join(repoRoot, 'analysis', ds.name, 'data.json');
    const { covers } = JSON.parse(readFileSync(dataPath, 'utf8'));
    // Absent `covers` disables the gate that exists to catch silent omissions,
    // which is how it sat switched off unnoticed. Missing is a failure.
    if (!covers) {
      throw new Error(
        `analysis/${ds.name}/data.json has no "covers" — ${ds.analyser} must`
        + ' declare which selections it covers, or the completeness gate is off');
    }
    const analysed = selections.filter((s) => ds.selections?.[s]?.analyse !== false);
    const missing = analysed.filter((s) => !covers.includes(s));
    if (missing.length > 0) {
      throw new Error(`${ds.analyser} does not cover selection(s) ${missing.join(', ')} — extend its sections`);
    }
  };

  if (analysedDatasets.has(ds.name)) {
    checkCoverage();
    return;
  }
  analysedDatasets.add(ds.name);
  // The audit gate: a chain places audit before analyse; running analyse alone
  // is allowed but the analyser only sees what exists — verdicts it cannot
  // find render as "—" in its output, never as invented numbers.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, ds.analyser)]);
  checkCoverage();
  // The overview joins every dataset's json into one card; regenerating it
  // here means it can never be staler than the analysis it summarises.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, 'analyse-overview.py')]);
  // Coverage is cross-dataset like the overview: what ran where, at which
  // effort, generated from the record so it can never be stale.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, 'analyse-coverage.py')]);
  // Experiments get their own cards: columns are contenders, rows are
  // control/variation/delta — each contender against itself under the two
  // conditions. See analysis/README.md.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, 'analyse-experiments.py')]);
  // Ad-hoc legs (--model, outside a combination) still cost money and still
  // get marked, so their figures come from the pipeline too.
  await spawnAwait(join(repoRoot, '.venv/bin/python'), [join(repoRoot, 'analyse-adhoc.py')]);
}

// ---- main ----------------------------------------------------------------------
// `cleanup` takes no target — stranded containers belong to no dataset by the
// time they are stranded.
const VERBS = { draw, resolve, ensure, run, mark, status, audit, analyse, cleanup };

const { readdirSync: readdir } = await import('node:fs');
const listJson = (dir) => {
  try {
    return readdir(join(repoRoot, dir)).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, ''));
  } catch {
    return [];
  }
};

const VERB_HELP = {
  draw: 'pick a selection\u2019s instances by its declared rule and freeze the list',
  resolve: 'look up each instance\u2019s image digest at the registry, record it in the manifest',
  ensure: 'make local Docker match the manifest \u2014 pull missing, refuse on mismatch',
  run: 'run the agents against each instance; the only verb that spends money',
  mark: 'grade the saved patches with the dataset\u2019s judges',
  status: 'where every verb stands for the target \u2014 read-only',
  audit: 'prove the record is complete; incomplete records block analysis',
  analyse: 'write the target\u2019s figures to analysis/ and refresh the overview',
};

const printHelp = () => {
  console.log('usage: ./swe.mjs [verb...] [target...] [flags]   (any order \u2014 verbs \u00d7 targets)');
  console.log('');
  console.log('verbs (omit for status):');
  for (const [v, h] of Object.entries(VERB_HELP)) console.log(`  ${v.padEnd(8)} ${h}`);
  console.log('');
  console.log(`targets (omit for all combinations):`);
  console.log(`  combinations: ${listJson('combinations').join(', ')}`);
  console.log(`  datasets:     ${listJson('datasets').map((d) => {
    try {
      return `${d} (${Object.keys(loadDataset(d).selections).map((s) => `${d}/${s}`).join(', ')})`;
    } catch {
      return d;
    }
  }).join('; ')}`);
  console.log('');
  console.log('flags: --model <m>   with a combination: run/mark only its matching legs (substring)');
  console.log('       --model <m> --effort <e> --workers <n>   (ad-hoc runs without a combination)');
  console.log('');
  console.log('examples:');
  console.log('  ./swe.mjs                        the dashboard: status of every meet');
  console.log('  ./swe.mjs analyse                analyse everything');
  console.log('  ./swe.mjs analyse multilingual   just multilingual');
  console.log('  ./swe.mjs run mark audit pro     chain per target, in order');
};

const args = process.argv.slice(2);
const verbs = [];
const targetNames = [];
const flags = {};
while (args.length > 0) {
  const a = args.shift();
  if (a === '--help' || a === '-h' || a === 'help') {
    printHelp();
    process.exit(0);
  } else if (a.startsWith('--')) {
    flags[a.slice(2)] = args.shift();
  } else if (VERBS[a]) {
    verbs.push(a);
  } else {
    targetNames.push(a);
  }
}

// verbs × targets: either axis omitted means all of it
if (verbs.length === 0) verbs.push('status');
if (targetNames.length === 0) targetNames.push(...listJson('combinations').sort());

// validate every target up front — a typo should name the choices, not half-run
const targets = [];
for (const name of targetNames) {
  try {
    targets.push([name, loadTarget(name)]);
  } catch {
    console.error(`unknown target '${name}' \u2014 not a verb (${Object.keys(VERBS).join(' ')}) and not a target:`);
    console.error(`combinations: ${listJson('combinations').join(', ')}`);
    console.error(`datasets:     ${listJson('datasets').map((d) => {
      try {
        return `${d} (${Object.keys(loadDataset(d).selections).map((s) => `${d}/${s}`).join(', ')})`;
      } catch {
        return d;
      }
    }).join('; ')}`);
    console.error(`run './swe.mjs --help' for the full grammar`);
    process.exit(2);
  }
}

// Keep the machine awake for as long as this process lives. A sleeping host
// suspends the Docker VM under a run, and the harness does not fail — it waits
// forever on containers that no longer exist, progress bar frozen on its last
// frame.
//
// All three flags, because each covers a different way it sleeps and -s alone
// is not enough: -s holds system sleep but ONLY on mains power, so a run died
// after ten seconds on battery; -i holds idle sleep whatever the power source;
// -d keeps the display awake, which is what stops clamshell and idle-display
// sleep from taking the system with it. `-w` ties the reprieve to this pid, so
// it lifts on exit, crash or kill with no cleanup to forget.
// Spawned directly, not through `sh -c '... &'`: the shell exits 0 the moment
// it forks, so its status says nothing about caffeinate, and the rig printed
// "holding the machine awake" on a box where caffeinate had failed — the exact
// reassurance that makes a mid-run sleep baffling.
let awake = null;
if (process.platform === 'darwin') {
  try {
    awake = spawn('caffeinate', ['-dis', '-w', String(process.pid)],
      { stdio: 'ignore', detached: true });
    awake.on('error', (e) => {
      console.error(`[swe] caffeinate failed (${e.message}) — the machine may sleep mid-run`);
      awake = null;
    });
    awake.unref();
  } catch (e) {
    console.error(`[swe] caffeinate failed (${e.message}) — the machine may sleep mid-run`);
    awake = null;
  }
}
// The assertion, not the process: caffeinate can be running and still not
// holding, so ask the system what it thinks.
if (awake) {
  const held = spawnSync('pmset', ['-g', 'assertions'], { encoding: 'utf8' });
  const holding = /PreventSystemSleep\s+1/.test(held.stdout ?? '');
  console.log(holding
    ? '[swe] holding the machine awake while this runs'
    : '[swe] WARNING: sleep is NOT held — a mid-run sleep will hang the harness');
}
// Closing the lid still sleeps: no assertion overrides clamshell on battery,
// and on mains it needs an external display attached. Nothing here can fix
// that, so say it rather than let a lid-close look like a hang.
if (awake && verbs.some((v) => ['run', 'mark', 'ensure'].includes(v))) {
  console.log('[swe] leave the lid open — closing it sleeps regardless');
}

try {
  for (const [name, target] of targets) {
    if (targets.length > 1) console.log(`\n=== ${name} ===`);
    for (const verb of verbs) {
      await VERBS[verb](target, flags);
    }
  }
} catch (err) {
  console.error(`[swe] failed: ${err.message}`);
  process.exit(1);
}
