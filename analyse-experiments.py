#!/usr/bin/env python3
"""One card per experiment: the same contenders, one condition changed.

A meet varies the contender, so its columns are models and a podium means
something. An experiment varies the CONDITION and holds the contenders, so the
comparison is each contender against itself — control against variation, on the
same events. Columns are still the contenders, but the rows beneath each metric
are control / variation / delta, which puts the two numbers that answer the
question side by side in one column.

Putting an experiment inside a meet's card, as these used to be, loses exactly
that: the pairing is split across sections and the numbers join a podium that
was never the question.

An experiment declares itself in its combination file:

    "experiment": { "control": "multi", "question": "...", "varies": "..." }
"""
import glob
import json
import os

import analysis_output

ROOT = os.path.dirname(os.path.abspath(__file__))
ROSTER = json.load(open(f"{ROOT}/models.json"))["models"]
NAME = {m["dir"]: m["name"] for m in ROSTER}


def combos():
    for path in sorted(glob.glob(f"{ROOT}/combinations/*.json")):
        yield json.load(open(path))


def multi_id(instance_id):
    """multi-swe names an instance `org/repo:pr-N`; the instance files and run
    directories name the same thing `org__repo-N`. Comparing the two forms
    directly intersects to nothing, which renders as a leg that resolved
    zero — indistinguishable from a leg that genuinely failed everything."""
    repo, _, pr = instance_id.partition(":pr-")
    return f"{repo.replace('/', '__')}-{pr}" if pr else instance_id


def verdicts(marker, dataset, combo, model, sel):
    """resolved_ids for one leg. Each marker stores them its own way — guessing
    a path returns nothing and renders as "unmarked", which reads like missing
    work rather than a lookup bug."""
    if marker == "multi-swe":
        path = f"{ROOT}/evals/{dataset}/{combo}-{model}-{sel}/final_report.json"
        if os.path.exists(path):
            return {multi_id(i) for i in json.load(open(path))["resolved_ids"]}
        return None
    reports = glob.glob(f"{ROOT}/evals/*.runs_{combo}_{model}_{sel}.json")
    if len(reports) > 1:
        raise SystemExit(f"{combo}/{model}/{sel}: {len(reports)} reports match")
    return set(json.load(open(reports[0]))["resolved_ids"]) if reports else None


def leg_figures(runs_dir, ids, resolved_ids):
    """Resolved and cost for one leg, scoped to the declared instances."""
    cost = 0.0
    seen = 0
    for tf in glob.glob(f"{ROOT}/{runs_dir}/*/*.traj.json"):
        if os.path.basename(os.path.dirname(tf)) not in ids:
            continue
        seen += 1
        cost += json.load(open(tf))["info"]["model_stats"]["instance_cost"]
    resolved = None if resolved_ids is None else len(resolved_ids & ids)
    return {"resolved": resolved, "cost": cost, "instances": seen}


def card(exp):
    spec = exp["experiment"]
    control = spec["control"]
    ds = json.load(open(f"{ROOT}/datasets/{exp['dataset']}.json"))
    sections = []

    for sel in exp["selections"]:
        ids = {l.strip() for l in open(f"{ROOT}/{ds['selections'][sel]['file']}")
               if l.strip()}
        models = [l["out"].split("/")[-1] for l in exp["legs"]]
        marker = ds["marker"]["type"]
        pairs = {}
        for m in models:
            pairs[m] = {
                "control": leg_figures(
                    f"runs/{control}/{m}/{sel}", ids,
                    verdicts(marker, exp["dataset"], control, m, sel)),
                "variation": leg_figures(
                    f"runs/{exp['name']}/{m}/{sel}", ids,
                    verdicts(marker, exp["dataset"], exp["name"], m, sel)),
            }

        def row(label, fn):
            return (label, [fn(pairs[m]) for m in models])

        def fmt_resolved(p, which):
            v = p[which]["resolved"]
            return f"{v}/{len(ids)}" if v is not None else "unmarked"

        def delta(p, key):
            a, b = p["control"][key], p["variation"][key]
            if a is None or b is None:
                return "—"
            d = b - a
            return f"{d:+}" if isinstance(d, int) else f"{d:+.2f}"

        body = [
            ("## Resolved", []),
            row("control", lambda p: fmt_resolved(p, "control")),
            row("variation", lambda p: fmt_resolved(p, "variation")),
            row("delta", lambda p: delta(p, "resolved")),
            ("## Cost", []),
            row("control", lambda p: f"${p['control']['cost']:.2f}"),
            row("variation", lambda p: f"${p['variation']['cost']:.2f}"),
            row("delta", lambda p: f"${delta(p, 'cost')}".replace("$-", "-$").replace("$+", "+$")),
        ]
        sections.append((f"{sel} — {len(ids)} events", body))

    columns = [NAME.get(l["out"].split("/")[-1], l["out"].split("/")[-1])
               for l in exp["legs"]]
    note = f"{spec['question']} Varies: {spec['varies']}. Control: {control}."
    analysis_output.emit(
        f"experiment-{exp['name']}",
        f"Experiment — {exp['name']} (control: {control})",
        columns, sections, note,
        {"covers": exp["selections"], "experiment": spec,
         "models": {m: {} for m in columns}},
    )


for combo in combos():
    if combo.get("experiment"):
        card(combo)
