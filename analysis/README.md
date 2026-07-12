# analysis/

Derived figures, written by `./swe.mjs <target> analyse` — never edited by
hand. Raw verdicts live in `evals/`; run data in `runs/`.

**Start at `overview/overview.svg`** — every dataset's headline (resolved %,
cost per resolved) on one card, grouped by dataset. Regenerated after every
`analyse`, so it is never staler than the analyses it summarises.

Three competing groups, never mixed in one table: the **latest generation**
(Fable 5, Opus 4.8, Sonnet 5, Haiku 4.5) fills the overview and every dataset
card; the **Opus lineage** (`opus-models/`) and **Sonnet lineage**
(`sonnet-models/`) compete on their own cards, generations as columns, read
left-to-right as the improvement curve (Verified data).

One folder per card — `overview/`, `verified/`, `pro/`, `multilingual/`,
`multi/`, `opus-models/`, `sonnet-models/` — each containing the same three
files:

| file         | for                                            |
|--------------|------------------------------------------------|
| `data.json`  | machines (the overview reads these)            |
| `table.md`   | reading as text, reconciling into `report.md`  |
| `<name>.svg` | the rendered card                              |

Headline rows (Resolved, Resolved %, Total cost, $/resolved) bold the best
cell per row — highest for resolve, lowest for cost. `<name>.d2` is the
render intermediate — regenerated every run, gitignored.
