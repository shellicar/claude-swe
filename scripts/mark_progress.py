#!/usr/bin/env python3
"""Marking progress in INSTANCES, across every marker.

A leg is 20-105 instances, so counting legs says nothing about how far through
the work is. And the three markers leave their per-instance evidence in three
different places, so counting only swebench's log directories reports a frozen
number through hours of healthy multi-swe work:

    swebench    evals/logs/run_evaluation/<run_id>/<model>/<instance>/
    multi-swe   evals/logs/multi-swe/<leg>/workdir/<org>/<repo>/evals/pr-N/
    scale       evals/pro/<leg>/instance_<id>/
"""
import glob
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MARKERS = {}
for f in glob.glob("datasets/*.json"):
    ds = json.load(open(f))
    MARKERS[ds["name"]] = ds["marker"]["type"]

DATASET_OF = {}
for f in glob.glob("combinations/*.json"):
    combo = json.load(open(f))
    DATASET_OF[combo["name"]] = combo["dataset"]


def graded_swebench(rid):
    return len(glob.glob(f"evals/logs/run_evaluation/{rid}/*/*"))


def graded_multi_swe(combo, model, sel):
    # From the VERDICT, not the scratch directory. Scratch is the harness's
    # working state: its key changed when the control/variation collision was
    # fixed, and the existing directories cannot be migrated because the old
    # key is precisely what made two legs indistinguishable. The verdict is the
    # record, is keyed per leg, and survives the harness's internals changing.
    path = f"evals/{DATASET_OF.get(combo, 'multi')}/{combo}-{model}-{sel}/final_report.json"
    if not os.path.exists(path):
        return 0
    d = json.load(open(path))
    return d.get("completed_instances", 0) + d.get("empty_patch_instances", 0)


def graded_scale(model, sel):
    suffix = "" if sel == "pro" else f"-{sel}"
    return len(glob.glob(f"evals/pro/{model}{suffix}/instance_*"))


total = graded = 0
by_marker = {}
for preds in sorted(glob.glob("runs/*/*/*/preds.json")):
    _runs, combo, model, sel = preds.split("/")[:4]
    n = len(json.load(open(preds)))
    marker = MARKERS.get(DATASET_OF.get(combo, "verified"), "swebench")
    if marker == "swebench":
        done = graded_swebench(f"runs_{combo}_{model}_{sel}")
    elif marker == "multi-swe":
        done = graded_multi_swe(combo, model, sel)
    else:
        done = graded_scale(model, sel)
    done = min(done, n)
    total += n
    graded += done
    if done < n:
        left = by_marker.setdefault(marker, {"instances": 0, "legs": 0})
        left["instances"] += n - done
        left["legs"] += 1

print(f"instances graded   {graded} / {total}   ({100 * graded / total:.0f}%)")
for marker, left in sorted(by_marker.items()):
    print(f"  {marker:10} {left['instances']:>5} left across {left['legs']} legs")

recent = [p for p in glob.glob("evals/**/*", recursive=True)
          if os.path.isfile(p) and time.time() - os.path.getmtime(p) < 600]
print(f"\nwritten last 10min {len(recent)}")
if recent:
    newest = max(recent, key=os.path.getmtime)
    print(f"newest             {time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(newest)))}"
          f"  {newest.split('/evals/')[-1]}")
