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


def four_rows(per_column):
    """The standard Results block — Resolved, Resolved %, Total cost,
    $/resolved — from {column: (resolved, instances, cost) | None}. The
    labels match analysis_output.HEADLINE, so the emitter medals them."""
    def cell(col, fn):
        v = per_column.get(col)
        return fn(*v) if v else "—"
    return [
        ("Resolved", [cell(c, lambda r, n, _: f"{r}/{n}") for c in COLUMNS]),
        ("Resolved %", [cell(c, lambda r, n, _: f"{r / n * 100:.0f}%") for c in COLUMNS]),
        ("Total cost", [cell(c, lambda r, n, x: f"${x:.2f}") for c in COLUMNS]),
        ("$/resolved", [cell(c, lambda r, n, x: f"${x / r:.2f}" if r else "—") for c in COLUMNS]),
    ]


# Each dataset adapter yields (selection label, {model short name: leg dict}).
def verified_rows(d):
    # verified.json predates the leg shape the others use: no 'instances' key,
    # the set sizes are implicit. Supply them.
    for sel, label, n in (("standard", "standard — *Python* (60)", 60), ("hard", "hard — *Python* (45)", 45)):
        yield label, {m: {**v["sets"][sel], "instances": n} for m, v in d["models"].items()}


def pro_rows(d):
    for sel, label in (("pro", "tutanota — *TypeScript* (20)"), ("nodebb", "NodeBB — *JavaScript* (44)"), ("element", "element-web — *JavaScript* (20)"), ("go", "*Go* (25 of 280)")):
        yield label, {m: v.get(sel) for m, v in d["models"].items()}


def multilingual_rows(d):
    labels = {
        "*Rust* — 7 repos (43 events)": "*Rust* — 7 repos (43)",
        "fmtlib/fmt — *C++* (11 events)": "fmt — *C++* (11)",
        "*Go* — 5 repos (42 events)": "*Go* — 5 repos (42)",
    }
    for key, label in labels.items():
        yield label, {m: v.get(key) for m, v in d["models"].items()}


def multi_rows(d):
    labels = {
        "*C++* control": "*C++* control (20)",
        "*Rust* control": "*Rust* control (20)",
        "tokio stack — *Rust* (org tokio-rs)": "tokio stack — *Rust* (20)",
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
# Latest generation only — the lineages compete on their own cards
# The contenders, in roster order; columns with no data are pruned below.
COLUMNS = [m["dir"] for m in json.load(open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.json"),
))["models"] if m.get("contender")]

sections = []
seen = set()
# per-column running totals over CONTROLS (variations revisit the same
# instances and would double-count them)
totals = {col: None for col in COLUMNS}


def accumulate(tot, col, r, n, x):
    cur = tot.get(col)
    tot[col] = (r, n, x) if cur is None else (cur[0] + r, cur[1] + n, cur[2] + x)


for title, name, rows_fn in DATASETS:
    d = load(name)
    if d is None:
        continue
    body = []
    ds_totals = {col: None for col in COLUMNS}
    for label, per_model in rows_fn(d):
        per_column = {}
        for col in COLUMNS:
            leg = per_model.get(col)
            if leg is None:
                continue
            seen.add(col)
            r, n, x = leg.get("resolved"), leg.get("instances") or 0, leg.get("cost") or 0
            if r is None or not n:
                continue
            per_column[col] = (r, n, x)
            # No label sniffing: every row here is a program now. Experiments
            # live on their own cards, so there is nothing to exclude — the
            # old `"variation" not in label` test would have silently started
            # counting anything renamed.
            accumulate(ds_totals, col, r, n, x)
            accumulate(totals, col, r, n, x)
        body.append((f"## {label}", [""] * len(COLUMNS)))
        body.extend(four_rows(per_column))
    body.append(("## total", [""] * len(COLUMNS)))
    body.extend(four_rows(ds_totals))
    sections.append((title, body))

sections.append(("TOTAL — every meet", four_rows(totals)))

# Drop columns no dataset ever populated.
keep = [i for i, c in enumerate(COLUMNS) if c in seen]
cols = [COLUMNS[i] for i in keep]
sections = [(title, [(l, [cells[i] for i in keep]) for l, cells in body]) for title, body in sections]

NOTE = "Each meet's event programs, the Results block medalled per row. — = did not enter or unjudged. Full results per meet in analysis/<dataset>/table.md."

emit("overview", "claude-swe — all meets", cols, sections, NOTE,
     {"columns": cols, "sections": [
         {"dataset": title, "rows": [{"label": l, "cells": cells} for l, cells in body]}
         for title, body in sections]})
