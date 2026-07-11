"""The front page of analysis/: every dataset's headline on one card.

Grouped by dataset — that is how the results are looked up: SWE-bench
Verified, SWE-bench Pro, SWE-bench Multilingual, Multi-SWE-bench — with each
dataset's selections as rows and the union of models as columns. Two rows per
selection: resolved n (%) and $/resolved. Cells read "—" where a model never
ran that selection or it is not yet marked.

Reads the per-dataset analysis/<name>/data.json files (the machine layer each
analyser writes), so it can only ever be as stale as they are; swe.mjs
regenerates it after every analyse.

Outputs: analysis/overview/ (data.json, table.md, table.html, table.png).
"""

import json
import os

from analysis_output import emit

ROOT = os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = f"{ROOT}/analysis/{name}/data.json"
    return json.load(open(path)) if os.path.exists(path) else None


def cellpair(leg):
    """(resolved cell, $/resolved cell) from a leg dict; dashes when unknown."""
    if leg is None:
        return "—", "—"
    resolved = leg.get("resolved")
    n = leg.get("instances") or 0
    if resolved is None or not n:
        return "—", "—"
    # non-breaking space: a wrapped cell makes d2 under-measure the table and
    # clip its bottom (the Pro section lost rows to exactly this)
    res = f"{resolved}\u00a0({resolved / n * 100:.0f}%)"
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
    labels = {
        "rust (tokio-rs/tokio, 9 instances)": "rust: tokio (9)",
        "cpp (fmtlib/fmt, 11 instances)": "cpp: fmt (11)",
        "cpp variation (verify + 900s, same 11)": "cpp variation (11)",
    }
    for key, label in labels.items():
        yield label, {m: v.get(key) for m, v in d["models"].items()}


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
# per-column running totals over CONTROLS (variations revisit the same
# instances and would double-count them)
totals = {col: dict(resolved=0, instances=0, cost=0.0) for col in COLUMNS}
def total_cells(tot):
    res_cells = []
    cost_cells = []
    for col in COLUMNS:
        t = tot[col]
        if t["instances"]:
            res_cells.append(f"{t['resolved']}/{t['instances']}\u00a0({t['resolved'] / t['instances'] * 100:.0f}%)")
            cost_cells.append(f"${t['cost'] / t['resolved']:.2f}" if t["resolved"] else "—")
        else:
            res_cells.append("—")
            cost_cells.append("—")
    return res_cells, cost_cells


for title, name, rows_fn in DATASETS:
    d = load(name)
    if d is None:
        continue
    body = []
    ds_totals = {col: dict(resolved=0, instances=0, cost=0.0) for col in COLUMNS}
    for label, per_model in rows_fn(d):
        res_cells = []
        cost_cells = []
        for col in COLUMNS:
            leg = per_model.get(col)
            res, cost = cellpair(leg)
            res_cells.append(res)
            cost_cells.append(cost)
            if leg is not None:
                seen.add(col)
                if "variation" not in label and leg.get("resolved") is not None and leg.get("instances"):
                    for t in (totals[col], ds_totals[col]):
                        t["resolved"] += leg["resolved"]
                        t["instances"] += leg["instances"]
                        t["cost"] += leg.get("cost") or 0
        body.append((label, res_cells, cost_cells))
    # per-dataset total row (controls only, same rule as the grand total)
    res_cells, cost_cells = total_cells(ds_totals)
    body.append(("total", res_cells, cost_cells))
    sections.append((title, body))

total_res, total_cost = total_cells(totals)
sections.append(("TOTAL — all controls (variations excluded)", [("resolved / attempted", total_res, total_cost)]))

# Drop columns no dataset ever populated.
keep = [i for i, c in enumerate(COLUMNS) if c in seen]
cols = [COLUMNS[i] for i in keep]
for si, (title, body) in enumerate(sections):
    sections[si] = (title, [(l, [r[i] for i in keep], [c[i] for i in keep]) for l, r, c in body])

NOTE = "Resolved n (%) and cost per resolved, per selection. — = not run or not yet marked. Details per dataset in analysis/<dataset>/table.md."

# Flatten the (label, res, cost) triples into the emitter's (label, cells) rows.
emit_sections = []
for title, body in sections:
    flat = []
    for label, res, cost in body:
        flat.append((label.replace(" ", "\u00a0"), res))
        flat.append(("—\u00a0cost/resolved", cost))
    emit_sections.append((title, flat))

emit("overview", "claude-swe — all experiments", cols, emit_sections, NOTE,
     {"columns": cols, "sections": [
         {"dataset": title, "rows": [{"selection": l, "resolved": r, "cost_per_resolved": c} for l, r, c in body]}
         for title, body in sections]})
