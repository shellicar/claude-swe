"""Aggregate the Multilingual experiment into files under analysis/.

Same conventions and row set as analyse.py/analyse-pro.py. Verdicts come from
the swebench marker's report JSONs in evals/ (run ids derive from the leg's
out path); when a leg is unmarked its resolve cells read "—" rather than
pretending.

Sources, per model x selection:
- resolved       : evals/*.runs_multilingual_<model>_<selection>.json
- cost/steps/tok : trajectories runs/multilingual/<model>/<selection>/*/*.traj.json
- thinking       : the leg's wire capture, attributed to selections by
                   first-user-message fingerprint (same hash the proxy uses)

Outputs: analysis/multilingual.json (raw figures), analysis/multilingual.md.
analysis/ is derived figures; evals/ is raw verdicts — kept apart on purpose.
"""

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SELECTIONS = ["rust", "cpp"]
EXPECTED = {"rust": 9, "cpp": 11}
REPOS = {"rust": "tokio-rs/tokio", "cpp": "fmtlib/fmt"}


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


def leg(model_dir, sel):
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    empty = 0
    trajs = sorted(glob.glob(f"{ROOT}/runs/multilingual/{model_dir}/{sel}/*/*.traj.json"))
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
    resolved = None
    reports = glob.glob(f"{ROOT}/evals/*.runs_multilingual_{model_dir}_{sel}.json")
    if len(reports) == 1:
        resolved = len(json.load(open(reports[0]))["resolved_ids"])
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, resolved=resolved,
                **test_outcomes(model_dir, sel))


def test_outcomes(model_dir, sel):
    """Test-level outcomes, from the marker's per-instance reports. Binary
    resolve hides the difference between 'never fixed it', 'fixed it and
    nicked one adjacent test', and 'shipped something that broke the build';
    these three counts recover it.
      fixed  : all FAIL_TO_PASS tests pass (the bug itself is fixed)
      near   : fixed, but some PASS_TO_PASS broke (fixed - resolved = near)
      wrecked: >20% of PASS_TO_PASS broke — in compiled repos this almost
               always means the patch did not build
    Requires evals/logs/run_evaluation/ locally (regenerable, not committed);
    returns None values when the logs are absent."""
    pattern = f"{ROOT}/evals/logs/run_evaluation/runs_multilingual_{model_dir}_{sel}/*/*/report.json"
    files = glob.glob(pattern)
    if not files:
        return dict(fixed=None, near=None, wrecked=None)
    fixed = near = wrecked = 0
    for f in files:
        rep = json.load(open(f))
        ((iid, r),) = rep.items()
        ts = r["tests_status"]
        f2p_clean = len(ts["FAIL_TO_PASS"]["failure"]) == 0
        p2p_fail = len(ts["PASS_TO_PASS"]["failure"])
        p2p_total = p2p_fail + len(ts["PASS_TO_PASS"]["success"])
        if f2p_clean:
            fixed += 1
            if p2p_fail > 0:
                near += 1
        if p2p_total > 0 and p2p_fail / p2p_total > 0.2:
            wrecked += 1
    return dict(fixed=fixed, near=near, wrecked=wrecked)


def wire_thinking(model_dir):
    """Per-selection thinking tokens from the leg's own capture."""
    timing = f"{ROOT}/runs/multilingual/{model_dir}/api-timing.jsonl"
    if not os.path.exists(timing):
        return None
    conv2sel = {}
    for sel in SELECTIONS:
        for tf in glob.glob(f"{ROOT}/runs/multilingual/{model_dir}/{sel}/*/*.traj.json"):
            t = json.load(open(tf))
            first = next((m for m in t["messages"] if m.get("role") == "user"), None)
            c = first["content"]
            text = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c)
            conv2sel[hashlib.sha256(text.encode()).hexdigest()[:12]] = sel
    totals = {sel: 0 for sel in SELECTIONS}
    for line in open(timing):
        d = json.loads(line)
        u = d.get("usage") or {}
        th = (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
        sel = conv2sel.get(d.get("conv"))
        if sel is not None:
            totals[sel] += th
    return totals


models = sorted(
    d for d in os.listdir(f"{ROOT}/runs/multilingual")
    if os.path.isdir(f"{ROOT}/runs/multilingual/{d}")
) if os.path.isdir(f"{ROOT}/runs/multilingual") else []
data = {m: {sel: leg(m, sel) for sel in SELECTIONS} for m in models}
THINKING = {m: wire_thinking(m) for m in models}


def make_rows(sel):
    expected = EXPECTED[sel]
    return [
        ("Instances", lambda L: str(L["instances"])),
        ("Resolved", lambda L: str(L["resolved"]) if L["resolved"] is not None else "—"),
        ("Resolved %", lambda L: f"{L['resolved']/expected*100:.0f}%" if L["resolved"] is not None else "—"),
        ("Bug fixed (F2P clean)", lambda L: str(L["fixed"]) if L["fixed"] is not None else "—"),
        ("Near misses (fixed, P2P broke)", lambda L: str(L["near"]) if L["near"] is not None else "—"),
        ("Build-breakers (>20% P2P broke)", lambda L: str(L["wrecked"]) if L["wrecked"] is not None else "—"),
        ("Total cost", lambda L: f"${L['cost']:.2f}"),
        ("$/resolved", lambda L: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
        ("$/instance", lambda L: f"${L['cost']/L['instances']:.2f}" if L["instances"] else "—"),
        ("Empty patches", lambda L: str(L["empty"])),
        ("Steps", lambda L: f"{L['steps']:,}"),
        ("Output tokens", lambda L: tok(L["out"])),
        ("Input tokens", lambda L: tok(L["intot"])),
        ("- non-cached", lambda L: tok(L["ncc"])),
        ("- cache read", lambda L: tok(L["cr"])),
        ("- cache write", lambda L: tok(L["cw"])),
        ("Wall-clock", lambda L: f"{L['wall']/3600:.1f} h"),
    ]


lines = []
lines.append("| Multilingual | " + " | ".join(models) + " |")
lines.append("|" + "---|" * (len(models) + 1))
for sel in SELECTIONS:
    lines.append(f"| **{sel} ({REPOS[sel]}, {EXPECTED[sel]} instances)** |" + " |" * len(models))
    for label, fn in make_rows(sel):
        lines.append(f"| {label} | " + " | ".join(fn(data[m][sel]) for m in models) + " |")
    thinks = []
    for m in models:
        v = THINKING.get(m)
        thinks.append(tok(v[sel]) if v else "—")
    lines.append(f"| Thinking (output) | " + " | ".join(thinks) + " |")
lines.append("")
lines.append("Verdicts from the swebench marker; — means a leg is not yet marked.")

os.makedirs(f"{ROOT}/analysis", exist_ok=True)
with open(f"{ROOT}/analysis/multilingual.json", "w") as f:
    json.dump({"models": data, "thinking": THINKING}, f, indent=2)
with open(f"{ROOT}/analysis/multilingual.md", "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"wrote {ROOT}/analysis/multilingual.json and {ROOT}/analysis/multilingual.md")
