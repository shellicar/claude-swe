"""Shared output writer for every analyser.

One call writes one dataset's folder — three files, no more:

    analysis/<name>/
        data.json     the raw figures (the overview joins these)
        table.md      the table as text
        <name>.svg    the rendered card

<name>.d2 is the render intermediate, regenerated every run and gitignored.

HEADLINE rows — Resolved, Resolved %, Total cost, $/resolved — get their best
cell bolded: highest wins on resolve rows, lowest on cost rows; ties all bold.
Everything else is information, not headline.

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


def _bold_best(label, cells):
    higher = HEADLINE.get(label.strip())
    if higher is None:
        return cells
    values = [_numeric(c) for c in cells]
    present = [v for v in values if v is not None]
    if len(present) < 2:
        return cells
    best = max(present) if higher else min(present)
    return [f"**{c}**" if v == best else c for c, v in zip(cells, values)]


def emit(name, heading, columns, sections, note, payload):
    outdir = f"{ROOT}/analysis/{name}"
    os.makedirs(outdir, exist_ok=True)

    with open(f"{outdir}/data.json", "w") as f:
        json.dump(payload, f, indent=2)

    sections = [(title, [(label, _bold_best(label, cells)) for label, cells in body])
                for title, body in sections]

    # markdown
    lines = [f"| {heading} | " + " | ".join(columns) + " |", "|" + "---|" * (len(columns) + 1)]
    for title, body in sections:
        lines.append(f"| **{title}** |" + " |" * len(columns))
        for label, cells in body:
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
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
            d2.append(f"  | {label} | " + " | ".join(cells) + " |")
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
