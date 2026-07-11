"""The front page of analysis/: every dataset's headline on one card.

Grouped by dataset — that is how the results are looked up: SWE-bench
Verified, SWE-bench Pro, SWE-bench Multilingual, Multi-SWE-bench — with each
dataset's selections as rows and the union of models as columns. Two rows per
selection: resolved n (%) and $/resolved. Cells read "—" where a model never
ran that selection or it is not yet marked.

Reads the per-dataset analysis/*.json files (the machine layer each analyser
writes), so it can only ever be as stale as they are; swe.mjs regenerates it
after every analyse.

Outputs: analysis/overview.{md,html,png,svg} (+ .d2 intermediate).
"""

import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = f"{ROOT}/analysis/{name}.json"
    return json.load(open(path)) if os.path.exists(path) else None


def cellpair(leg):
    """(resolved cell, $/resolved cell) from a leg dict; dashes when unknown."""
    if leg is None:
        return "—", "—"
    resolved = leg.get("resolved")
    n = leg.get("instances") or 0
    if resolved is None or not n:
        return "—", "—"
    res = f"{resolved} ({resolved / n * 100:.0f}%)"
    cost = leg.get("cost") or 0
    return res, (f"${cost / resolved:.2f}" if resolved else "—")


# Each dataset adapter yields (selection label, {model short name: leg dict}).
def verified_rows(d):
    # verified.json predates the leg shape the others use: no 'instances' key,
    # the set sizes are implicit. Supply them.
    for sel, label, n in (("standard", "standard (60)", 60), ("hard", "hard (45)", 45)):
        yield label, {m: {**v["sets"][sel], "instances": n} for m, v in d["models"].items()}


def pro_rows(d):
    for sel, label in (("pro", "tutanota ts (20)"), ("nodebb", "NodeBB js (44)")):
        yield label, {m: v.get(sel) for m, v in d["models"].items()}


def multilingual_rows(d):
    for sel, label in (("rust", "rust: tokio (9)"), ("cpp", "cpp: fmt (11)")):
        yield label, {m: v.get(sel) for m, v in d["models"].items()}


def multi_rows(d):
    labels = {
        "cpp control": "cpp control (20)",
        "rust control": "rust control (20)",
        "cpp variation (verify + 900s)": "cpp variation (20)",
    }
    for key, label in labels.items():
        yield label, {m: v.get(key) for m, v in d["models"].items()}


DATASETS = [
    ("SWE-bench Verified", "verified", verified_rows),
    ("SWE-bench Pro", "pro", pro_rows),
    ("SWE-bench Multilingual", "multilingual", multilingual_rows),
    ("Multi-SWE-bench", "multi", multi_rows),
]

# Column order: the main-experiment models first, in the report's order.
COLUMNS = ["fable-5", "opus-4-8", "opus-4-7", "opus-4-6", "sonnet-4-6", "sonnet-5", "haiku-4-5"]

sections = []
seen = set()
for title, name, rows_fn in DATASETS:
    d = load(name)
    if d is None:
        continue
    body = []
    for label, per_model in rows_fn(d):
        res_cells = []
        cost_cells = []
        for col in COLUMNS:
            res, cost = cellpair(per_model.get(col))
            res_cells.append(res)
            cost_cells.append(cost)
            if per_model.get(col) is not None:
                seen.add(col)
        body.append((label, res_cells, cost_cells))
    sections.append((title, body))

# Drop columns no dataset ever populated.
keep = [i for i, c in enumerate(COLUMNS) if c in seen]
cols = [COLUMNS[i] for i in keep]
for si, (title, body) in enumerate(sections):
    sections[si] = (title, [(l, [r[i] for i in keep], [c[i] for i in keep]) for l, r, c in body])

# No '$' here: d2 parses $ inside quoted labels as a substitution and dies.
NOTE = "Resolved n (%) and cost per resolved, per selection. — = not run or not yet marked. Details per dataset in analysis/<dataset>.md."

# markdown
lines = ["| | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
for title, body in sections:
    lines.append(f"| **{title}** |" + " |" * len(cols))
    for label, res, cost in body:
        lines.append(f"| {label} | " + " | ".join(res) + " |")
        lines.append(f"| — $/resolved | " + " | ".join(cost) + " |")
lines += ["", NOTE]

# html
import html as html_mod
h = ["<!doctype html><meta charset='utf-8'><title>claude-swe overview</title>",
     "<style>body{background:#1b1b2b;color:#e8e8f0;font:14px -apple-system,sans-serif;padding:2em}",
     "table{border-collapse:collapse}td,th{border:1px solid #555;padding:.35em .8em;text-align:left}",
     "th{background:#2a2a3f}td.sec{background:#2a2a3f;font-weight:bold}td.sub{color:#9a9ab0}</style>",
     "<table><tr><th></th>" + "".join(f"<th>{html_mod.escape(c)}</th>" for c in cols) + "</tr>"]
for title, body in sections:
    h.append(f"<tr><td class='sec' colspan='{len(cols) + 1}'>{html_mod.escape(title)}</td></tr>")
    for label, res, cost in body:
        h.append("<tr><td>" + html_mod.escape(label) + "</td>" + "".join(f"<td>{html_mod.escape(c)}</td>" for c in res) + "</tr>")
        h.append("<tr><td class='sub'>— $/resolved</td>" + "".join(f"<td class='sub'>{html_mod.escape(c)}</td>" for c in cost) + "</tr>")
h.append(f"</table><p>{html_mod.escape(NOTE)}</p>")

# d2 — one md table per dataset section (the known measurement traps: split
# tables, one-line cells, sacrificial blank last row)
d2 = ["vars: { d2-config: { theme-id: 200 } }", "",
      'title: "claude-swe — all experiments" { near: top-center; shape: text; style.font-size: 22; style.bold: true }', ""]
prev = None
for idx, (title, body) in enumerate(sections):
    name = f"section{idx}"
    d2.append(f"{name}: |||md")
    d2.append(f"  | {title} | " + " | ".join(cols) + " |")
    d2.append("  |" + "---|" * (len(cols) + 1))
    for label, res, cost in body:
        d2.append(f"  | {label} | " + " | ".join(res) + " |")
        d2.append(f"  | $/resolved | " + " | ".join(cost) + " |")
    d2.append("  | " + " | " * (len(cols) + 1))
    d2.append("|||")
    if prev is not None:
        d2.append(f"{prev} -> {name}: {{style.opacity: 0}}")
    prev = name
d2.append(f'note: "{NOTE}" {{ near: bottom-center; shape: text; style.font-color: "#7F8C8D" }}')

os.makedirs(f"{ROOT}/analysis", exist_ok=True)
with open(f"{ROOT}/analysis/overview.md", "w") as f:
    f.write("\n".join(lines) + "\n")
with open(f"{ROOT}/analysis/overview.html", "w") as f:
    f.write("\n".join(h) + "\n")
with open(f"{ROOT}/analysis/overview.d2", "w") as f:
    f.write("\n".join(d2) + "\n")
wrote = "overview.md, overview.html, overview.d2"
if shutil.which("d2"):
    for ext in ("png", "svg"):
        subprocess.run(["d2", f"{ROOT}/analysis/overview.d2", f"{ROOT}/analysis/overview.{ext}"],
                       check=True, capture_output=True)
    wrote += ", overview.png, overview.svg"
print(f"wrote analysis/: {wrote}")
