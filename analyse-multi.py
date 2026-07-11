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

Outputs: analysis/multi.{json,md,html,d2} — and multi.{png,svg} when d2 is
on PATH. analysis/ is derived figures; evals/ is raw verdicts.
"""

import glob
import hashlib
import html as html_mod
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# label -> (runs root, selection ids file, evals dir prefix)
SECTIONS = {
    "cpp control": dict(runs="runs/multi/{m}/cpp", ids="instances-multi-cpp.txt", evals="evals/multi/multi-{m}-cpp"),
    "rust control": dict(runs="runs/multi/{m}/rust", ids="instances-multi-rust.txt", evals="evals/multi/multi-{m}-rust"),
    "cpp variation (verify + 900s)": dict(runs="runs/cpp-variation/{m}/cpp", ids="instances-multi-cpp.txt", evals="evals/multi/cpp-variation-{m}-cpp"),
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
    report = f"{ROOT}/{decl['evals'].format(m=model_dir)}/final_report.json"
    if os.path.exists(report):
        resolved = json.load(open(report))["resolved_instances"]
    return dict(instances=len(trajs), empty=empty, cost=cost, steps=steps, out=out,
                ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, thinking=thinking,
                resolved=resolved)


def find_models():
    models = set()
    for decl in SECTIONS.values():
        root = f"{ROOT}/{decl['runs'].split('/{m}')[0]}"
        if os.path.isdir(root):
            models.update(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return sorted(models)


models = find_models()
data = {m: {label: leg(m, decl) for label, decl in SECTIONS.items()} for m in models}

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
    body = [(rl, [fn(data[m][label]) for m in models]) for rl, fn in rows]
    sections_out.append((f"{label} ({n} instances)", body))

# markdown
lines = ["| Multi-SWE-bench | " + " | ".join(models) + " |", "|" + "---|" * (len(models) + 1)]
for title, body in sections_out:
    lines.append(f"| **{title}** |" + " |" * len(models))
    for rl, cells in body:
        lines.append(f"| {rl} | " + " | ".join(cells) + " |")
lines += ["", NOTE]

# html
h = ["<!doctype html><meta charset='utf-8'><title>Multi-SWE-bench</title>",
     "<style>body{background:#1b1b2b;color:#e8e8f0;font:14px -apple-system,sans-serif;padding:2em}",
     "table{border-collapse:collapse}td,th{border:1px solid #555;padding:.35em .8em;text-align:left}",
     "th{background:#2a2a3f}td.sec{background:#2a2a3f;font-weight:bold}</style>",
     "<table><tr><th>Multi-SWE-bench</th>" + "".join(f"<th>{html_mod.escape(m)}</th>" for m in models) + "</tr>"]
for title, body in sections_out:
    h.append(f"<tr><td class='sec' colspan='{len(models) + 1}'>{html_mod.escape(title)}</td></tr>")
    for rl, cells in body:
        h.append("<tr><td>" + html_mod.escape(rl) + "</td>" + "".join(f"<td>{html_mod.escape(c)}</td>" for c in cells) + "</tr>")
h.append(f"</table><p>{html_mod.escape(NOTE)}</p>")

# d2 — one md table per section, sacrificial blank last rows (see
# docs/diagrams/model-comparison.d2 for the measurement traps)
d2 = ["vars: { d2-config: { theme-id: 200 } }", "",
      'title: "Multi-SWE-bench" { near: top-center; shape: text; style.font-size: 22; style.bold: true }', ""]
prev = None
for idx, (title, body) in enumerate(sections_out):
    name = f"section{idx}"
    d2.append(f"{name}: |||md")
    d2.append(f"  | {title} | " + " | ".join(models) + " |")
    d2.append("  |" + "---|" * (len(models) + 1))
    for rl, cells in body:
        d2.append(f"  | {rl} | " + " | ".join(cells) + " |")
    d2.append("  | " + " | " * (len(models) + 1))
    d2.append("|||")
    if prev is not None:
        d2.append(f"{prev} -> {name}: {{style.opacity: 0}}")
    prev = name
d2.append(f'note: "{NOTE}" {{ near: bottom-center; shape: text; style.font-color: "#7F8C8D" }}')

os.makedirs(f"{ROOT}/analysis", exist_ok=True)
with open(f"{ROOT}/analysis/multi.json", "w") as f:
    json.dump({"models": data}, f, indent=2)
with open(f"{ROOT}/analysis/multi.md", "w") as f:
    f.write("\n".join(lines) + "\n")
with open(f"{ROOT}/analysis/multi.html", "w") as f:
    f.write("\n".join(h) + "\n")
with open(f"{ROOT}/analysis/multi.d2", "w") as f:
    f.write("\n".join(d2) + "\n")
wrote = "multi.json, multi.md, multi.html, multi.d2"
if shutil.which("d2"):
    for ext in ("png", "svg"):
        subprocess.run(["d2", f"{ROOT}/analysis/multi.d2", f"{ROOT}/analysis/multi.{ext}"],
                       check=True, capture_output=True)
    wrote += ", multi.png, multi.svg"
print(f"wrote analysis/: {wrote}")
