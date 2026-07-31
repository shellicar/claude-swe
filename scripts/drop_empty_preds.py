#!/usr/bin/env python3
"""Drop empty-patch entries from a leg's preds.json so `run` redoes them.

Resume skips whatever is keyed in preds.json (mini-swe-agent's swebench.py),
so an instance that died with RateLimitError and no patch is treated as
complete forever. Removing just those keys is what makes it re-runnable;
trajectories need no touching, since the harness unlinks the old one when it
reprocesses an instance.

    python scripts/drop_empty_preds.py runs/effort-sweep/fable-5-max
"""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
for preds in sorted(base.glob("*/preds.json")):
    data = json.loads(preds.read_text())
    empty = [k for k, v in data.items() if not (v.get("model_patch") or "").strip()]
    for k in empty:
        del data[k]
    preds.write_text(json.dumps(data, indent=2))
    print(f"{preds}: dropped {len(empty)}, kept {len(data)}")
