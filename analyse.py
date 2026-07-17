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

from analysis_output import emit

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


def leg(base, s):
    # base is the run out path, e.g. "main/opus-4-8" or "exec-arm-1/sonnet-5".
    # Report is <model>.<run_id>.json; run_id = runs_<base-with-underscores>_<set>.
    rid = base.replace("/", "_")
    rep = glob.glob(f"{ROOT}/evals/*.runs_{rid}_{s}.json")[0]
    resolved = len(json.load(open(rep))["resolved_ids"])
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    for tf in glob.glob(f"{ROOT}/runs/{base}/{s}/*/*.traj.json"):
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
data = {d: {s: leg(f"main/{d}", s) for s, n in SETS} for _, d in MODELS}

rows = [
    ("## Results", lambda L, n: ""),
    ("Resolved", lambda L, n: str(L["resolved"])),
    ("Resolved %", lambda L, n: f"{L['resolved']/n*100:.0f}%"),
    ("Total cost", lambda L, n: f"${L['cost']:.2f}"),
    ("$/resolved", lambda L, n: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
    ("## Stats", lambda L, n: ""),
    ("Steps", lambda L, n: f"{L['steps']:,}"),
    ("Output tokens", lambda L, n: tok(L["out"])),
    ("Thinking (output)", None),  # special: needs dirn+set
    ("Input tokens", lambda L, n: tok(L["intot"])),
    ("\u2014 non-cached", lambda L, n: tok(L["ncc"])),
    ("\u2014 cache read", lambda L, n: tok(L["cr"])),
    ("\u2014 cache write", lambda L, n: tok(L["cw"])),
    ("Wall-clock (12-way parallel)", lambda L, n: f"{L['wall']/3600:.1f} h"),
]

def combined(d):
    c = {}
    for k in data[d]["standard"]:
        c[k] = data[d]["standard"][k] + data[d]["hard"][k]
    return c


def section(dirs, getter, n, thinking_set):
    body = []
    for label, fn in rows:
        if fn is None:  # thinking row
            if thinking_set is None:  # combined
                cells = []
                for d in dirs:
                    v = THINKING.get(d)
                    cells.append(tok(v["standard"] + v["hard"]) if v else "—")
            else:
                cells = [think(d, thinking_set) for d in dirs]
            body.append((label, cells))
            continue
        lab = label.format(n=n) if "{n}" in label else label
        body.append((lab, [fn(getter(d), n) for d in dirs]))
    return body


def sections_for(dirs):
    return [
        ("Standard — 60 *Python* events (<1 h human effort)", section(dirs, lambda d: data[d]["standard"], 60, "standard")),
        ("Hard — 45 *Python* events (1+ h human effort)", section(dirs, lambda d: data[d]["hard"], 45, "hard")),
        ("Combined — 105 *Python* events", section(dirs, lambda d: combined(d), 105, None)),
    ]


NAME = dict((d, name) for name, d in MODELS)
NOTE = "Verdicts from the pinned swebench judges. Full caveats in report.md."

# Three competing groups, never mixed in one table (a model may enter two
# groups, like an athlete in two events): the latest generation of each tier,
# and the two lineages read left-to-right as improvement curves. The verified
# data.json keeps EVERY model — grouping is presentation, not data loss.
GROUPS = [
    ("verified", "SWE-bench Verified — latest-generation division",
     ["fable-5", "opus-4-8", "sonnet-5", "haiku-4-5"]),
    ("opus-models", "Opus division — the lineage (SWE-bench Verified)",
     ["opus-4-6", "opus-4-7", "opus-4-8"]),
    ("sonnet-models", "Sonnet division — the lineage (SWE-bench Verified)",
     ["sonnet-4-6", "sonnet-5"]),
]

for card, heading, dirs in GROUPS:
    payload = {"models": {d: {"name": name, "sets": data[d], "thinking": THINKING.get(d)}
                          for name, d in MODELS}}
    if card == "verified":
        payload["covers"] = ["standard", "hard"]
    emit(card, heading, [NAME[d] for d in dirs], sections_for(dirs), NOTE, payload)


# Structured-execution division: bash control vs the exec arms, verified/hard,
# Sonnet 5. Hard-only — the frozen set the exec experiment ran on.
EXEC = [
    ("Sonnet 5 — bash (control)", "main/sonnet-5"),
    ("Sonnet 5 — exec, bash instructions", "exec-arm-1/sonnet-5"),
    ("Sonnet 5 — exec, aligned instructions", "exec-arm-2/sonnet-5"),
]
exec_data = {base: leg(base, "hard") for _, base in EXEC}


def exec_section(bases):
    body = []
    for label, fn in rows:
        if fn is None:  # thinking not attributed for the exec arms
            body.append((label, ["—" for _ in bases]))
            continue
        body.append((label, [fn(exec_data[b], 45) for b in bases]))
    return body


_bases = [b for _, b in EXEC]
emit("exec", "Structured-execution division — SWE-bench Verified hard, Sonnet 5",
     [n for n, _ in EXEC],
     [("Hard — 45 *Python* events (1+ h human effort)", exec_section(_bases))],
     NOTE,
     {"covers": ["hard"], "models": {b: {"name": n, "sets": {"hard": exec_data[b]}} for n, b in EXEC}})
