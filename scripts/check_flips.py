#!/usr/bin/env python3
"""Did re-marking with the fixed harness change any verdict?

The old marker reset the whole working tree before grading any instance whose
test patch only adds files, destroying the model's patch first — so those
instances could never resolve. This compares each leg's current verdicts
against the versions committed before the re-mark.
"""
import json
import subprocess
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE = "sphinx-doc__sphinx-8595"


def committed(path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{path}"],
                       capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


flips = []
checked = 0
for report in sorted(glob.glob(os.path.join(ROOT, "evals", "*.json"))):
    rel = os.path.relpath(report, ROOT)
    now = json.load(open(report))
    was = committed(rel)
    if was is None:
        continue
    checked += 1
    gained = set(now.get("resolved_ids", [])) - set(was.get("resolved_ids", []))
    lost = set(was.get("resolved_ids", [])) - set(now.get("resolved_ids", []))
    if gained or lost:
        flips.append((rel, sorted(gained), sorted(lost)))

print(f"reports compared against their committed versions: {checked}")
print(f"reports whose verdicts changed: {len(flips)}\n")
for rel, gained, lost in flips:
    name = rel.split("/")[-1]
    if gained:
        print(f"  + RESOLVED now: {', '.join(gained)}\n      {name}")
    if lost:
        print(f"  - lost resolution: {', '.join(lost)}\n      {name}")

# And specifically the instance the bug made unwinnable.
holders = [r for r in glob.glob(os.path.join(ROOT, "evals", "*.json"))
           if INSTANCE in json.load(open(r)).get("resolved_ids", [])]
print(f"\nlegs now resolving {INSTANCE}: {len(holders)}")
for h in holders:
    print(f"   {os.path.basename(h)}")
