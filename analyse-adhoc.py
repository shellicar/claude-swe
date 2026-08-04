#!/usr/bin/env python3
"""The ad-hoc card: legs run with --model rather than through a combination.

`runs/adhoc/` is where a one-off lands — a new contender's first smoke test.
A handful of instances says little on its own, so each instance is shown
against every contender that has already run it: the meet legs supply the
baseline, and a cell is only comparable because it is the same event.

Rows are instances, columns are contenders. Each cell is verdict and cost.
"""
import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
ADHOC = f"{ROOT}/runs/adhoc"
ROSTER = json.load(open(f"{ROOT}/models.json"))["models"]
NAME = {m["dir"]: m["name"].replace("Claude ", "") for m in ROSTER}


def selection_of(instance):
    for sel in ("standard", "hard"):
        ids = {l.strip() for l in open(f"{ROOT}/instances-{sel}.txt") if l.strip()}
        if instance in ids:
            return sel
    return None


def verdicts(rid, sel):
    rep = glob.glob(f"{ROOT}/evals/*.runs_{rid}_{sel}.json")
    return set(json.load(open(rep[0]))["resolved_ids"]) if rep else None


def cost_of(base, sel, instance):
    tf = f"{ROOT}/runs/{base}/{sel}/{instance}/{instance}.traj.json"
    if not os.path.exists(tf):
        return None
    return json.load(open(tf))["info"]["model_stats"]["instance_cost"]


def cell(base, rid, sel, instance):
    c = cost_of(base, sel, instance)
    if c is None:
        return "—"
    res = verdicts(rid, sel)
    mark = "unmarked" if res is None else ("**resolved**" if instance in res else "no")
    return f"{mark} ${c:.3f}"


def thinking_tokens(usage):
    """Reasoning tokens under whichever name the provider uses — Anthropic's
    output_tokens_details.thinking_tokens or OpenAI-shaped
    completion_tokens_details.reasoning_tokens."""
    return (
        (usage.get("output_tokens_details") or {}).get("thinking_tokens")
        or (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
        or 0
    )


def wire_totals(leg, program):
    """Thinking tokens and call count for ONE program of a leg.

    A leg writes a single api-timing.jsonl across every program it ran, so
    totalling the file would report the same numbers under each — double
    counting. Calls carry the proxy's `conv` fingerprint (sha256 of the first
    user message), and each trajectory contains that same message, so the two
    can be matched back to the program that produced them.
    """
    timing = f"{ADHOC}/{leg}/api-timing.jsonl"
    if not os.path.exists(timing):
        return None
    mine = set()
    for tf in glob.glob(f"{ADHOC}/{leg}/{program}/*/*.traj.json"):
        t = json.load(open(tf))
        first = next((m for m in t["messages"] if m.get("role") == "user"), None)
        if not first:
            continue
        c = first["content"]
        text = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c)
        mine.add(hashlib.sha256(text.encode()).hexdigest()[:12])
    calls = think = 0
    for line in open(timing):
        d = json.loads(line)
        if d.get("status") != 200 or d.get("conv") not in mine:
            continue
        calls += 1
        think += thinking_tokens(d.get("usage") or {})
    return {"calls": calls, "thinking": think} if calls else None


def model_of(preds_path):
    """The leg's own model, from what it recorded rather than its directory.
    Run directories drop the vendor's `claude-` prefix, so the recorded name
    has to be normalised the same way or the roster lookup misses and the
    column shows a raw model id."""
    data = json.load(open(preds_path))
    for v in data.values():
        name = v.get("model_name_or_path", "")
        return name.split("/")[-1].removeprefix("claude-")
    return None


sections = []
for leg in sorted(os.listdir(ADHOC)) if os.path.isdir(ADHOC) else []:
    for preds in sorted(glob.glob(f"{ADHOC}/{leg}/*/preds.json")):
        sel = os.path.basename(os.path.dirname(preds))
        instances = sorted(json.load(open(preds)).keys())
        if not instances:
            continue
        own = model_of(preds)
        # The leg's own model is the first column; it must not appear again as
        # a comparison column, where it would be empty by definition — an
        # ad-hoc leg is precisely a model that has not run the meet.
        others = [m for m in ROSTER if m["dir"] != own]
        body = []
        for i in instances:
            meet_sel = selection_of(i)
            row = [cell(f"adhoc/{leg}", f"adhoc_{leg}", sel, i)]
            for m in others:
                row.append(cell(f"main/{m['dir']}", f"main_{m['dir']}", meet_sel, i)
                           if meet_sel else "—")
            body.append((i, row))
        sections.append((f"{leg} / {sel}", body, own, others))

def projection(leg, sel, instances):
    """What a full meet would cost this leg, scaled off the contenders.

    A few instances cannot be multiplied up naively — a smoke set is not a
    random sample, and cost per instance varies hugely by program. But every
    contender has run BOTH these instances and the whole meet, so each one
    yields a ratio (its full-program cost / its cost on these same instances).
    The median ratio applied to the ad-hoc leg's spend is an estimate grounded
    in observed behaviour rather than arithmetic on three points.

    Still an estimate: it assumes the new model's cost scales across the
    program like the contenders' does, which a cheaper-but-more-verbose model
    would break.
    """
    own = sum(c for c in (cost_of(f"adhoc/{leg}", sel, i) for i in instances)
              if c is not None)
    if not own:
        return None
    out = {}
    for program, n in (("standard", 60), ("hard", 45)):
        ratios = []
        for m in ROSTER:
            d = m["dir"]
            here = [cost_of(f"main/{d}", selection_of(i), i) for i in instances]
            here = [c for c in here if c is not None]
            if len(here) != len(instances):
                continue
            full = [cost_of(f"main/{d}", program, os.path.basename(p))
                    for p in glob.glob(f"{ROOT}/runs/main/{d}/{program}/*")]
            full = [c for c in full if c is not None]
            if len(full) < n:
                continue
            ratios.append(sum(full) / sum(here))
        if ratios:
            ratios.sort()
            out[program] = own * ratios[len(ratios) // 2]
    return out


if sections:
    # Each ad-hoc leg gets its own table: its comparison columns depend on
    # which model it is.
    lines = []
    for title, body, own, others in sections:
        columns = [NAME.get(own, own or "ad-hoc leg")] + [NAME[m["dir"]] for m in others]
        lines += [f"| {title} | " + " | ".join(columns) + " |",
                  "|" + "---|" * (len(columns) + 1)]
        for label, cells in body:
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
        w = wire_totals(*title.split(" / "))
        if w:
            lines.append(f"| _wire capture_ | {w['calls']} calls, "
                         f"{w['thinking']:,} thinking tokens |"
                         + " |" * (len(columns) - 1))
        lines.append("")
    lines += ["", "Same event, so the cells compare directly; the ad-hoc leg's own "
              "program is not a meet's full program, so its RATE does not."]

    proj_rows = []
    for leg in sorted(os.listdir(ADHOC)) if os.path.isdir(ADHOC) else []:
        for preds in sorted(glob.glob(f"{ADHOC}/{leg}/*/preds.json")):
            sel = os.path.basename(os.path.dirname(preds))
            instances = sorted(json.load(open(preds)).keys())
            p = projection(leg, sel, instances)
            if p:
                std, hard = p.get("standard"), p.get("hard")
                both = (std or 0) + (hard or 0)
                proj_rows.append(
                    f"| {leg} / {sel} | {len(instances)} | "
                    f"{'$%.2f' % std if std else '—'} | "
                    f"{'$%.2f' % hard if hard else '—'} | "
                    f"{'$%.2f' % both if both else '—'} |")
    if proj_rows:
        lines += [
            "", "## Projected cost of a full meet", "",
            "Scaled by the median of every contender's own "
            "(full-program cost / cost on these same instances) ratio.", "",
            "| ad-hoc leg | sampled | standard (60) | hard (45) | verified (105) |",
            "|---|---|---|---|---|",
            *proj_rows,
        ]

    outdir = f"{ROOT}/analysis/adhoc"
    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/table.html", "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(f"{outdir}/data.json", "w") as f:
        json.dump({t: dict(b) for t, b, _o, _x in sections}, f, indent=2)
    print("wrote analysis/adhoc/: data.json, table.html")
