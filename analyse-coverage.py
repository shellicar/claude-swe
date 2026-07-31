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

ROOT = os.path.dirname(os.path.abspath(__file__))
LEVELS = ["low", "medium", "high", "xhigh", "max"]
GLYPH = {"marked": "#", "run": "~", "none": "."}

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


def leg_state(out, selection):
    """none / run / marked for one leg × selection."""
    if not glob.glob(f"{ROOT}/{out}/{selection}/*/*.traj.json"):
        return "none"
    # `out` is runs/<combo>/<leg>; the report id drops the runs/ prefix.
    rid = out.split("/", 1)[1].replace("/", "_")
    if any(f.endswith(f".runs_{rid}_{selection}.json") for f in SWEBENCH_REPORTS):
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


def kind_of(fixture):
    """analysis/README.md's vocabulary: a MEET is a dataset with its own judges
    and program (its primary contest, whose legs differ only by contender or
    effort); a VARIATION is an exhibition — same program, altered rules, off
    the medal table; everything else is a FIXTURE testing scaffolding or
    tools rather than a contender."""
    if fixture["name"].endswith("-variation"):
        return "variation"
    if fixture["name"] in ("main", "effort-sweep") or fixture["name"] == fixture["dataset"]:
        return "meet"
    return "fixture"


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
            rows.setdefault((kind, label), {})[(model, effort)] = leg["out"]

ORDER = {"meet": 0, "variation": 1, "fixture": 2}
bodies = {k: [] for k in ORDER}
for (kind, label), legs in sorted(rows.items(), key=lambda kv: (ORDER[kv[0][0]], kv[0][1])):
    cells = []
    selection = label.split("/")[-1]
    for m in COLUMNS:
        mine = LEVELS_BY_MODEL[m["dir"]]
        strip = ""
        for lv in LEVELS:
            if lv not in mine:
                strip += " "  # the model has no such level; not a gap
                continue
            out = legs.get((m["dir"], lv))
            strip += GLYPH[leg_state(out, selection)] if out else GLYPH["none"]
        cells.append(f"`{strip}`")
    bodies[kind].append((label, cells))

columns = [m["dir"] for m in COLUMNS]
heading = "Coverage — contender × meet × effort"
lines = [f"| {heading} | " + " | ".join(columns) + " |",
         "|" + "---|" * (len(columns) + 1)]
for title, body in (("Meets — contenders on the medal table", bodies["meet"]),
                    ("Exhibitions — variations, off the medal table", bodies["variation"]),
                    ("Fixtures — scaffolding and tools, not contenders", bodies["fixture"])):
    if not body:
        continue
    lines.append(f"| **{title}** |" + " |" * len(columns))
    for label, cells in body:
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
lines.append(f"| **Legend** |" + " |" * len(columns))
lines.append(f"| effort slots: low medium high xhigh max | "
             + " | ".join(["`#` marked", "`~` run, unmarked", "`.` not run"]
                          + [""] * (len(columns) - 3)) + " |")

outdir = f"{ROOT}/analysis/coverage"
os.makedirs(outdir, exist_ok=True)
with open(f"{outdir}/table.md", "w") as f:
    f.write("\n".join(lines) + "\n")
payload = {"levels": LEVELS, "columns": columns,
           "rows": {label: {m["dir"]: [
               GLYPH[leg_state(legs[(m["dir"], lv)], label.split("/")[-1])]
               if (m["dir"], lv) in legs else GLYPH["none"] for lv in LEVELS]
               for m in COLUMNS} for (_k, label), legs in rows.items()}}
with open(f"{outdir}/data.json", "w") as f:
    json.dump(payload, f, indent=2)
print("wrote analysis/coverage/: data.json, table.md")
