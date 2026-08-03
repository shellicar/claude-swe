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

    "experiment": { "control": "multi", "question": "...", "varies": "..." }
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


def card(exp):
    spec = exp["experiment"]
    control = spec["control"]
    dataset = exp["dataset"]
    meet = meet_analyser(dataset)
    models = [l["out"].split("/")[-1] for l in exp["legs"]]

    for model in models:
        sections = []
        figures = {}
        for sel in exp["selections"]:
            body = []
            expected = selections.expected(dataset, sel)
            legs = {
                "control": meet.leg(model, decls(dataset, control, sel, expected)),
                "variation": meet.leg(model, decls(dataset, exp["name"], sel, expected)),
            }
            for label, render in meet_rows(meet, expected):
                body.append((label, [render(legs[c]) for c in ("control", "variation")]))
            sections.append((f"{sel} — {expected} events", body))
            figures[sel] = legs

        analysis_output.emit(
            f"experiment-{exp['name']}-{model}",
            f"{NAME.get(model, model)} — {exp['name']} experiment",
            ["control", "variation"], sections,
            f"{spec['question']} Varies: {spec['varies']}. Control: {control}.",
            {"covers": exp["selections"], "experiment": spec,
             "control": control, "contender": model, "sets": figures},
        )


for path in sorted(glob.glob(f"{ROOT}/combinations/*.json")):
    combo = json.load(open(path))
    if combo.get("experiment"):
        card(combo)
