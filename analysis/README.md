# analysis/

Derived figures, written by `./swe.mjs <target> analyse` — never edited by
hand. Raw verdicts live in `evals/`; run data in `runs/`.

**Start at `overview/table.png`** — every dataset's headline (resolved %,
cost per resolved) on one card, grouped by dataset. Regenerated after every
`analyse`, so it is never staler than the analyses it summarises.

One folder per dataset — `overview/`, `verified/`, `pro/`, `multilingual/`,
`multi/` — each containing the same four files:

| file         | for                                            |
|--------------|------------------------------------------------|
| `data.json`  | machines (the overview reads these)            |
| `table.md`   | reading as text, reconciling into `report.md`  |
| `table.html` | opening in a browser                           |
| `table.png`  | pasting into chat (markdown pastes as pipes)   |

`table.d2` / `table.svg` are render intermediates — regenerated every run,
gitignored.
