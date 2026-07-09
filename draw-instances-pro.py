"""Draw the frozen SWE-bench Pro instance set: 10 TypeScript instances.

All 20 ts instances in the public Pro split are tutao/tutanota, so this is a
single-repo, single-language paper by construction. Seeded so the draw is
reproducible from the committed dataset snapshot; the output list is the
frozen set and is committed (same discipline as draw-instances.py).
"""

import json
import random

rows = [json.loads(l) for l in open("datasets/swe-bench-pro.jsonl")]
ts = sorted(r["instance_id"] for r in rows if r["repo_language"] == "ts")

random.seed(42)
picked = sorted(random.sample(ts, 10))

with open("instances-pro.txt", "w") as f:
    f.write("\n".join(picked) + "\n")
print(f"wrote {len(picked)} instance ids to instances-pro.txt")
