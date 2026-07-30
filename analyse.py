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

from analysis_output import _medal_row, emit

MODELS = [  # display name -> dir
    ("Claude Fable 5", "fable-5"),
    ("Claude Fable 5 (2 Jul)", "fable-5-high-2026-07-02"),
    ("Claude Opus 5", "opus-5"),
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


def wire_thinking(dirn, base=None):
    """Per-set thinking tokens from the leg's own proxy capture, attributed to
    instances by first-user-message fingerprint (same hash the proxy uses).
    Returns None when the leg has no capture. `base` is the run out-path,
    defaulting to the model's main leg."""
    base = base or f"main/{dirn}"
    timing = f"{ROOT}/runs/{base}/api-timing.jsonl"
    if not os.path.exists(timing):
        return THINKING_LEGACY.get(dirn)
    conv2set = {}
    for s, _ in SETS:
        for tf in glob.glob(f"{ROOT}/runs/{base}/{s}/*/*.traj.json"):
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
    cost = steps = out = cr = cw = ncc = failed = 0
    wall = 0.0
    peak_ctx = 0  # largest single-turn context (prompt_tokens) seen, any instance
    for tf in glob.glob(f"{ROOT}/runs/{base}/{s}/*/*.traj.json"):
        t = json.load(open(tf))
        st = t["info"]["model_stats"]
        cost += st["instance_cost"]
        steps += st["api_calls"]
        prev = None
        for m in t["messages"]:
            ts = m.get("extra", {}).get("timestamp")
            # FormatError: the model's tool call was rejected before ever
            # reaching execution (bad shape, unknown tool, missing field).
            # Counted per rejected call, not per turn.
            if m.get("extra", {}).get("interrupt_type") == "FormatError":
                failed += m.get("extra", {}).get("n_actions", 1) or 1
            if m.get("role") == "assistant":
                u = (m.get("extra", {}).get("response") or {}).get("usage") or {}
                out += u.get("completion_tokens", 0) or 0
                p = u.get("prompt_tokens", 0) or 0
                r = u.get("cache_read_input_tokens", 0) or 0
                w = u.get("cache_creation_input_tokens", 0) or 0
                cr += r
                cw += w
                ncc += max(p - r - w, 0)
                peak_ctx = max(peak_ctx, p)
                if ts and prev:
                    wall += ts - prev
            if ts:
                prev = ts
    return dict(resolved=resolved, cost=cost, steps=steps, out=out, failed=failed,
               ncc=ncc, cr=cr, cw=cw, intot=ncc + cr + cw, wall=wall, peak_ctx=peak_ctx)


def per_instance(base, s):
    """{instance_id: (resolved, cost)} — the granularity leg() aggregates away."""
    rid = base.replace("/", "_")
    rep = glob.glob(f"{ROOT}/evals/*.runs_{rid}_{s}.json")[0]
    resolved = set(json.load(open(rep))["resolved_ids"])
    out = {}
    for tf in glob.glob(f"{ROOT}/runs/{base}/{s}/*/*.traj.json"):
        t = json.load(open(tf))
        iid = t["instance_id"]
        out[iid] = (iid in resolved, t["info"]["model_stats"]["instance_cost"])
    return out


def instance_medals(bases, sets=None):
    """Medals per INSTANCE, not per aggregate row: each instance is its own
    event. Resolving is the entry ticket — a competitor that failed cannot
    place, however cheap it was — and among the finishers the cheapest takes
    gold. An instance nobody resolved awards nothing to anyone.

    This shows what averages hide: a model can post the best $/resolved while
    rarely being the cheapest on any individual instance, if it is cheap on
    the easy majority.

    `bases` are run out-paths ("main/opus-5", "exec-arm-1/sonnet-5"), so the
    same contest works for model divisions and for scaffolding arms.
    """
    sets = sets or [s for s, _n in SETS]
    per = {}
    for b in bases:
        acc = {}
        for s in sets:
            try:
                acc.update(per_instance(b, s))
            except IndexError:
                pass  # leg never run or never marked
        per[b] = acc
    counts = {b: [0, 0, 0] for b in bases}
    unsolved = 0
    every = {i for b in bases for i in per[b]}
    for iid in sorted(every):
        finishers = sorted(
            (per[b][iid][1], b) for b in bases
            if per[b].get(iid, (False, 0.0))[0]
        )
        if not finishers:
            unsolved += 1
            continue
        for rank, (_cost, b) in enumerate(finishers[:3]):
            counts[b][rank] += 1
    return counts, unsolved, len(every)


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
    ("Steps (total)", lambda L, n: f"{L['steps']:,}"),
    ("Turns/instance (avg)", lambda L, n: f"{L['steps']/n:.1f}"),
    ("Cost/turn (avg)", lambda L, n: f"${L['cost']/L['steps']:.3f}"),
    ("Output tokens", lambda L, n: tok(L["out"])),
    ("Thinking (output)", None),  # special: needs dirn+set
    ("Input tokens", lambda L, n: tok(L["intot"])),
    ("\u2014 non-cached", lambda L, n: tok(L["ncc"])),
    ("\u2014 cache read", lambda L, n: tok(L["cr"])),
    ("\u2014 cache write", lambda L, n: tok(L["cw"])),
    ("Failed tool calls (FormatError)", lambda L, n: str(L["failed"])),
    ("Input tokens/turn (avg)", lambda L, n: f"{L['intot']/L['steps']:,.0f}"),
    ("Output tokens/turn (avg)", lambda L, n: f"{L['out']/L['steps']:,.0f}"),
    ("Context window (peak, single turn)", lambda L, n: tok(L["peak_ctx"])),
    ("Wall-clock (12-way parallel)", lambda L, n: f"{L['wall']/3600:.1f} h"),
]

def combined(d):
    c = {}
    for k in data[d]["standard"]:
        if k == "peak_ctx":  # a max, not a sum — combining two legs takes the larger
            c[k] = max(data[d]["standard"][k], data[d]["hard"][k])
        else:
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
     ["fable-5", "opus-5", "sonnet-5", "haiku-4-5"]),
    ("opus-models", "Opus division — the lineage (SWE-bench Verified)",
     ["opus-4-6", "opus-4-7", "opus-4-8", "opus-5"]),
    ("sonnet-models", "Sonnet division — the lineage (SWE-bench Verified)",
     ["sonnet-4-6", "sonnet-5"]),
]

for card, heading, dirs in GROUPS:
    payload = {"models": {d: {"name": name, "sets": data[d], "thinking": THINKING.get(d)}
                          for name, d in MODELS}}
    if card == "verified":
        payload["covers"] = ["standard", "hard"]
    emit(card, heading, [NAME[d] for d in dirs], sections_for(dirs), NOTE, payload,
         medals=instance_medals([f"main/{d}" for d in dirs]))


# Effort divisions: one card per model, read left-to-right as the effort curve.
# `high` is the model's DEFAULT-effort leg in main — the sweep deliberately
# omits it rather than running the same configuration twice. A model appears
# only once at least two of its levels have been run and marked, so a sweep in
# progress produces a partial curve instead of an error.
#
# The per-instance medals answer the question the aggregate rows cannot: does
# the extra spend ever buy the cheapest solve? An effort level that resolves
# more but never places is paying for results it could have had for less.
EFFORT_LEVELS = ["low", "medium", "high", "xhigh", "max"]
EFFORT_MODELS = ["opus-4-8", "opus-5", "sonnet-5", "fable-5"]


def effort_base(model, level):
    return f"main/{model}" if level == "high" else f"effort-sweep/{model}-{level}"


def _try_leg(base, s):
    try:
        return leg(base, s)
    except (IndexError, FileNotFoundError):
        return None


def effort_card(card, heading, entries):
    """One card from (label, base, thinking-dir) triples. Bases with no marked
    leg are dropped, so a sweep in progress yields a partial card rather than
    an error; fewer than two survivors means no contest and no card."""
    bases, labels, edata, think = [], [], {}, {}
    for label, base, tdir in entries:
        sets = {s: _try_leg(base, s) for s, _n in SETS}
        if all(sets.values()):
            bases.append(base)
            labels.append(label)
            edata[base] = sets
            think[base] = wire_thinking(tdir, base)
    if len(bases) < 2:
        return

    def esection(getter, n, tset):
        body = []
        for lab, fn in rows:
            if fn is None:  # thinking row
                cells = []
                for b in bases:
                    v = think.get(b)
                    if not v:
                        cells.append("—")
                    elif tset is None:
                        cells.append(tok(v["standard"] + v["hard"]))
                    else:
                        cells.append(tok(v[tset]))
                body.append((lab, cells))
                continue
            body.append((lab.format(n=n) if "{n}" in lab else lab,
                         [fn(getter(b), n) for b in bases]))
        return body

    def ecombined(b):
        c = {}
        for k in edata[b]["standard"]:
            if k == "peak_ctx":
                c[k] = max(edata[b]["standard"][k], edata[b]["hard"][k])
            else:
                c[k] = edata[b]["standard"][k] + edata[b]["hard"][k]
        return c

    sections = [
        ("Standard — 60 *Python* events (<1 h human effort)",
         esection(lambda b: edata[b]["standard"], 60, "standard")),
        ("Hard — 45 *Python* events (1+ h human effort)",
         esection(lambda b: edata[b]["hard"], 45, "hard")),
        ("Combined — 105 *Python* events",
         esection(lambda b: ecombined(b), 105, None)),
    ]
    emit(card, heading, labels, sections, NOTE,
         {"models": {b: {"name": lv, "sets": edata[b], "thinking": think.get(b)}
                     for b, lv in zip(bases, labels)}},
         medals=instance_medals(bases))


# Per model: the effort curve, read left-to-right.
for _model in EFFORT_MODELS:
    effort_card(
        f"effort-{_model}",
        f"Effort division — {NAME[_model]} (SWE-bench Verified)",
        [(lv, effort_base(_model, lv), _model) for lv in EFFORT_LEVELS],
    )

# Per effort level: every contender at the SAME setting. Comparing models at
# their defaults was fine while effort bought nothing (Opus 4.8), but Opus 5
# converts effort into resolves, so a single-level comparison now depends on
# which level you pick — these cards make the choice explicit instead.
for _lv in EFFORT_LEVELS:
    effort_card(
        f"effort-{_lv}",
        f"{_lv.capitalize()}-effort division — every contender (SWE-bench Verified)",
        [(NAME[m], effort_base(m, _lv), m) for m in EFFORT_MODELS],
    )


# Prompt-scaffolding division: does the imperative "MUST" scaffolding earn its
# keep, and does the submission ritual itself matter? BASH ONLY (native
# LitellmModel, no exec tool anywhere) — a different knob from the division
# above, sharing only the same control.
SCAFFOLD = [
    ("Sonnet 5 — bash (control)", "main/sonnet-5"),
    ("Sonnet 5 — minimal prompt (pen-down fallback)", "minimal-prompt/sonnet-5"),
    ("Sonnet 5 — no ritual (pen-down only)", "no-ritual/sonnet-5"),
    ("Sonnet 5 — exec tool, no ritual (pen-down only)", "exec-arm-2-no-ritual/sonnet-5"),
]
scaffold_data = {base: leg(base, "hard") for _, base in SCAFFOLD}


def scaffold_section(bases):
    body = []
    for label, fn in rows:
        if fn is None:
            body.append((label, ["—" for _ in bases]))
            continue
        body.append((label, [fn(scaffold_data[b], 45) for b in bases]))
    return body


_sbases = [b for _, b in SCAFFOLD]
emit("scaffold", "Prompt-scaffolding division (bash only) — SWE-bench Verified hard, Sonnet 5",
     [n for n, _ in SCAFFOLD],
     [("Hard — 45 *Python* events (1+ h human effort)", scaffold_section(_sbases))],
     NOTE,
     {"covers": ["hard"], "models": {b: {"name": n, "sets": {"hard": scaffold_data[b]}} for n, b in SCAFFOLD}},
     medals=instance_medals(_sbases, sets=["hard"]))


# Variable-row divisions: each entry is (label, base, {dim: value}). Rather than
# packing an arm's whole config into its column header, each dimension is its
# own row above Results — but SEPARATE EXPERIMENTS get SEPARATE tables/files.
# Control repeats across all of them on purpose: each table answers one
# question standalone, not "all arms ever run" in one wide sheet.
#
# Dims: tool (bash/ExecV1/V2/V3), name (what the tool is called in the prompt),
# encoding (raw string / JSON / plain-text variants), prompt, extra (decorative
# bloat or real Edit/Write/Read), submission (ritual vs pen-down), output
# (bash's raw text / exec's per-command block format / block flattened to plain).


def safe_leg(base, s):
    try:
        return leg(base, s)
    except IndexError:
        return None


VARIABLE_DIMS = [
    ("Shell tool", "tool"),
    ("Tool name shown to model", "name"),
    ("Input encoding", "encoding"),
    ("Prompt", "prompt"),
    ("Extra tools", "extra"),
    ("Submission", "submission"),
    ("Output format", "output"),
]


def experiment_table(heading, entries):
    """Build one markdown table (own header, own columns) for one experiment.
    Multiple of these get concatenated into ONE table.md — separate experiments,
    not separate files: control repeats across tables on purpose, but nobody
    reading exec-grammar results needs plain-text-encoding's columns in view."""
    data_ = {base: safe_leg(base, "hard") for _, base, _ in entries}
    bases = [b for _, b, _ in entries]
    columns = [n for n, _, _ in entries]
    variables_body = [(label, [v[key] for _, _, v in entries]) for label, key in VARIABLE_DIMS]
    results_body = []
    for label, fn in rows:
        if fn is None:
            results_body.append((label, ["—" for _ in bases]))
            continue
        results_body.append((label, [fn(data_[b], 45) if data_[b] else "—" for b in bases]))
    sections_ = [("Variables", variables_body), ("Hard — 45 *Python* events (1+ h human effort)", results_body)]
    sections_ = [(title, [(label, _medal_row(label, cells)) for label, cells in body]) for title, body in sections_]
    # Per-instance contest across the arms, same rules as the model divisions:
    # only arms that resolved an instance can place, cheapest takes gold.
    counts, unsolved, total = instance_medals(bases, sets=["hard"])
    if total:
        tally_body = []
        for i, (m, word) in enumerate(zip(("\U0001F947", "\U0001F948", "\U0001F949"),
                                          ("gold", "silver", "bronze"))):
            tally_body.append((f"{m} {word}", [str(counts[b][i]) for b in bases]))
        tally_body.append(("medals total", [str(sum(counts[b])) for b in bases]))
        sections_.append((
            f"Medal tally — per instance ({total} events, {unsolved} unsolved by every arm)",
            tally_body,
        ))
    lines = [f"| {heading} | " + " | ".join(columns) + " |", "|" + "---|" * (len(columns) + 1)]
    for title, body in sections_:
        lines.append(f"| **{title}** |" + " |" * len(columns))
        for label, cells in body:
            if label.startswith("## "):
                lines.append(f"| **{label[3:]}** |" + " |" * len(columns))
            else:
                lines.append(f"| {label} | " + " | ".join(cells) + " |")
    payload = {"models": {b: {"name": n, "sets": {"hard": data_[b]}} for n, b, _ in entries if data_[b]}}
    return "\n".join(lines), payload


_CONTROL = ("Control", "main/sonnet-5",
            dict(tool="bash", name="bash", encoding="raw string", prompt="bash", extra="—", submission="ritual", output="text"))

# Experiment 1: does the exec-tool GRAMMAR (structured JSON) alone beat bash,
# across tool generations and naming? Never mixed with real dedicated tools.
EXEC_GRAMMAR = [
    _CONTROL,
    ("Exec Arm 1", "exec-arm-1/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="JSON", prompt="bash (mismatched)", extra="—", submission="ritual", output="block")),
    ("ExecV1, aligned", "execv1-arm2/sonnet-5",
     dict(tool="ExecV1", name="bash", encoding="JSON", prompt="exec-aligned", extra="—", submission="ritual", output="block")),
    ("ExecV2, aligned", "execv2-arm2/sonnet-5",
     dict(tool="ExecV2", name="bash", encoding="JSON", prompt="exec-aligned", extra="—", submission="ritual", output="block")),
    ("ExecV3, aligned (bash-named)", "exec-arm-2/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="JSON", prompt="exec-aligned", extra="—", submission="ritual", output="block")),
    ("ExecV3, aligned (exec-named)", "exec-arm-3/sonnet-5",
     dict(tool="ExecV3", name="exec", encoding="JSON", prompt="exec-aligned", extra="—", submission="ritual", output="block")),
    ("ExecV3, no ritual", "exec-arm-2-no-ritual/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="JSON", prompt="exec-aligned", extra="—", submission="pen-down", output="block")),
]
_t1, _p1 = experiment_table("Exec-grammar division — SWE-bench Verified hard, Sonnet 5", EXEC_GRAMMAR)

# Experiment 2: does the SCHEMA alone move the needle — pure bloat, real
# dedicated tools (neutral / prompted to prefer), and swapping bash itself for
# ExecV3 once those dedicated tools already exist alongside it.
TOOL_ALTERNATIVES = [
    _CONTROL,
    ("+90 bloat tools", "tools-arm-1/sonnet-5",
     dict(tool="bash", name="bash", encoding="raw string", prompt="bash", extra="+90 unusable", submission="ritual", output="text")),
    ("+Edit/Write/Read, neutral", "tools-arm-2/sonnet-5",
     dict(tool="bash", name="bash", encoding="raw string", prompt="bash", extra="Edit/Write/Read", submission="ritual", output="text")),
    ("+Edit/Write/Read, prefer", "tools-arm-3/sonnet-5",
     dict(tool="bash", name="bash", encoding="raw string", prompt="bash + prefer", extra="Edit/Write/Read", submission="ritual", output="text")),
    ("ExecV3 +Edit/Write/Read", "tools-arm-4/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="JSON", prompt="bash + prefer", extra="Edit/Write/Read", submission="ritual", output="block")),
    ("ExecV3 +EWR, plain output", "tools-arm-5/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="JSON", prompt="bash + prefer", extra="Edit/Write/Read", submission="ritual", output="plain")),
]
_t2, _p2 = experiment_table("Tool-alternatives division — SWE-bench Verified hard, Sonnet 5", TOOL_ALTERNATIVES)

# Experiment 3: does the exec tool's plain-text ENCODING (vs JSON) change
# anything — symbolic (bash-lookalike operators/redirects), the same grammar
# with loud named rejections, and a keyword grammar sharing no symbols with bash.
PLAIN_TEXT_ENCODING = [
    _CONTROL,
    ("ExecV3, plain-text (symbolic)", "exec-arm-4/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="text (symbolic)", prompt="text-aligned", extra="—", submission="ritual", output="block")),
    ("ExecV3, plain-text (symbolic, loud)", "exec-arm-5/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="text (symbolic)", prompt="text-aligned + loud", extra="—", submission="ritual", output="block")),
    ("ExecV3, plain-text (keyword)", "exec-arm-6/sonnet-5",
     dict(tool="ExecV3", name="bash", encoding="text (keyword)", prompt="keyword-aligned", extra="—", submission="ritual", output="block")),
]
_t3, _p3 = experiment_table("Plain-text encoding division — SWE-bench Verified hard, Sonnet 5", PLAIN_TEXT_ENCODING)

# One file, three separate tables — not three directories. Each keeps its own
# header/columns; they're stacked, not merged into one wide sheet.
os.makedirs(f"{ROOT}/analysis/tools", exist_ok=True)
with open(f"{ROOT}/analysis/tools/table.md", "w") as f:
    f.write(_t1 + "\n\n" + NOTE + "\n\n" + _t2 + "\n\n" + NOTE + "\n\n" + _t3 + "\n\n" + NOTE + "\n")
with open(f"{ROOT}/analysis/tools/data.json", "w") as f:
    json.dump({"exec-grammar": _p1, "tool-alternatives": _p2, "plain-text-encoding": _p3}, f, indent=2)
print("wrote analysis/tools/: data.json, table.md")
