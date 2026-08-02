#!/usr/bin/env python3
"""Marking progress in INSTANCES — the unit that takes the time.

A leg is 20-105 instances, so counting legs says nothing about how far through
the work is.
"""
import glob
import json
import os
import time

total = graded = 0
for preds in glob.glob("runs/*/*/*/preds.json"):
    n = len(json.load(open(preds)))
    total += n
    leg = "/".join(preds.split("/")[1:3])
    sel = preds.split("/")[3]
    rid = f"runs_{leg.replace('/', '_')}_{sel}"
    graded += len(glob.glob(f"evals/logs/run_evaluation/{rid}/*/*"))

recent = [p for p in glob.glob("evals/**/*", recursive=True)
          if os.path.isfile(p) and time.time() - os.path.getmtime(p) < 600]
newest = max((os.path.getmtime(p), p) for p in glob.glob("evals/**/*", recursive=True)
             if os.path.isfile(p))

# What is left, by marker: swebench resumes and skips what is already graded,
# so its legs fly; multi-swe and Scale re-evaluate every instance from scratch
# and build per instance, so they dominate the remaining time.
remaining = {}
for ds_file in glob.glob("datasets/*.json"):
    ds = json.load(open(ds_file))
    remaining[ds["name"]] = ds["marker"]["type"]

by_marker = {}
for preds in glob.glob("runs/*/*/*/preds.json"):
    n = len(json.load(open(preds)))
    leg = "/".join(preds.split("/")[1:3])
    sel = preds.split("/")[3]
    rid = f"runs_{leg.replace('/', '_')}_{sel}"
    done = len(glob.glob(f"evals/logs/run_evaluation/{rid}/*/*"))
    if done >= n:
        continue
    combo = preds.split("/")[1]
    ds_name = json.load(open(f"combinations/{combo}.json"))["dataset"] \
        if os.path.exists(f"combinations/{combo}.json") else "verified"
    marker = remaining.get(ds_name, "?")
    by_marker[marker] = by_marker.get(marker, 0) + (n - done)

print(f"instances graded   {graded} / {total}")
print("remaining by marker", by_marker)
print(f"written last 10min {len(recent)}")
print(f"newest             {time.strftime('%H:%M:%S', time.localtime(newest[0]))}"
      f"  {newest[1].split('/evals/')[-1]}")
