"""Aggregate the SWE-bench Pro pilot into files under analysis/.

Same conventions as analyse.py. Verdicts come from the vendored Scale harness
(`node eval-experiment.mjs mark-pro`); when a model has no eval_results.json
yet, its resolve cells read "—" rather than pretending.

Sources, per model:
- resolved       : evals/pro/<model>/eval_results.json ({instance_id: bool})
- cost/steps/tok : trajectories runs/pro/<model>/pro/*/*.traj.json
- thinking       : the leg's own wire capture runs/pro/<model>/api-timing.jsonl
- empty patches  : submissions with no diff (automatic unresolved)

Outputs: analysis/pro.json (raw figures), analysis/pro.md (table).
analysis/ is derived figures; evals/ is raw verdicts — kept apart on purpose.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


def leg(model_dir):
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    empty = 0
    trajs = sorted(glob.glob(f"{ROOT}/runs/pro/{model_dir}/pro/*/*.traj.json"))
    for tf in trajs:
        t = json.load(open(tf))
        info = t["info"]
        st = info["model_stats"]
        cost += st["instance_cost"]
        steps += st["api_calls"]
        if not (info.get("submission") or "").strip():
            empty += 1
        prev = None
        for m in t["messages"]:
            ts = m.get("extra", {}).get("timestamp")
            if m.get("role") == "assistant":
                u = (m.get("extra", {}).get("response") or {}).get("usage") or {}
                out += u.get("completion_tokens", 0) or 0
                p = u.get("prompt_tokens", 0) or 0
                r = u.get("cache_read_input_tokens", 0) or 0
                w = u.get("cache_creation_input_tokens", 0) or 0
                cr += r
                cw += w
                ncc += max(p - r - w, 0)
                if ts and prev:
                    wall += ts - prev
            if ts:
                prev = ts
    thinking = 0
    timing = f"{ROOT}/runs/pro/{model_dir}/api-timing.jsonl"
    if os.path.exists(timing):
        for line in open(timing):
            u = json.loads(line).get("usage") or {}
            thinking += (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
    else:
        thinking = None
    resolved = None
    results_path = f"{ROOT}/evals/pro/{model_dir}/eval_results.json"
    if os.path.exists(results_path):
        results = json.load(open(results_path))
        resolved = sum(1 for v in results.values() if v)
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, thinking=thinking,
                resolved=resolved)


models = sorted(
    d for d in os.listdir(f"{ROOT}/runs/pro")
    if os.path.isdir(f"{ROOT}/runs/pro/{d}/pro")
) if os.path.isdir(f"{ROOT}/runs/pro") else []
data = {m: leg(m) for m in models}

rows = [
    ("Instances", lambda L: str(L["instances"])),
    ("Resolved", lambda L: str(L["resolved"]) if L["resolved"] is not None else "—"),
    ("Resolved %", lambda L: f"{L['resolved']/L['instances']*100:.0f}%" if L["resolved"] is not None and L["instances"] else "—"),
    ("$/resolved", lambda L: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
    ("Empty patches", lambda L: str(L["empty"])),
    ("Total cost", lambda L: f"${L['cost']:.2f}"),
    ("$/instance", lambda L: f"${L['cost']/L['instances']:.2f}" if L["instances"] else "—"),
    ("Steps", lambda L: f"{L['steps']:,}"),
    ("Output tokens", lambda L: tok(L["out"])),
    ("Thinking (output)", lambda L: tok(L["thinking"]) if L["thinking"] is not None else "—"),
    ("Input tokens", lambda L: tok(L["intot"])),
    ("- non-cached", lambda L: tok(L["ncc"])),
    ("- cache read", lambda L: tok(L["cr"])),
    ("- cache write", lambda L: tok(L["cw"])),
    ("Wall-clock", lambda L: f"{L['wall']/3600:.1f} h"),
]

lines = []
n_instances = max((d["instances"] for d in data.values()), default=0)
lines.append(f"| SWE-bench Pro — {n_instances} ts instances (tutao/tutanota) | " + " | ".join(models) + " |")
lines.append("|" + "---|" * (len(models) + 1))
for label, fn in rows:
    lines.append(f"| {label} | " + " | ".join(fn(data[m]) for m in models) + " |")
lines.append("")
lines.append("Verdicts from the vendored Scale harness (mark-pro); — means a leg is not yet marked.")

os.makedirs(f"{ROOT}/analysis", exist_ok=True)
with open(f"{ROOT}/analysis/pro.json", "w") as f:
    json.dump({"models": data}, f, indent=2)
with open(f"{ROOT}/analysis/pro.md", "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"wrote {ROOT}/analysis/pro.json and {ROOT}/analysis/pro.md")
