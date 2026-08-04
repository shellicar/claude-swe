"""Shared output writer for every analyser.

One call writes one dataset's folder — three files, no more:

    analysis/<name>/
        data.json     the raw figures (the overview joins these)
        table.html      the table as text
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
import medals as medals_mod

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


def emit(name, heading, columns, sections, note, payload, medals=None,
         medals_by_section=None):
    """`medals_by_section` maps a section title to its own tally.

    A tally belongs to a RESULT TABLE — one set of columns compared over one
    subject — not to a file. A meet's card is one result table (contenders over
    a program), so one tally covers it. An experiment's card holds one result
    table per contender (control against variation, that contender against
    itself), so a single card-wide tally would be comparing one contender's
    control with another's variation, which is not a contest anyone entered.
    """
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

    if medals_by_section:
        # Each result table carries its own tally, immediately after it.
        expanded = []
        for title, body in sections:
            expanded.append((title, body))
            got = medals_by_section.get(title)
            if not got:
                continue
            counts, unsolved, total = got
            # No placing row: with two conditions it would only restate gold.
            expanded.append((
                f"{title} — {medals_mod.heading('condition', total, unsolved)}",
                medals_mod.rows(counts, list(counts), placing=False)))
        sections = expanded

    # medal tally, split per discipline and WEIGHTED BY EVENTS: a gold on a
    # 44-event program outweighs a gold on an 11-event one. The weight is the
    # ONE medal system, in medals.py: every instance is an event, resolving is
    # the entry ticket, the cheapest finisher takes gold. A card either passes
    # a tally computed that way or shows none. There used to be a third path
    # here that counted the medal glyphs decorating aggregate rows and weighted
    # them by an event count parsed out of the section heading with a regex,
    # silently falling back to 1 when the heading did not match — a different
    # quantity wearing the same emoji.
    if medals:
        counts, unsolved, total = medals
        keys = list(counts)
        sections = sections + [
            (medals_mod.heading("model", total, unsolved),
             medals_mod.rows(counts, keys))]

    # HTML, not a markdown table — see analysis_html for why.
    with open(f"{outdir}/table.html", "w") as f:
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

    # tidy superseded forms: the generic table.* names an older layout wrote,
    # and table.md from when this file held markdown rather than HTML.
    for stale in ("table.md", "table.png", "table.d2", "table.svg"):
        p = f"{outdir}/{stale}"
        if os.path.exists(p):
            os.remove(p)

    written = "data.json, table.html"
    if shutil.which("d2"):
        for ext in ("svg", "png"):
            subprocess.run(["d2", f"{outdir}/{name}.d2", f"{outdir}/{name}.{ext}"],
                           check=True, capture_output=True)
        written += f", {name}.svg, {name}.png"
    print(f"wrote analysis/{name}/: {written}")
