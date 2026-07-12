"""Aggregate the Multi-SWE-bench experiments into files under analysis/.

Same conventions and row set as the other analysers. Three sections: the
control arms (cpp, rust) and the C++ verification variation — same 20 cpp
instances, prompt told to build and run the suite, 900s action timeout.
Verdicts come from ByteDance's harness (final_report.json per leg); when a
leg is unmarked its resolve cells read "—" rather than pretending.

Sources, per section x model:
- resolved       : evals/multi/<runsroot>-<model>-<sel>/final_report.json
- cost/steps/tok : trajectories under the section's runs root
- thinking       : the leg's own wire capture, attributed by fingerprint
- empty patches  : submissions with no diff (automatic unresolved)

Outputs: analysis/multi/ (data.json, table.md, table.html, table.png) via the
shared emitter. analysis/ is derived figures; evals/ is raw verdicts.
"""

import glob
import hashlib
import json
import os

from analysis_output import emit

ROOT = os.path.dirname(os.path.abspath(__file__))

# label -> (runs root, selection ids file, evals dir prefix)
SECTIONS = {
    "cpp control": dict(runs="runs/multi/{m}/cpp", ids="instances-multi-cpp.txt", evals="evals/multi/multi-{m}-cpp"),
    "rust control": dict(runs="runs/multi/{m}/rust", ids="instances-multi-rust.txt", evals="evals/multi/multi-{m}-rust"),
    "cpp variation (verify + 900s)": dict(runs="runs/cpp-variation/{m}/cpp", ids="instances-multi-cpp.txt", evals="evals/multi/cpp-variation-{m}-cpp"),
    "tokio stack (org tokio-rs)": dict(runs="runs/tokio/{m}/tokio", ids="instances-tokio-stack.txt", evals="evals/multi/tokio-{m}-tokio"),
}


def selection(decl):
    return {l.strip() for l in open(f"{ROOT}/{decl['ids']}") if l.strip()}


def tok(x):
    return f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"


def leg(model_dir, decl):
    cost = steps = out = cr = cw = ncc = 0
    wall = 0.0
    empty = 0
    runs_dir = decl["runs"].format(m=model_dir)
    # selection members only — stray traj dirs from the pre-fix naming
    # collision remain on disk as banked data and must not pollute figures
    ids = selection(decl)
    trajs = sorted(t for t in glob.glob(f"{ROOT}/{runs_dir}/*/*.traj.json")
                   if os.path.basename(os.path.dirname(t)) in ids)
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
    # thinking: the leg dir's own capture, attributed by first-user-message
    # fingerprint (control legs share one capture across cpp+rust)
    thinking = None
    timing = f"{ROOT}/{runs_dir.rsplit('/', 1)[0]}/api-timing.jsonl"
    if not os.path.exists(timing):
        timing = f"{ROOT}/{os.path.dirname(runs_dir.format(m=model_dir))}/api-timing.jsonl"
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
    report = f"{ROOT}/{decl['evals'].format(m=model_dir)}/final_report.json"
    if os.path.exists(report):
        rep = json.load(open(report))
        resolved = rep["resolved_instances"]
        # per-repo slice: selections mix repos, and a per-selection number
        # hides which repo carried it (fmt's zeros hid inside 14/20 until
        # sliced by hand — 2026-07-11). resolved_ids look like 'org/repo:pr-N';
        # selection ids like 'org__repo-N'.
        won = {}
        for rid in rep.get("resolved_ids", []):
            repo = rid.split("/")[1].split(":")[0]
            won[repo] = won.get(repo, 0) + 1
        by_repo = {}
        for iid in sorted(ids):
            repo = iid.split("__")[1].rsplit("-", 1)[0]
            t, _ = by_repo.get(repo, (0, 0))
            by_repo[repo] = (t + 1, won.get(repo, 0))
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, thinking=thinking,
                resolved=resolved, by_repo=by_repo)


def find_models():
    models = set()
    for decl in SECTIONS.values():
        root = f"{ROOT}/{decl['runs'].split('/{m}')[0]}"
        if os.path.isdir(root):
            models.update(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return sorted(models)


models = find_models()
data = {m: {label: leg(m, decl) for label, decl in SECTIONS.items()} for m in models}

def repo_rows(label_models):
    """One 'resolved n/m' row per repo appearing in a section's selections —
    the slice that survives selection changes."""
    repos = []
    for m in models:
        br = label_models[m].get("by_repo")
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

NOTE = "Verdicts from ByteDance's Multi-SWE harness; — means a leg is not yet marked."

sections_out = []
for label, decl in SECTIONS.items():
    n = max((data[m][label]["instances"] for m in models), default=0)
    per_model = {m: data[m][label] for m in models}
    section_rows = rows[:2] + repo_rows(per_model) + rows[2:]
    body = [(rl, [fn(data[m][label]) for m in models]) for rl, fn in section_rows]
    sections_out.append((f"{label} ({n} instances)", body))

emit("multi", "Multi-SWE-bench", models, sections_out, NOTE, {"models": data})
