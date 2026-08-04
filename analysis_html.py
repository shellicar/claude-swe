"""HTML rendering for the cards.

`table.html` holds an HTML table rather than a markdown one. Markdown has no
colspan, and a card runs to nineteen columns: without merged headers every
column has to repeat its model name, so a row reads "Claude Opus 5 low |
Claude Opus 5 medium | Claude Opus 5 high | ..." and the families are
impossible to pick out. These cards are read rendered — and screenshotted —
never copied as text, so losing the plain-text table costs nothing.

Rules run VERTICALLY, between model families, never horizontally under each
row: what the eye needs is which model a column belongs to, and a line under
every one of forty rows buries exactly that.

One <style> block, classes on the cells. The rules were inline on every cell,
which put the same eighty characters on each of ~4,000 cells and made one card
130 KB — mostly the word "padding" repeated. GitHub strips <style> from README
prose but keeps it in a standalone file, and every local preview honours it.

The SVG/PNG path is unaffected: it builds its own markdown inside d2.
"""
import os

LEVELS = ("low", "medium", "high", "xhigh", "max")

# `g` marks the first column of a model family and carries the vertical rule;
# `t` marks the first row of a group and carries the rule above it.
STYLE = """<style>
.card { border-collapse: collapse }
.card th, .card td { padding: 3px 10px; text-align: left; white-space: nowrap }
.card th { font-weight: bold }
.card .g { border-left: 1px solid #888 }
.card .t { border-top: 1px solid #888 }
.card .h { border-bottom: 1px solid #888; border-top: 1px solid #888 }
.card .u { border-bottom: 1px solid #888 }
.card .s { vertical-align: middle }
</style>"""


def split_family(label):
    """(family, level) for a column labelled "<model> <level>".

    Effort levels are a closed set, so a trailing one is the level and the rest
    is the family. A column with no level — a model with no effort control —
    is its own family with nothing beneath it.
    """
    for level in LEVELS:
        if label.endswith(f" {level}"):
            return label[: -len(level) - 1], level
    return label, ""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cell(text):
    """Cell content, carrying over the little markdown these rows use."""
    out = esc(text)
    while out.count("**") >= 2:
        out = out.replace("**", "<b>", 1).replace("**", "</b>", 1)
    while out.count("*") >= 2:
        out = out.replace("*", "<i>", 1).replace("*", "</i>", 1)
    return out


def klass(*names):
    """A class attribute, or nothing at all when there is no class to give."""
    got = " ".join(n for n in names if n)
    return f' class="{got}"' if got else ""


def _grouped(body):
    """[(group, rows)] — rows carrying a "## X" divider start a new group.

    The divider stops being a row of its own and becomes a cell spanning the
    rows beneath it. Rows before any divider belong to an unnamed group.
    """
    groups, current, name = [], [], ""
    for label, cells in body:
        if label.startswith("## "):
            if current:
                groups.append((name, current))
            name, current = label[3:], []
            continue
        current.append((label, cells))
    if current:
        groups.append((name, current))
    return groups


def write(outdir, html):
    """Write a card's table.html, clearing the table.md this file used to be.

    Every card writer needs this, and each one that hand-rolled its own output
    kept a stale markdown copy beside the HTML until someone noticed.
    """
    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/table.html", "w") as f:
        f.write(html + "\n")
    stale = f"{outdir}/table.md"
    if os.path.exists(stale):
        os.remove(stale)


def table(heading, columns, sections, note):
    families = [split_family(c) for c in columns]
    has_levels = any(level for _f, level in families)

    # Consecutive columns of one family merge into a single header cell.
    groups = []
    for family, _level in families:
        if groups and groups[-1][0] == family:
            groups[-1][1] += 1
        else:
            groups.append([family, 1])

    # The first column of each family carries the vertical rule.
    starts, at = set(), 0
    for _family, n in groups:
        starts.add(at)
        at += n

    def header(label):
        """Families across, then their levels beneath — boxed as one block.

        The rule sits UNDER the level row, not under the family name: the two
        rows are one heading, so a line between them cuts a family off from
        the levels it owns.
        """
        span = 2 if has_levels else 1
        # colspan 2: the label area is the group column plus the row column.
        # It spans BOTH header rows, so its bottom edge is level with the rule
        # under the levels — it needs that border or the line starts partway
        # across the table with a gap on the left.
        rows = ["  <tr>",
                f'    <th rowspan="{span}" colspan="2" class="h">{cell(label)}</th>']
        # A family name only gets its bottom rule when there is no level row
        # beneath it to carry one.
        fam = "h" if not has_levels else "t"
        for family, n in groups:
            rows.append(f'    <th colspan="{n}"{klass(fam, "g")}>{esc(family)}</th>')
        rows.append("  </tr>")
        if has_levels:
            rows.append("  <tr>")
            for i, (_family, level) in enumerate(families):
                rows.append(f'    <th{klass("u", "g" if i in starts else "")}>'
                            f'{esc(level) or "&nbsp;"}</th>')
            rows.append("  </tr>")
        return rows

    # No table-wide <thead>: every section already carries the same family and
    # level rows, so a top one prints them twice. The card's own title moves
    # above the table rather than disappearing with it.
    out = [STYLE, f"<h3>{cell(heading)}</h3>", '<table class="card">']
    for title, body in sections:
        # Every section repeats the headers: the table is far too wide to read
        # a section against a header row scrolled off the top, and one section
        # is often all that gets shown.
        out += ["<tbody>", *header(title)]
        for g, (group, rows) in enumerate(_grouped(body)):
            # A rule between row groups — Results from Stats — since they are
            # different kinds of number, not a continuous list.
            for j, (label, cells) in enumerate(rows):
                edge = "t" if g and j == 0 else ""
                out.append("  <tr>")
                if not group:
                    # An ungrouped section — a TOTAL, a medal tally — has no
                    # word to put in the left column, so the label takes both
                    # rather than sitting beside an empty cell.
                    out.append(f'    <th colspan="2"{klass(edge)}>{cell(label)}</th>')
                else:
                    if j == 0:
                        # "Results" / "Stats" beside their rows rather than
                        # above them: as a full-width divider row it cost a
                        # blank line across every column to carry one word.
                        out.append(f'    <th rowspan="{len(rows)}"{klass("s", edge)}>'
                                   f"{cell(group)}</th>")
                    out.append(f'    <th{klass(edge)}>{cell(label)}</th>')
                for i, c in enumerate(cells):
                    out.append(f'    <td{klass("g" if i in starts else "", edge)}>'
                               f"{cell(c)}</td>")
                out.append("  </tr>")
        out.append("</tbody>")
    out += ["</table>", "", esc(note)]
    return "\n".join(out)
