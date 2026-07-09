"""Draw the frozen SWE-bench Pro instance set: every TypeScript instance.

All 20 ts instances in the public Pro split are tutao/tutanota, so this is a
single-repo, single-language paper by construction. The set is the full ts
population (originally a seeded 10; expanded 2026-07-10 — a superset, so the
earlier runs stay valid). The output list is the frozen set and is committed
(same discipline as draw-instances.py).
"""

import json

rows = [json.loads(l) for l in open("datasets/swe-bench-pro.jsonl")]
ts = sorted(r["instance_id"] for r in rows if r["repo_language"] == "ts")

with open("instances-pro.txt", "w") as f:
    f.write("\n".join(ts) + "\n")
print(f"wrote {len(ts)} instance ids to instances-pro.txt")
