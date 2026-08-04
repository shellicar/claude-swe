#!/usr/bin/env python3
"""One card per experiment: the same contenders, one condition changed.

A meet varies the contender, so its columns are models. An experiment varies
the CONDITION and holds the contenders, so its columns are the conditions —
control and variation — and there is one table per contender, because the
comparison is each contender against itself.

Everything else is the meet's card. The rows are the meet analyser's own rows
and the figures come from its own `leg`, so an experiment is read exactly like
the contest it varies: same metrics, same definitions, same shape. A card
invented for the occasion carries different numbers and cannot be compared
with anything.

An experiment declares itself in its combination file:

    "experiment": { "control": "multi" }
"""
import glob
import importlib.util
import json
import os

import analysis_output
import selections

ROOT = os.path.dirname(os.path.abspath(__file__))
ROSTER = json.load(open(f"{ROOT}/models.json"))["models"]
NAME = {m["dir"]: m["name"] for m in ROSTER}


def meet_analyser(dataset):
    """The analyser that builds this meet's card, imported for its `leg` and
    `rows` — hyphenated filenames are not importable by name."""
    path = f"{ROOT}/analyse-{dataset}.py"
    spec = importlib.util.spec_from_file_location(f"meet_{dataset}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decls(dataset, combo, sel, expected):
    """The meet analyser's own leg declaration, pointed at one combination."""
    if dataset == "multi":
        return dict(sel=sel, runs=f"runs/{combo}/{{m}}/{sel}",
                    evals=f"evals/multi/{combo}-{{m}}-{sel}")
    return dict(sel=sel, runs=f"runs/{combo}",
                runid=f"runs_{combo}", expected=expected)


def meet_rows(meet, expected):
    """The meet's rows. Some analysers define them at module level, others
    build them per section because a row needs the selection's size."""
    if hasattr(meet, "rows"):
        return meet.rows
    return meet.make_rows(expected)


def instance_tally(dataset, sel, legs, ids):
    """Per instance, which condition resolved it — and where both did, which did
    it cheaper. Resolving is the entry ticket, so a condition that failed an
    instance cannot place on it however cheap it was."""
    per = {}
    for combo, model in legs:
        resolved = verdicts(dataset, combo, model, sel) or set()
        costs = {}
        for tf in glob.glob(f"{ROOT}/runs/{combo}/{model}/{sel}/*/*.traj.json"):
            iid = os.path.basename(os.path.dirname(tf))
            if iid in ids:
                costs[iid] = json.load(open(tf))["info"]["model_stats"]["instance_cost"]
        per[combo] = (resolved, costs)
    counts = {combo: [0, 0, 0] for combo, _m in legs}
    unsolved = 0
    for iid in sorted(ids):
        finishers = sorted((per[c][1].get(iid, 0.0), c) for c, _m in legs
                           if iid in per[c][0])
        if not finishers:
            unsolved += 1
            continue
        for rank, (_cost, combo) in enumerate(finishers[:3]):
            counts[combo][rank] += 1
    return counts, unsolved, len(ids)


def verdicts(dataset, combo, model, sel):
    """resolved_ids for one leg, in the shape its marker stores them."""
    marker = json.load(open(f"{ROOT}/datasets/{dataset}.json"))["marker"]["type"]
    if marker == "multi-swe":
        path = f"{ROOT}/evals/{dataset}/{combo}-{model}-{sel}/final_report.json"
        if not os.path.exists(path):
            return None
        return {multi_id(i) for i in json.load(open(path))["resolved_ids"]}
    reports = glob.glob(f"{ROOT}/evals/*.runs_{combo}_{model}_{sel}.json")
    return set(json.load(open(reports[0]))["resolved_ids"]) if reports else None


def multi_id(instance_id):
    """multi-swe names an instance `org/repo:pr-N`; the instance files and run
    directories name the same thing `org__repo-N`."""
    repo, _, pr = instance_id.partition(":pr-")
    return f"{repo.replace('/', '__')}-{pr}" if pr else instance_id


def card(exp):
    spec = exp["experiment"]
    control = spec["control"]
    dataset = exp["dataset"]
    meet = meet_analyser(dataset)
    models = [l["out"].split("/")[-1] for l in exp["legs"]]

    # One card, one table per contender: the experiment is a single result, and
    # splitting it across files means holding three of them side by side to
    # read one answer.
    sections = []
    figures = {}
    tallies = {}
    for model in models:
        for sel in exp["selections"]:
            body = []
            expected = selections.expected(dataset, sel)
            legs = {
                "control": meet.leg(model, decls(dataset, control, sel, expected)),
                "variation": meet.leg(model, decls(dataset, exp["name"], sel, expected)),
            }
            for label, render in meet_rows(meet, expected):
                body.append((label, [render(legs[c]) for c in ("control", "variation")]))
            title = f"{NAME.get(model, model)} — {sel}, {expected} events"
            sections.append((title, body))
            figures.setdefault(model, {})[sel] = legs
            # This contender against itself, per instance: the tally belongs to
            # this result table alone.
            tallies[title] = instance_tally(
                dataset, sel, [(control, model), (exp["name"], model)],
                selections.ids(dataset, sel))

    analysis_output.emit(
        f"experiment-{exp['name']}",
        f"{exp['name']} — control against variation",
        ["control", "variation"], sections,
        f"Control: {control}.",
        {"covers": exp["selections"], "experiment": spec,
         "control": control, "contenders": figures},
        medals_by_section=tallies,
    )


for path in sorted(glob.glob(f"{ROOT}/combinations/*.json")):
    combo = json.load(open(path))
    if combo.get("experiment"):
        card(combo)
