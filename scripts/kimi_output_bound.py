#!/usr/bin/env python3
"""Is Kimi honouring our output bound, or its own default?

litellm translates max_completion_tokens into max_tokens for Moonshot, so the
parameter Kimi documents as authoritative never reaches it. Kimi accepts the
request either way (no error), which proves nothing about whether the bound is
applied — but the completions do: if any response exceeds our 32k, max_tokens
was ignored and the model was running to its own default (131072 for K3).
"""
import glob
import json

BOUND = 32000

for log in sorted(glob.glob("runs/**/kimi*/api-timing.jsonl", recursive=True)
                  + glob.glob("runs/**/*kimi*/api-timing.jsonl", recursive=True)):
    seen = set()
    if log in seen:
        continue
    biggest = 0
    over = 0
    n = 0
    lengths = 0
    for line in open(log):
        d = json.loads(line)
        u = d.get("usage") or {}
        out = u.get("completion_tokens") or u.get("output_tokens") or 0
        if not out:
            continue
        n += 1
        biggest = max(biggest, out)
        if out > BOUND:
            over += 1
        if d.get("stop_reason") == "length":
            lengths += 1
    if n:
        print(f"{log}")
        print(f"   calls={n} largest completion={biggest} over {BOUND}: {over}"
              f"  finish_reason=length: {lengths}")
