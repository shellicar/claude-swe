"""Shared output writer for every analyser.

One call writes one dataset's folder — three files, no more:

    analysis/<name>/
        data.json     the raw figures (the overview joins these)
        table.md      the table as text
        <name>.svg    the rendered card

<name>.d2 is the render intermediate, regenerated every run and gitignored.

HEADLINE rows — Resolved, Resolved %, Total cost, $/resolved — get medals by
rank (🥇🥈🥉 are the colour d2's md tables cannot give a cell): highest wins on
resolve rows, lowest on cost rows; tied values share a medal. Medals sit
BEFORE the value so the text stays aligned; gold is also bold.

Rows whose label starts with "## " render as bold group dividers (Results /
Stats) — the visual hierarchy inside a section.

A medal tally (the Olympics table: golds, silvers, bronzes per model) is
appended automatically, counting every medalled row outside TOTAL sections —
aggregate rows would double-weight the contests they summarise.

sections: list of (title, body) where body is a list of (row label, [cell per
column]). All cells must be one-line strings: d2 mis-measures wrapped cells
and clips the table bottom (see docs/diagrams/model-comparison.d2).
"""

import json
import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# headline rows get best-cell bolding; True = higher is better
HEADLINE = {"Resolved": True, "Resolved %": True, "Total cost": False, "$/resolved": False}


def _numeric(cell):
    m = re.search(r"-?\d[\d,]*\.?\d*", cell.replace("\u00a0", " "))
    return float(m.group().replace(",", "")) if m else None


def _medal_row(label, cells):
    higher = HEADLINE.get(label.strip())
    if higher is None:
        return cells
    values = [_numeric(c) for c in cells]
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


def emit(name, heading, columns, sections, note, payload):
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

    # medal tally: count each column's medals across the contests. Aggregates
    # are excluded — TOTAL sections and rows under a '## …total…' divider
    # summarise contests already counted.
    tally = {m: [0] * len(columns) for m in ("\U0001F947", "\U0001F948", "\U0001F949")}
    for title, body in sections:
        if title.startswith("TOTAL"):
            continue
        in_total_group = False
        for label, cells in body:
            if label.startswith("## "):
                in_total_group = "total" in label.lower()
                continue
            if in_total_group:
                continue
            for i, c in enumerate(cells):
                for m in tally:
                    if m in c:
                        tally[m][i] += 1
    if any(any(v) for v in tally.values()):
        sections = sections + [("Medal tally", [
            ("\U0001F947 gold", [str(n) for n in tally["\U0001F947"]]),
            ("\U0001F948 silver", [str(n) for n in tally["\U0001F948"]]),
            ("\U0001F949 bronze", [str(n) for n in tally["\U0001F949"]]),
        ])]

    # markdown
    lines = [f"| {heading} | " + " | ".join(columns) + " |", "|" + "---|" * (len(columns) + 1)]
    for title, body in sections:
        lines.append(f"| **{title}** |" + " |" * len(columns))
        for label, cells in body:
            lines.append(render_row(label, cells))
    lines += ["", note]
    with open(f"{outdir}/table.md", "w") as f:
        f.write("\n".join(lines) + "\n")

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
        subprocess.run(["d2", f"{outdir}/{name}.d2", f"{outdir}/{name}.svg"],
                       check=True, capture_output=True)
        written += f", {name}.svg"
    print(f"wrote analysis/{name}/: {written}")
