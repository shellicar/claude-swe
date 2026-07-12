"""Aggregate the Multilingual experiments into files under analysis/.

Three sections: the control arms (rust, cpp) and the fmt verification
variation — the SAME 11 cpp instances, prompt told to build and run the
suite, 900s action timeout (combinations/fmt-variation.json). Verdicts come
from the swebench marker's report JSONs in evals/; when a leg is unmarked its
resolve cells read "—" rather than pretending.

Sources, per section x model:
- resolved       : evals/*.<runid prefix>_<model>_cpp.json
- cost/steps/tok : trajectories under the section's runs root
- test outcomes  : the marker's per-instance reports (evals/logs/, regenerable)
- thinking       : the leg's wire capture, attributed by fingerprint

Outputs: analysis/multilingual/ (data.json, table.md, table.html, table.png)
via the shared emitter. analysis/ is derived figures; evals/ is raw verdicts.
"""

import glob
import hashlib
import json
import os

from analysis_output import emit

ROOT = os.path.dirname(os.path.abspath(__file__))

# label -> (selection, runs root, run-id prefix, expected)
SECTIONS = {
    "*Rust* — 7 repos (43 events)": dict(sel="rust", runs="runs/multilingual", runid="runs_multilingual", expected=43, ids="instances-rust.txt"),
    "fmtlib/fmt — *C++* (11 events)": dict(sel="cpp", runs="runs/multilingual", runid="runs_multilingual", expected=11),
    "*Go* — 5 repos (42 events)": dict(sel="go", runs="runs/multilingual", runid="runs_multilingual", expected=42, ids="instances-go.txt"),
    "*C++* variation (verify + 900s, same 11 — exhibition)": dict(sel="cpp", runs="runs/fmt-variation", runid="runs_fmt-variation", expected=11),
}


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


def test_outcomes(decl, model_dir):
    """Test-level outcomes from the marker's per-instance reports. Binary
    resolve hides 'never fixed it' vs 'fixed it and nicked a test' vs 'broke
    the build'; these counts recover it. None when the logs are absent."""
    pattern = f"{ROOT}/evals/logs/run_evaluation/{decl['runid']}_{model_dir}_{decl['sel']}/*/*/report.json"
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


def leg(model_dir, decl):
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    empty = 0
    runs_dir = f"{decl['runs']}/{model_dir}/{decl['sel']}"
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
    # thinking: the leg's own capture, attributed by first-user-message
    # fingerprint (the multilingual control shares one capture across selections)
    thinking = None
    timing = f"{ROOT}/{decl['runs']}/{model_dir}/api-timing.jsonl"
    if os.path.exists(timing):
        conv2here = set()
        for tf in trajs:
            t = json.load(open(tf))
            first = next((m for m in t["messages"] if m.get("role") == "user"), None)
            c = first["content"]
            text = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c)
            conv2here.add(hashlib.sha256(text.encode()).hexdigest()[:12])
        thinking = 0
        for line in open(timing):
            d = json.loads(line)
            u = d.get("usage") or {}
            th = (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
            if d.get("conv") in conv2here:
                thinking += th
    resolved = None
    by_repo = None
    reports = glob.glob(f"{ROOT}/evals/*.{decl['runid']}_{model_dir}_{decl['sel']}.json")
    if len(reports) == 1:
        rep = json.load(open(reports[0]))
        resolved = len(rep["resolved_ids"])
        # per-repo slice for multi-repo selections — a flat count hides which
        # repo carried it (the fmt lesson)
        if decl.get("ids"):
            short = lambda iid: iid.split("__")[1].rsplit("-", 1)[0]
            won = {}
            for iid in rep["resolved_ids"]:
                won[short(iid)] = won.get(short(iid), 0) + 1
            by_repo = {}
            for iid in sorted(l.strip() for l in open(f"{ROOT}/{decl['ids']}") if l.strip()):
                r = short(iid)
                t, _ = by_repo.get(r, (0, 0))
                by_repo[r] = (t + 1, won.get(r, 0))
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, thinking=thinking,
                resolved=resolved, by_repo=by_repo, **test_outcomes(decl, model_dir))



# Latest-generation column order; a model appears when its runs exist (Haiku
# joins automatically once it competes here).
LATEST = ["fable-5", "opus-4-8", "sonnet-5", "haiku-4-5"]

def find_models():
    models = set()
    for decl in SECTIONS.values():
        root = f"{ROOT}/{decl['runs']}"
        if os.path.isdir(root):
            models.update(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return [m for m in LATEST if m in models]


models = find_models()
data = {m: {label: leg(m, decl) for label, decl in SECTIONS.items()} for m in models}



def total_section(controls):
    """Sum the control sections' headline figures into a TOTAL section —
    the tally at the bottom of the card. Variations are excluded: they
    revisit instances the controls already count."""
    body = []
    sums = {m: dict(r=0, n=0, c=0.0) for m in models}
    for label in controls:
        for m in models:
            L = data[m][label]
            if L.get("resolved") is not None and L.get("instances"):
                sums[m]["r"] += L["resolved"]
                sums[m]["n"] += L["instances"]
                sums[m]["c"] += L["cost"]
    def cells(fn):
        return [fn(sums[m]) if sums[m]["n"] else "—" for m in models]
    body.append(("Resolved", cells(lambda s: f"{s['r']}/{s['n']}")))
    body.append(("Resolved %", cells(lambda s: f"{s['r']/s['n']*100:.0f}%")))
    body.append(("Total cost", cells(lambda s: f"${s['c']:.2f}")))
    body.append(("$/resolved", cells(lambda s: f"${s['c']/s['r']:.2f}" if s["r"] else "—")))
    return body

def make_rows(expected):
    return [
        ("## Results", lambda L: ""),
        ("Resolved", lambda L: str(L["resolved"]) if L["resolved"] is not None else "—"),
        ("Resolved %", lambda L: f"{L['resolved']/expected*100:.0f}%" if L["resolved"] is not None else "—"),
        ("Total cost", lambda L: f"${L['cost']:.2f}"),
        ("$/resolved", lambda L: f"${L['cost']/L['resolved']:.2f}" if L["resolved"] else "—"),
        ("## Stats", lambda L: ""),
        ("Bug fixed (F2P clean)", lambda L: str(L["fixed"]) if L["fixed"] is not None else "—"),
        ("Near misses (fixed, P2P broke)", lambda L: str(L["near"]) if L["near"] is not None else "—"),
        ("Build-breakers (>20% P2P broke)", lambda L: str(L["wrecked"]) if L["wrecked"] is not None else "—"),
        ("$/instance", lambda L: f"${L['cost']/L['instances']:.2f}" if L["instances"] else "—"),
        ("Empty patches", lambda L: str(L["empty"])),
        ("Steps", lambda L: f"{L['steps']:,}"),
        ("Output tokens", lambda L: tok(L["out"])),
        ("Thinking (output)", lambda L: tok(L["thinking"]) if L["thinking"] is not None else "—"),
        ("Input tokens", lambda L: tok(L["intot"])),
        ("- non-cached", lambda L: tok(L["ncc"])),
        ("- cache read", lambda L: tok(L["cr"])),
        ("- cache write", lambda L: tok(L["cw"])),
        ("Wall-clock", lambda L: f"{L['wall']/3600:.1f} h"),
    ]


NOTE = "Verdicts from the swebench judges; — means a contender has not entered or is unjudged."

def repo_rows(label):
    repos = []
    for m in models:
        br = data[m][label].get("by_repo")
        if br:
            for r in br:
                if r not in repos:
                    repos.append(r)
    out = []
    for r in sorted(repos):
        def fn(L, _r=r):
            br = L.get("by_repo")
            if not br or _r not in br:
                return "—"
            t, w = br[_r]
            return f"{w}/{t}"
        out.append((f"— {r}", fn))
    return out


sections = []
for label, decl in SECTIONS.items():
    rows_all = make_rows(decl["expected"])
    rows_all = rows_all[:5] + repo_rows(label) + rows_all[5:]
    body = [(rl, [fn(data[m][label]) for m in models]) for rl, fn in rows_all]
    sections.append((label, body))

sections.append(("TOTAL — controls (variation excluded)", total_section(["*Rust* — 7 repos (43 events)", "fmtlib/fmt — *C++* (11 events)", "*Go* — 5 repos (42 events)"])))

emit("multilingual", "SWE-bench Multilingual", models, sections, NOTE,
     {"covers": ["rust", "cpp", "go"], "models": data})
