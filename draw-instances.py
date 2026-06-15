"""Frozen instance selection for the Opus 4.8 vs Fable 5 experiment.

Hard set: census — every instance rated over an hour. No sampling.
Standard set: 60 from the under-an-hour band, stratified by difficulty x repo
(proportional quotas, largest-remainder rounding), seeded draw within cells.

Re-running this script always reproduces the same lists (SEED below).
"""

import random
from collections import Counter, defaultdict

from datasets import load_dataset

SEED = 42
STANDARD_N = 60
HARD_BUCKETS = {"1-4 hours", ">4 hours"}

ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")

hard = sorted(i["instance_id"] for i in ds if i["difficulty"] in HARD_BUCKETS)

standard_pool = [i for i in ds if i["difficulty"] not in HARD_BUCKETS]
cells = defaultdict(list)
for i in standard_pool:
    cells[(i["difficulty"], i["repo"])].append(i["instance_id"])

total = len(standard_pool)
# Proportional quotas with largest-remainder rounding to exactly STANDARD_N.
exact = {k: len(v) * STANDARD_N / total for k, v in cells.items()}
quota = {k: int(e) for k, e in exact.items()}
remainder = sorted(exact, key=lambda k: exact[k] - quota[k], reverse=True)
for k in remainder[: STANDARD_N - sum(quota.values())]:
    quota[k] += 1

rng = random.Random(SEED)
standard = []
for k in sorted(cells):  # deterministic cell order
    standard.extend(rng.sample(sorted(cells[k]), quota[k]))
standard.sort()

with open("instances-hard.txt", "w") as f:
    f.write("\n".join(hard) + "\n")
with open("instances-standard.txt", "w") as f:
    f.write("\n".join(standard) + "\n")

print(f"hard: {len(hard)} (census)")
print(f"standard: {len(standard)} (seed={SEED})")
print("\nstandard composition (difficulty x repo -> drawn/available):")
for k in sorted(cells, key=lambda k: -len(cells[k])):
    if quota[k]:
        print(f"  {k[0]:>15} | {k[1]:<28} {quota[k]}/{len(cells[k])}")
dropped = [k for k in sorted(cells) if not quota[k]]
print(f"\ncells rounded to zero: {[f'{k[1]} {k[0]}' for k in dropped]}")
print("\nhard composition (repo -> count):")
for r, c in Counter(i.split("__")[0] for i in hard).most_common():
    print(f"  {r}: {c}")
