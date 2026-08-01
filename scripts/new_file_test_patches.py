#!/usr/bin/env python3
"""Which instances does the pinned marker grade unwinnably?

swebench #518: make_eval_script_list_py resets test files with

    git checkout {base_commit} {' '.join(get_modified_files(test_patch))}

but get_modified_files() EXCLUDES files whose source is /dev/null — new files.
So a test patch that only ADDS files yields an empty list, and the command
degrades to a bare `git checkout {base_commit}`, which resets the whole working
tree — wiping the model's patch before the tests run. Those instances cannot be
resolved by any patch under the pinned marker.

This lists them, and whether anything has ever resolved them here.
"""
import glob
import json
import re

SNAPSHOT = "datasets/swe-bench-verified.jsonl"
SELECTIONS = {s: {l.strip() for l in open(f"instances-{s}.txt") if l.strip()}
              for s in ("standard", "hard")}

# A file in a unified diff whose source side is /dev/null is newly added.
FILE_HEADER = re.compile(r"^--- (\S+)", re.M)


def only_new_files(test_patch):
    sources = FILE_HEADER.findall(test_patch or "")
    return bool(sources) and all(s == "/dev/null" for s in sources)


affected = []
for line in open(SNAPSHOT):
    row = json.loads(line)
    iid = row["instance_id"]
    where = next((s for s, ids in SELECTIONS.items() if iid in ids), None)
    if where and only_new_files(row.get("test_patch", "")):
        affected.append((where, iid))

print(f"instances in our selections whose test patch ONLY adds files: {len(affected)}")
for where, iid in affected:
    resolved_by = []
    for rep in glob.glob(f"evals/*_{where}.json"):
        try:
            d = json.load(open(rep))
        except Exception:
            continue
        if iid in d.get("resolved_ids", []):
            resolved_by.append(rep.split("/")[-1].split(".")[0])
    print(f"  {where:9} {iid:34} resolved by: {len(resolved_by)} leg(s)")
