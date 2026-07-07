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
import json

MODELS = [  # display name -> dir
    ("Claude Fable 5", "fable-5"),
    ("Claude Fable 5 (2 Jul)", "fable-5-high-2026-07-02"),
    ("Claude Opus 4.8", "opus-4-8"),
    ("Claude Opus 4.7", "opus-4-7"),
    ("Claude Opus 4.6", "opus-4-6"),
    ("Claude Sonnet 4.6", "sonnet-4-6"),
    ("Claude Haiku 4.5", "haiku-4-5"),
]
SETS = [("standard", 60), ("hard", 45)]
ROOT = "/Users/shellicar/claude-swe"

# wire-derived thinking tokens (see module docstring); None => unknown
THINKING = {
    "opus-4-6": {"standard": 127114, "hard": 298606},
    "opus-4-7": {"standard": 190279, "hard": 345513},
}


def leg(dirn, s):
    # Report is named <model>.<run_id>.json; the run_id (runs_main_<dir>_<set>) is
    # unique per leg, so glob on it rather than assume model name == dir name (a
    # repeat run keeps the model slug 'fable-5' but a distinct dir).
    rep = glob.glob(f"{ROOT}/*.runs_main_{dirn}_{s}.json")[0]
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

hdr = "| | " + " | ".join(name for name, _ in MODELS) + " |"
sep = "|" + "---|" * (len(MODELS) + 1)
print(hdr)
print(sep)


def combined(d):
    c = {}
    for k in data[d]["standard"]:
        c[k] = data[d]["standard"][k] + data[d]["hard"][k]
    return c


def emit(section_label, getter, n, thinking_set):
    print(f"| **{section_label}** |" + " |" * len(MODELS))
    for label, fn in rows:
        if fn is None:  # thinking row
            cells = [think(d, thinking_set) if thinking_set else
                     (think(d, "standard") if False else "—") for _, d in MODELS]
            if thinking_set is None:  # combined
                cells = []
                for _, d in MODELS:
                    v = THINKING.get(d)
                    cells.append(tok(v["standard"] + v["hard"]) if v else "—")
            print(f"| {label} | " + " | ".join(cells) + " |")
            continue
        lab = label.format(n=n) if "{n}" in label else label
        cells = [fn(getter(d), n) for _, d in MODELS]
        print(f"| {lab} | " + " | ".join(cells) + " |")


emit("Standard \u2014 60 problems (<1 h human effort)", lambda d: data[d]["standard"], 60, "standard")
emit("Hard \u2014 45 problems (1+ h human effort)", lambda d: data[d]["hard"], 45, "hard")
emit("Combined \u2014 105 problems", lambda d: combined(d), 105, None)
