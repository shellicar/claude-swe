"""Aggregate the experiment into the report table.

Sources, per model/set:
- resolved        : eval report  anthropic__claude-<model>.runs_main_<model>_<set>.json
- cost/steps/tok  : trajectories runs/main/<model>/<set>/*/*.traj.json
- wall-clock      : trajectory message timestamps (tool->assistant gaps). This is
                    wall-clock-under-12-way-parallel, ~5x true API service time
                    (see runs/main/api-timing.jsonl / the proxy capture); NOT API time.
- thinking        : wire capture for opus-4-6/4-7 only (litellm under-reports it in
                    trajectories). Per-set values below are from opus46-47-responses.jsonl
                    attributed by first-user-message fingerprint. Unknown ("—") for the
                    models whose run predates the wire capture.
"""

import glob
import hashlib
import json
import os

MODELS = [  # display name -> dir
    ("Claude Fable 5", "fable-5"),
    ("Claude Fable 5 (2 Jul)", "fable-5-high-2026-07-02"),
    ("Claude Opus 4.8", "opus-4-8"),
    ("Claude Opus 4.7", "opus-4-7"),
    ("Claude Opus 4.6", "opus-4-6"),
    ("Claude Sonnet 4.6", "sonnet-4-6"),
    ("Claude Sonnet 5", "sonnet-5"),
    ("Claude Haiku 4.5", "haiku-4-5"),
]
SETS = [("standard", 60), ("hard", 45)]
ROOT = os.path.dirname(os.path.abspath(__file__))  # was hardcoded to the old machine's path

# Legacy wire-derived thinking tokens: the opus-4-6/4-7 shared capture lives in
# a different file format (opus46-47-responses.jsonl) and predates per-leg
# captures, so its totals stay hardcoded. Every leg run since gets a per-leg
# runs/main/<dir>/api-timing.jsonl and is computed automatically below.
THINKING_LEGACY = {
    "opus-4-6": {"standard": 127114, "hard": 298606},
    "opus-4-7": {"standard": 190279, "hard": 345513},
}


def wire_thinking(dirn):
    """Per-set thinking tokens from the leg's own proxy capture, attributed to
    instances by first-user-message fingerprint (same hash the proxy uses).
    Returns None when the leg has no capture."""
    timing = f"{ROOT}/runs/main/{dirn}/api-timing.jsonl"
    if not os.path.exists(timing):
        return THINKING_LEGACY.get(dirn)
    conv2set = {}
    for s, _ in SETS:
        for tf in glob.glob(f"{ROOT}/runs/main/{dirn}/{s}/*/*.traj.json"):
            t = json.load(open(tf))
            first = next((m for m in t["messages"] if m.get("role") == "user"), None)
            c = first["content"]
            text = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c)
            conv2set[hashlib.sha256(text.encode()).hexdigest()[:12]] = s
    totals = {s: 0 for s, _ in SETS}
    for line in open(timing):
        d = json.loads(line)
        u = d.get("usage") or {}
        th = (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
        s = conv2set.get(d.get("conv"))
        if s is not None:
            totals[s] += th
    return totals


def leg(dirn, s):
    # Report is named <model>.<run_id>.json; the run_id (runs_main_<dir>_<set>) is
    # unique per leg, so glob on it rather than assume model name == dir name (a
    # repeat run keeps the model slug 'fable-5' but a distinct dir).
    # Verdicts live under evals/ since the eval operations rework.
    rep = glob.glob(f"{ROOT}/evals/*.runs_main_{dirn}_{s}.json")[0]
    resolved = len(json.load(open(rep))["resolved_ids"])
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    for tf in glob.glob(f"{ROOT}/runs/main/{dirn}/{s}/*/*.traj.json"):
        t = json.load(open(tf))
        st = t["info"]["model_stats"]
        cost += st["instance_cost"]
        steps += st["api_calls"]
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
    return dict(resolved=resolved, cost=cost, steps=steps, out=out,
               ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall)


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


# gather thinking once per model (None => no capture exists for that leg)
THINKING = {d: wire_thinking(d) for _, d in MODELS}


def think(dirn, s):
    v = THINKING.get(dirn)
    return tok(v[s]) if v else "—"


# gather: data[dirn][set] = leg dict
data = {d: {s: leg(d, n and s) for s, n in SETS} for _, d in MODELS}

rows = [
    ("Resolved (/{n})", lambda L, n: str(L["resolved"])),
    ("Resolved %", lambda L, n: f"{L['resolved']/n*100:.0f}%"),
    ("Total cost", lambda L, n: f"${L['cost']:.2f}"),
    ("$ / resolved", lambda L, n: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
    ("Steps", lambda L, n: f"{L['steps']:,}"),
    ("Output tokens", lambda L, n: tok(L["out"])),
    ("Thinking (output)", None),  # special: needs dirn+set
    ("Input tokens", lambda L, n: tok(L["intot"])),
    ("\u2014 non-cached", lambda L, n: tok(L["ncc"])),
    ("\u2014 cache read", lambda L, n: tok(L["cr"])),
    ("\u2014 cache write", lambda L, n: tok(L["cw"])),
    ("Wall-clock (12-way parallel)", lambda L, n: f"{L['wall']/3600:.1f} h"),
]

OUT_LINES = []
OUT_LINES.append("| | " + " | ".join(name for name, _ in MODELS) + " |")
OUT_LINES.append("|" + "---|" * (len(MODELS) + 1))


def combined(d):
    c = {}
    for k in data[d]["standard"]:
        c[k] = data[d]["standard"][k] + data[d]["hard"][k]
    return c


def emit(section_label, getter, n, thinking_set):
    OUT_LINES.append(f"| **{section_label}** |" + " |" * len(MODELS))
    for label, fn in rows:
        if fn is None:  # thinking row
            cells = [think(d, thinking_set) if thinking_set else
                     (think(d, "standard") if False else "—") for _, d in MODELS]
            if thinking_set is None:  # combined
                cells = []
                for _, d in MODELS:
                    v = THINKING.get(d)
                    cells.append(tok(v["standard"] + v["hard"]) if v else "—")
            OUT_LINES.append(f"| {label} | " + " | ".join(cells) + " |")
            continue
        lab = label.format(n=n) if "{n}" in label else label
        cells = [fn(getter(d), n) for _, d in MODELS]
        OUT_LINES.append(f"| {lab} | " + " | ".join(cells) + " |")


emit("Standard \u2014 60 problems (<1 h human effort)", lambda d: data[d]["standard"], 60, "standard")
emit("Hard \u2014 45 problems (1+ h human effort)", lambda d: data[d]["hard"], 45, "hard")
emit("Combined \u2014 105 problems", lambda d: combined(d), 105, None)

# Outputs land on disk, not stdout: the numbers are data, not chat.
# analysis/ is derived figures; evals/ is raw verdicts — kept apart on purpose.
# - analysis/verified.json: every raw figure (per model, per set, plus thinking).
# - analysis/verified.md:   the rendered table, to be reconciled into report.md.
os.makedirs(f"{ROOT}/analysis", exist_ok=True)
with open(f"{ROOT}/analysis/verified.json", "w") as f:
    json.dump({"models": {d: {"name": name, "sets": data[d], "thinking": THINKING.get(d)}
                          for name, d in MODELS}}, f, indent=2)
with open(f"{ROOT}/analysis/verified.md", "w") as f:
    f.write("\n".join(OUT_LINES) + "\n")
print(f"wrote {ROOT}/analysis/verified.json and {ROOT}/analysis/verified.md")
