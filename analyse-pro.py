"""Aggregate SWE-bench Pro results into files under analysis/.

One file for the whole pro dataset, a section per selection — tutanota (ts)
and NodeBB (js) — same conventions and row set as the other analysers.
Verdicts come from the vendored Scale harness; when a leg has no
eval_results.json yet its resolve cells read "—" rather than pretending.

Sources, per selection x model:
- resolved       : evals/pro/<model>/eval_results.json (tutanota, legacy path)
                   evals/pro/<model>-nodebb/eval_results.json (nodebb)
- cost/steps/tok : trajectories under the selection's runs root
- thinking       : the leg's own wire capture (one per selection leg dir)
- empty patches  : submissions with no diff (automatic unresolved)

Outputs: analysis/pro/ (data.json, table.md, table.html, table.png) via the
shared emitter. analysis/ is derived figures; evals/ is raw verdicts.
"""

import glob
import json
import os

from analysis_output import emit

ROOT = os.path.dirname(os.path.abspath(__file__))

# Per selection: where its run legs live, and how its verdict dir is named
# (the 'pro' selection keeps the original evals/pro/<model> layout; later
# selections carry a -<sel> suffix — mirrors scaleOutDir in swe.mjs).
SELECTIONS = {
    "pro": dict(label="tutanota ts", runs="runs/pro/{m}/pro", evals="evals/pro/{m}", repo="repo_language", equals="ts"),
    "nodebb": dict(label="NodeBB js", runs="runs/nodebb/{m}/nodebb", evals="evals/pro/{m}-nodebb", repo="repo", equals="NodeBB/NodeBB"),
    "element": dict(label="element-web js", runs="runs/element/{m}/element", evals="evals/pro/{m}-element", repo="repo", equals="element-hq/element-web"),
}


def population(decl):
    """How many instances exist in the snapshot for this selection's rule —
    so the table can say 'n of N' instead of passing a sample off as a world."""
    count = 0
    for line in open(f"{ROOT}/datasets/swe-bench-pro.jsonl"):
        if line.strip() and json.loads(line).get(decl["repo"]) == decl["equals"]:
            count += 1
    return count


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


def leg(model_dir, sel):
    decl = SELECTIONS[sel]
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    empty = 0
    runs_dir = decl["runs"].format(m=model_dir)
    trajs = sorted(glob.glob(f"{ROOT}/{runs_dir}/*/*.traj.json"))
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
    # thinking: the leg dir's own wire capture (one proxy per leg)
    thinking = None
    timing = f"{ROOT}/{runs_dir.rsplit('/', 1)[0]}/api-timing.jsonl"
    if os.path.exists(timing):
        thinking = 0
        for line in open(timing):
            u = json.loads(line).get("usage") or {}
            thinking += (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
    resolved = None
    results_path = f"{ROOT}/{decl['evals'].format(m=model_dir)}/eval_results.json"
    if os.path.exists(results_path):
        results = json.load(open(results_path))
        resolved = sum(1 for v in results.values() if v)
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, thinking=thinking,
                resolved=resolved)


def find_models():
    models = set()
    for sel, decl in SELECTIONS.items():
        root = f"{ROOT}/{decl['runs'].split('/{m}')[0]}"
        if os.path.isdir(root):
            models.update(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return sorted(models)


models = find_models()
data = {m: {sel: leg(m, sel) for sel in SELECTIONS} for m in models}

rows = [
    # headline
    ("Resolved", lambda L: str(L["resolved"]) if L["resolved"] is not None else "—"),
    ("Resolved %", lambda L: f"{L['resolved']/L['instances']*100:.0f}%" if L["resolved"] is not None and L["instances"] else "—"),
    ("Total cost", lambda L: f"${L['cost']:.2f}"),
    ("$/resolved", lambda L: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
    # information
    ("Empty patches", lambda L: str(L["empty"])),
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

NOTE = "Verdicts from the vendored Scale harness; — means a leg is not yet marked."

# One (label, cells-per-model) matrix per section, rendered into each format.
sections = []
for sel, decl in SELECTIONS.items():
    n = max((data[m][sel]["instances"] for m in models), default=0)
    pop = population(decl)
    scope = f"all {pop}" if n == pop else f"{n} of {pop}"
    body = [(label, [fn(data[m][sel]) for m in models]) for label, fn in rows]
    sections.append((f"{decl['label']} ({scope} instances)", body))

emit("pro", "SWE-bench Pro", models, sections, NOTE,
     {"covers": list(SELECTIONS), "models": data})
