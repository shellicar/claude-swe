#!/usr/bin/env node
// Render an arm's tool description by filtering the tagged fragments of
// Anthropic's Claude Code Bash description. The fragments partition the raw
// capture byte-exactly, so `--verify` proves the artifact hasn't drifted
// from the recorded original, and every arm's description is an auditable
// filter expression instead of hand-edited prose.
//
//   node compose.mjs --verify
//   node compose.mjs --list
//   node compose.mjs --preset honest-cc
//   node compose.mjs --preset honest-cc --exclude-id state_profile_init
//   node compose.mjs --exclude-validity false_affordance,false_reference

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const artifact = JSON.parse(
  readFileSync(join(here, "anthropic-claude-code-bash.fragments.json"), "utf8"),
);
const raw = readFileSync(join(here, artifact.provenance.raw_file), "utf8");

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? (args[i + 1] ?? "") : null;
};
const csv = (name) => (flag(name) ?? "").split(",").filter(Boolean);

if (args.includes("--verify")) {
  const joined = artifact.fragments.map((f) => f.text).join("");
  if (joined === raw) {
    console.log(`OK: ${artifact.fragments.length} fragments recompose the raw capture byte-exactly`);
    process.exit(0);
  }
  console.error("FAIL: fragments do not recompose the raw capture");
  process.exit(1);
}

if (args.includes("--list")) {
  for (const f of artifact.fragments) {
    const preview = f.text.trim().replace(/\s+/g, " ").slice(0, 70);
    console.log(`${f.id.padEnd(24)} ${f.category.padEnd(24)} ${f.validity.padEnd(24)} ${preview}`);
  }
  process.exit(0);
}

const preset = flag("--preset");
const filters = { exclude_categories: [], exclude_ids: [], exclude_validities: [] };
// A preset may also REPLACE a fragment's text (e.g. the fresh arm states
// fresh semantics where the persistence sentence was) — the replacement
// lives in the artifact, so composed output stays auditable.
let replacements = {};
if (preset) {
  const p = artifact.presets[preset];
  if (!p) {
    console.error(`unknown preset ${preset}; have: ${Object.keys(artifact.presets).join(", ")}`);
    process.exit(2);
  }
  filters.exclude_categories.push(...(p.exclude_categories ?? []));
  filters.exclude_ids.push(...(p.exclude_ids ?? []));
  filters.exclude_validities.push(...(p.exclude_validities ?? []));
  replacements = p.replace_ids ?? {};
}
filters.exclude_categories.push(...csv("--exclude-category"));
filters.exclude_ids.push(...csv("--exclude-id"));
filters.exclude_validities.push(...csv("--exclude-validity"));

let included = artifact.fragments.filter(
  (f) =>
    !filters.exclude_categories.includes(f.category) &&
    !filters.exclude_ids.includes(f.id) &&
    !filters.exclude_validities.includes(f.validity),
);

// A structure header with no surviving content before the next header is
// itself dropped.
included = included.filter((f, i) => {
  if (f.category !== "structure") return true;
  for (const g of included.slice(i + 1)) {
    if (g.category === "structure") return false;
    return true;
  }
  return false;
});

const composed = included
  .map((f) => (f.id in replacements ? replacements[f.id] : f.text))
  .join("")
  .replace(/\n{3,}/g, "\n\n")
  .trim();
process.stdout.write(composed + "\n");
