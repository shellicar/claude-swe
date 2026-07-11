# analysis/

Derived figures, written by `./swe.mjs <target> analyse` — never edited by
hand. Raw verdicts live in `evals/`; run data in `runs/`.

**Start at `overview.png`** — every dataset's headline (resolved %, cost per
resolved) on one card, grouped by dataset. Regenerated after every `analyse`.

Per dataset (`verified`, `pro`, `multilingual`, `multi`), the same table in
up to four forms:

| form    | for                                            |
|---------|------------------------------------------------|
| `.json` | machines (the overview reads these)            |
| `.md`   | reading as text, reconciling into `report.md`  |
| `.html` | opening in a browser                           |
| `.png`  | pasting into chat (markdown pastes as pipes)   |

`.d2` and `.svg` are render intermediates — regenerated every run, not
committed.
