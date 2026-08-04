#!/usr/bin/env python3
"""The coverage card: which model ran which meet at which configuration.

Generated from the declarations and the record, never hand-maintained — a
hand-written matrix is stale the moment a leg finishes. Rows are what a model
can be run against (each meet's selections, then each scaffolding arm);
columns are the contenders; every cell is a five-slot effort strip:

    low medium high xhigh max

    #  run and marked      ~  run, not yet marked      .  not run

`high` is the default-effort leg — the sweeps deliberately omit it rather than
running the same configuration twice, so a default-only cell reads `..#..`.
"""
import glob
import json
import os

import selections

ROOT = os.path.dirname(os.path.abspath(__file__))
LEVELS = ["low", "medium", "high", "xhigh", "max"]
GLYPH = {"marked": "#", "part": "½", "run": "~", "none": "."}

ROSTER = json.load(open(f"{ROOT}/models.json"))["models"]
COLUMNS = [m for m in ROSTER if m.get("contender")]
# A model's own ladder — a slot it cannot have is not a gap in coverage.
LEVELS_BY_MODEL = {m["dir"]: m.get("effortLevels", LEVELS) for m in ROSTER}


# Verdict locations, listed once: globbing per cell made this card take two
# minutes. swebench writes flat reports named <model>.runs_<out>_<sel>.json;
# the Scale and multi-swe markers write directories instead.
SWEBENCH_REPORTS = {f for f in os.listdir(f"{ROOT}/evals") if f.endswith(".json")}
MARKER_DIRS = set()
for sub in ("multi", "pro"):
    p = f"{ROOT}/evals/{sub}"
    if os.path.isdir(p):
        MARKER_DIRS |= {f"{sub}/{d}" for d in os.listdir(p)}


def leg_state(out, selection, expected=None):
    """none / run / part / marked for one leg × selection.

    A report EXISTING is not the same as a leg being fully graded: a scoped
    `--instance_ids` run rewrites the aggregate down to just those instances,
    and an interrupted mark leaves a partial one. Both used to read as `#`,
    which is how the card claimed complete coverage of work that was not.
    """
    if not glob.glob(f"{ROOT}/{out}/{selection}/*/*.traj.json"):
        return "none"
    # `out` is runs/<combo>/<leg>; the report id drops the runs/ prefix.
    rid = out.split("/", 1)[1].replace("/", "_")
    for f in SWEBENCH_REPORTS:
        if not f.endswith(f".runs_{rid}_{selection}.json"):
            continue
        if expected:
            d = json.load(open(f"{ROOT}/evals/{f}"))
            graded = d.get("completed_instances", 0) + d.get("empty_patch_instances", 0)
            if graded < expected:
                return "part"
        return "marked"
    combo, legdir = out.split("/")[1], out.split("/")[2]
    if any(d.endswith(f"/{combo}-{legdir}-{selection}") or d.endswith(f"/{legdir}-{selection}")
           or d == f"pro/{legdir}" for d in MARKER_DIRS):
        return "marked"
    return "run"


def combos():
    for f in sorted(glob.glob(f"{ROOT}/combinations/*.json")):
        d = json.load(open(f))
        ds = json.load(open(f"{ROOT}/datasets/{d['dataset']}.json"))
        yield d, ds


def kind_of(combo):
    """analysis/README.md's vocabulary. A MEET varies the contender: same events,
    same conditions, one column per model. An EXPERIMENT varies a condition and
    holds the contenders, comparing each against itself.

    An experiment says so in its combination file, rather than being recognised
    by a suffix in its name — the name is a label, and a rename would silently
    reclassify it."""
    if combo.get("experiment"):
        return "experiment"
    if combo["name"] in ("main", "effort-sweep") or combo["name"] == combo["dataset"]:
        return "meet"
    return "experiment"


# Every meet/program a contender could compete in, and every leg that exists
# for it, keyed by (contender, effort).
rows = {}   # (kind, label) -> {(model, effort): out}
for d, ds in combos():
    kind = kind_of(d)
    for leg in d["legs"]:
        model = leg["model"].split("/")[-1].replace("claude-", "")
        effort = leg.get("effort", "high")
        for sel in d["selections"]:
            # A meet's rows are named for the meet and its program; a fixture
            # or exhibition is named for itself, since that IS the variable.
            label = f"{d['dataset']}/{sel}" if kind == "meet" else f"{d['name']}/{sel}"
            # The dataset travels with the row: the label alone cannot say
            # which meet a fixture's selection belongs to.
            rows.setdefault((kind, label, d["dataset"]), {})[(model, effort)] = leg["out"]




def strip_for(model, legs, dataset, selection):
    """One model's five effort slots for a row. A level the model does not have
    is a space, not a gap: absence of a rung is not missing work."""
    mine = LEVELS_BY_MODEL[model["dir"]]
    out = ""
    for lv in LEVELS:
        if lv not in mine:
            out += " "
            continue
        leg_out = legs.get((model["dir"], lv))
        out += (GLYPH[leg_state(leg_out, selection, selections.expected(dataset, selection))]
                if leg_out else GLYPH["none"])
    return out


ORDER = {"meet": 0, "experiment": 1}
bodies = {k: [] for k in ORDER}
for (kind, label, dataset), legs in sorted(rows.items(),
                                          key=lambda kv: (ORDER[kv[0][0]], kv[0][1])):
    selection = label.split("/")[-1]
    cells = [f"`{strip_for(m, legs, dataset, selection)}`" for m in COLUMNS]
    bodies[kind].append((label, cells))

columns = [m["dir"] for m in COLUMNS]
heading = "Coverage — contender × meet × effort"
lines = [f"| {heading} | " + " | ".join(columns) + " |",
         "|" + "---|" * (len(columns) + 1)]
for title, body in (("Meets — the contender varies", bodies["meet"]),
                    ("Experiments — a condition varies, contenders held",
                     bodies["experiment"])):
    if not body:
        continue
    # Repeat the column names per section, so a section reads on its own.
    lines.append(f"| **{title}** | " + " | ".join(f"**{c}**" for c in columns) + " |")
    for label, cells in body:
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
lines.append(f"| **Legend** |" + " |" * len(columns))
lines.append(f"| effort slots: low medium high xhigh max | "
             + " | ".join(["`#` marked", "`½` partly marked", "`~` run, unmarked",
                           "`.` not run"]
                          + [""] * (len(columns) - 4)) + " |")

outdir = f"{ROOT}/analysis/coverage"
os.makedirs(outdir, exist_ok=True)
with open(f"{outdir}/table.html", "w") as f:
    f.write("\n".join(lines) + "\n")
# The same strips the table renders, so the machine layer cannot disagree with
# it — it previously recorded "." (not run) for levels a model does not have,
# showing gaps that were not gaps.
payload = {"levels": LEVELS, "columns": columns,
           "legend": {v: k for k, v in GLYPH.items()} | {" ": "model has no such level"},
           "rows": {label: {m["dir"]: list(strip_for(m, legs, dataset,
                                                     label.split("/")[-1]))
                            for m in COLUMNS}
                    for (_k, label, dataset), legs in rows.items()}}
with open(f"{outdir}/data.json", "w") as f:
    json.dump(payload, f, indent=2)
print("wrote analysis/coverage/: data.json, table.html")
