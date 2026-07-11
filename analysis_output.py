"""Shared output writer for every analyser.

One call writes one dataset's folder:

    analysis/<name>/
        data.json    the raw figures (the overview joins these)
        table.md     the table as text
        table.html   the table in a browser
        table.png    the table as an image (the paste-into-chat form)

table.d2 / table.svg are render intermediates, regenerated every run and
gitignored. Every analyser produces the same four files with the same names —
that uniformity is the point (the flat six-format soup this replaces was
unreadable).

sections: list of (title, body) where body is a list of (row label, [cell per
column]). All cells must be one-line strings: d2 mis-measures wrapped cells
and clips the table bottom (see docs/diagrams/model-comparison.d2).
"""

import html as html_mod
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))


def emit(name, heading, columns, sections, note, payload):
    outdir = f"{ROOT}/analysis/{name}"
    os.makedirs(outdir, exist_ok=True)

    with open(f"{outdir}/data.json", "w") as f:
        json.dump(payload, f, indent=2)

    # markdown
    lines = [f"| {heading} | " + " | ".join(columns) + " |", "|" + "---|" * (len(columns) + 1)]
    for title, body in sections:
        lines.append(f"| **{title}** |" + " |" * len(columns))
        for label, cells in body:
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines += ["", note]
    with open(f"{outdir}/table.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    # html
    h = [f"<!doctype html><meta charset='utf-8'><title>{html_mod.escape(heading)}</title>",
         "<style>body{background:#1b1b2b;color:#e8e8f0;font:14px -apple-system,sans-serif;padding:2em}",
         "table{border-collapse:collapse}td,th{border:1px solid #555;padding:.35em .8em;text-align:left}",
         "th{background:#2a2a3f}td.sec{background:#2a2a3f;font-weight:bold}</style>",
         f"<table><tr><th>{html_mod.escape(heading)}</th>" + "".join(f"<th>{html_mod.escape(c)}</th>" for c in columns) + "</tr>"]
    for title, body in sections:
        h.append(f"<tr><td class='sec' colspan='{len(columns) + 1}'>{html_mod.escape(title)}</td></tr>")
        for label, cells in body:
            h.append("<tr><td>" + html_mod.escape(label) + "</td>" + "".join(f"<td>{html_mod.escape(c)}</td>" for c in cells) + "</tr>")
    h.append(f"</table><p>{html_mod.escape(note)}</p>")
    with open(f"{outdir}/table.html", "w") as f:
        f.write("\n".join(h) + "\n")

    # d2 (intermediate) -> png/svg. One md table per section: a single long
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
    with open(f"{outdir}/table.d2", "w") as f:
        f.write("\n".join(d2) + "\n")

    written = "data.json, table.md, table.html"
    if shutil.which("d2"):
        for ext in ("png", "svg"):
            subprocess.run(["d2", f"{outdir}/table.d2", f"{outdir}/table.{ext}"],
                           check=True, capture_output=True)
        written += ", table.png"
    print(f"wrote analysis/{name}/: {written}")
