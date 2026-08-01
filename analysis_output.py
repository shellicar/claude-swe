"""Shared output writer for every analyser.

One call writes one dataset's folder — three files, no more:

    analysis/<name>/
        data.json     the raw figures (the overview joins these)
        table.md      the table as text
        <name>.svg    the rendered card
        <name>.png    the same card for pasting into chat (SVG pastes as text)

<name>.d2 is the render intermediate, regenerated every run and gitignored.

HEADLINE rows — Resolved, Resolved %, Total cost, $/resolved — get medals by
rank (🥇🥈🥉 are the colour d2's md tables cannot give a cell): highest wins on
resolve rows, lowest on cost rows; tied values share a medal. Medals sit
BEFORE the value so the text stays aligned; gold is also bold.

Rows whose label starts with "## " render as bold group dividers (Results /
Stats) — the visual hierarchy inside a section.

A medal tally (the Olympics table: golds, silvers, bronzes per model) is
appended automatically, split per discipline — Resolved, Total cost,
$/resolved — counting every medalled row outside TOTAL sections and
'## …total…' groups (aggregates would double-weight the contests they
summarise). Resolved % is excluded: within a group it always medals
identically to Resolved.

sections: list of (title, body) where body is a list of (row label, [cell per
column]). All cells must be one-line strings: d2 mis-measures wrapped cells
and clips the table bottom (see docs/diagrams/model-comparison.d2).
"""

import json
import os
import re
import shutil
import subprocess

import analysis_html

ROOT = os.path.dirname(os.path.abspath(__file__))

# Medals mark contest outcomes: only Resolved (and its % twin) medal. Cost
# rows are statistics, not contests — best figure bolded, never medalled:
# cheapness is a property of the price list, and $/resolved is a ratio a
# contender can top while losing nearly every event.
MEDALLED = {"Resolved": True, "Resolved %": True}
BOLD_BEST = {"Total cost": False, "$/resolved": False}


def _numeric(cell):
    m = re.search(r"-?\d[\d,]*\.?\d*", cell.replace("\u00a0", " "))
    return float(m.group().replace(",", "")) if m else None


def _medal_row(label, cells):
    key = label.strip()
    values = [_numeric(c) for c in cells]
    if key in BOLD_BEST:
        # cost rows rank 1/2/3 with the same medal emojis (lowest wins) — the
        # tally ignores them: it counts Resolved rows only, so no one collects
        # tally medals for being cheap while failing.
        present = sorted({v for v in values if v is not None})
        if len(present) < 2:
            return cells
        mark_for = {v: m for v, m in zip(present, ("🥇", "🥈", "🥉"))}
        out = []
        for c, v in zip(cells, values):
            mark = mark_for.get(v)
            if mark == "🥇":
                out.append(f"{mark} **{c}**")
            elif mark:
                out.append(f"{mark} {c}")
            else:
                out.append(c)
        return out
    higher = MEDALLED.get(key)
    if higher is None:
        return cells
    present = sorted({v for v in values if v is not None}, reverse=higher)
    if len(present) < 2:
        return cells
    medal_for = {v: m for v, m in zip(present, ("\U0001F947", "\U0001F948", "\U0001F949"))}
    out = []
    for c, v in zip(cells, values):
        medal = medal_for.get(v)
        if medal == "\U0001F947":
            out.append(f"{medal}\u00a0**{c}**")
        elif medal:
            out.append(f"{medal}\u00a0{c}")
        else:
            out.append(c)
    return out


def emit(name, heading, columns, sections, note, payload, medals=None):
    outdir = f"{ROOT}/analysis/{name}"
    os.makedirs(outdir, exist_ok=True)

    with open(f"{outdir}/data.json", "w") as f:
        json.dump(payload, f, indent=2)

    def render_row(label, cells):
        # "## X" rows are group dividers: bold label, blank cells
        if label.startswith("## "):
            return f"| **{label[3:]}** |" + " |" * len(columns)
        return f"| {label} | " + " | ".join(cells) + " |"

    sections = [(title, [(label, _medal_row(label, cells)) for label, cells in body])
                for title, body in sections]

    # medal tally, split per discipline and WEIGHTED BY EVENTS: a gold on a
    # 44-event program outweighs a gold on an 11-event one. The weight is the
    # event count parsed from the program's header. Aggregates are excluded —
    # TOTAL sections and rows under a '## …total…' divider summarise contests
    # already counted. Resolved % is skipped: it medals identically to
    # Resolved within every group. Divisions never share a tally: each card
    # tallies only its own columns.
    import re as _re

    def _events_in(text):
        m = _re.search(r"\((?:all\s+)?(\d+)(?:\s+of\s+\d+)?(?:\s+events)?\)", text)
        if not m:
            m = _re.search(r"(\d+)\s+(?:\*\w+\*\s+)?events", text)
        return int(m.group(1)) if m else 1

    MEDALS = ("\U0001F947", "\U0001F948", "\U0001F949")
    # Per-INSTANCE medals when the caller computed them: every instance is its
    # own event, resolving is the entry ticket, cheapest finisher takes gold.
    if medals:
        counts, unsolved, total = medals
        keys = list(counts)
        body = []
        for i, (m, word) in enumerate(zip(MEDALS, ("gold", "silver", "bronze"))):
            body.append((f"{m} {word}", [str(counts[d][i]) for d in keys]))
        # Placing by the Olympic rule: golds first, silvers then bronzes only
        # as tie-breakers — one gold outranks any number of silvers. Gold here
        # means "solved it cheapest", so it is the column that carries the
        # contest; a total-medals count would mostly restate Resolved.
        order = sorted(keys, key=lambda d: tuple(-n for n in counts[d]))
        placing = {}
        rank = 0
        for i, d in enumerate(order):
            if i and counts[d] != counts[order[i - 1]]:
                rank = i
            placing[d] = rank
        body.append(("placing", [
            f"{MEDALS[placing[d]]}\u00a0**{placing[d] + 1}**" if placing[d] < 3
            else str(placing[d] + 1)
            for d in keys
        ]))
        heading_row = (
            f"Medal tally — per instance ({total} events, "
            f"{unsolved} unsolved by every model)"
        )
        sections = sections + [(heading_row, body)]
    else:
        DISCIPLINES = ("Resolved",)
        tally = {d: {m: [0] * len(columns) for m in MEDALS} for d in DISCIPLINES}
        for title, body in sections:
            if title.startswith("TOTAL"):
                continue
            weight = _events_in(title)
            in_total_group = False
            for label, cells in body:
                if label.startswith("## "):
                    in_total_group = "total" in label.lower()
                    if not in_total_group:
                        weight = _events_in(label)
                    continue
                if in_total_group or label.strip() not in tally:
                    continue
                for i, c in enumerate(cells):
                    for m in MEDALS:
                        if m in c:
                            tally[label.strip()][m][i] += weight
        if any(any(v) for d in tally.values() for v in d.values()):
            body = []
            for m, word in zip(MEDALS, ("gold", "silver", "bronze")):
                body.append((f"{m} {word}", [str(n) for n in tally["Resolved"][m]]))
            sections = sections + [("Medal tally — counted in events", body)]

    # HTML, not a markdown table — see analysis_html for why.
    with open(f"{outdir}/table.md", "w") as f:
        f.write(analysis_html.table(heading, columns, sections, note) + "\n")

    # d2 (intermediate) -> <name>.svg. One md table per section: a single long
    # table gets mis-measured and clipped; the blank last row is sacrificial.
    # No '$' in the note: d2 parses $ in quoted labels as a substitution.
    d2 = ["vars: { d2-config: { theme-id: 200 } }", "",
          f'title: "{heading}" {{ near: top-center; shape: text; style.font-size: 22; style.bold: true }}', ""]
    prev = None
    for idx, (title, body) in enumerate(sections):
        node = f"section{idx}"
        d2.append(f"{node}: |||md")
        d2.append(f"  | {title} | " + " | ".join(columns) + " |")
        d2.append("  |" + "---|" * (len(columns) + 1))
        for label, cells in body:
            d2.append("  " + render_row(label, cells))
        d2.append("  | " + " | " * (len(columns) + 1))
        d2.append("|||")
        if prev is not None:
            d2.append(f"{prev} -> {node}: {{style.opacity: 0}}")
        prev = node
    safe_note = note.replace("$", "")
    d2.append(f'note: "{safe_note}" {{ near: bottom-center; shape: text; style.font-color: "#7F8C8D" }}')
    with open(f"{outdir}/{name}.d2", "w") as f:
        f.write("\n".join(d2) + "\n")

    # tidy the superseded forms so each folder holds exactly the three files
    for stale in ("table.html", "table.png", "table.d2", "table.svg"):
        p = f"{outdir}/{stale}"
        if os.path.exists(p):
            os.remove(p)

    written = "data.json, table.md"
    if shutil.which("d2"):
        for ext in ("svg", "png"):
            subprocess.run(["d2", f"{outdir}/{name}.d2", f"{outdir}/{name}.{ext}"],
                           check=True, capture_output=True)
        written += f", {name}.svg, {name}.png"
    print(f"wrote analysis/{name}/: {written}")
