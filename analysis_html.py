"""HTML rendering for the cards.

`table.md` holds an HTML table rather than a markdown one. Markdown has no
colspan, and a card runs to nineteen columns: without merged headers every
column has to repeat its model name, so a row reads "Claude Opus 5 low |
Claude Opus 5 medium | Claude Opus 5 high | ..." and the families are
impossible to pick out. These cards are read rendered — and screenshotted —
never copied as text, so losing the plain-text table costs nothing.

Rules run VERTICALLY, between model families, never horizontally under each
row: what the eye needs is which model a column belongs to, and a line under
every one of forty rows buries exactly that. Styling is inline rather than in
a <style> block, because several markdown previews strip the block.

The SVG/PNG path is unaffected: it builds its own markdown inside d2.
"""
LEVELS = ("low", "medium", "high", "xhigh", "max")

RULE = "1px solid #888"
TD = "padding:3px 10px;text-align:left;white-space:nowrap;border:none"
GROUP = f"{TD};border-left:{RULE}"



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
        base = f"{TD};font-weight:bold;border-top:{RULE}"
        span = 2 if has_levels else 1
        bottom = "" if has_levels else f";border-bottom:{RULE}"
        # colspan 2: the label area is the group column plus the row column.
        # It spans BOTH header rows, so its bottom edge is level with the rule
        # under the levels — it needs that border or the line starts partway
        # across the table with a gap on the left.
        rows = ["  <tr>",
                f'    <th rowspan="{span}" colspan="2" '
                f'style="{base};border-bottom:{RULE}">{cell(label)}</th>']
        for family, n in groups:
            rows.append(f'    <th colspan="{n}" '
                        f'style="{base}{bottom};border-left:{RULE}">{esc(family)}</th>')
        rows.append("  </tr>")
        if has_levels:
            rows.append("  <tr>")
            for i, (_family, level) in enumerate(families):
                s = f"{TD};font-weight:bold;border-bottom:{RULE}"
                if i in starts:
                    s += f";border-left:{RULE}"
                rows.append(f'    <th style="{s}">{esc(level) or "&nbsp;"}</th>')
            rows.append("  </tr>")
        return rows

    # No table-wide <thead>: every section already carries the same family and
    # level rows, so a top one prints them twice. The card's own title moves
    # above the table rather than disappearing with it.
    out = [f"<h3>{cell(heading)}</h3>", '<table style="border-collapse:collapse">']
    for title, body in sections:
        # Every section repeats the headers: the table is far too wide to read
        # a section against a header row scrolled off the top, and one section
        # is often all that gets shown.
        out += ["<tbody>", *header(title)]
        for g, (group, rows) in enumerate(_grouped(body)):
            # A rule between row groups — Results from Stats — since they are
            # different kinds of number, not a continuous list.
            top = f";border-top:{RULE}" if g else ""
            for j, (label, cells) in enumerate(rows):
                edge = top if j == 0 else ""
                out.append("  <tr>")
                if j == 0:
                    # "Results" / "Stats" beside their rows rather than above
                    # them: as a full-width divider row it cost a blank line
                    # across every column just to carry one word.
                    out.append(f'    <th rowspan="{len(rows)}" '
                               f'style="{TD};font-weight:bold;vertical-align:top{edge}">'
                               f"{cell(group)}</th>")
                out.append(f'    <th style="{TD};font-weight:bold{edge}">'
                           f"{cell(label)}</th>")
                for i, c in enumerate(cells):
                    out.append(f'    <td style="{GROUP if i in starts else TD}{edge}">'
                               f"{cell(c)}</td>")
                out.append("  </tr>")
        out.append("</tbody>")
    out += ["</table>", "", esc(note)]
    return "\n".join(out)
