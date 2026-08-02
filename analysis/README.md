# analysis/

Derived figures, written by `./swe.mjs <target> analyse` — never edited by
hand. Raw verdicts live in `evals/`; run data in `runs/`.

**Start at `overview/overview.svg`** — every dataset's headline (resolved %,
cost per resolved) on one card, grouped by dataset. Regenerated after every
`analyse`, so it is never staler than the analyses it summarises.

## What a card compares

Every card holds everything fixed but one thing, and that one thing is its
columns. Which thing varies decides what the card can say, and there are only
two kinds.

**A meet** varies the **contender**. Same events, same conditions, one column
per model. Reading across the row compares models, so a podium means
something: they all faced the same test.

**An experiment** varies the **condition** — the prompt, the tool surface, the
timeout, the effort. The contenders are held. The comparison is each contender
against *itself* under condition A and condition B, so the row that matters
runs A / B / delta for one model. A podium across models here says nothing:
nobody is asking which model wins, they are asking whether the change moved
anything.

That is why an experiment never appears as a section inside a meet's card. Put
it there and its columns become models, which is the wrong axis: the pairing
that carries the answer — this contender before, this contender after — is not
even adjacent, and its numbers join a podium that was never its question.

A contender is `provider → family → version` (anthropic → opus → 5), not a flat
name. An experiment routinely says "the same configuration across every Opus"
or "repeat this on the next version", and that needs the parts.

## Vocabulary

The cards speak competition vocabulary — a naming aid, not a model:

| word | construct |
|---|---|
| contender | model, as provider → family → version |
| division | group of contenders — same events, separate podiums |
| event | instance (one result per contender) |
| event group | repo · **sport** — language |
| meet | dataset, with its own **judges** (marker) and **program** (selection) |
| experiment | a condition varied against a control, on the same events; its own card, never a section in a meet |

The divisions are declared in `models.json` (`latest`, `tier`), never listed
here — prose drifts from the roster. The **latest generation** fills the
overview and every meet's card; the **Opus** and **Sonnet** divisions
(`opus-models/`, `sonnet-models/`) compete on their own cards, generations as
columns, read left-to-right as the improvement curve (Verified data).

One folder per card — `overview/`, `verified/`, `pro/`, `multilingual/`,
`multi/`, `opus-models/`, `sonnet-models/` — each containing the same three
files:

| file         | for                                            |
|--------------|------------------------------------------------|
| `data.json`  | machines (the overview reads these)            |
| `table.md`   | reading as text, reconciling into `report.md`  |
| `<name>.svg` | the rendered card                              |
| `<name>.png` | the card for pasting into chat (SVG pastes as text) |

Headline rows (Resolved, Resolved %, Total cost, $/resolved) bold the best
cell per row — highest for resolve, lowest for cost. `<name>.d2` is the
render intermediate — regenerated every run, gitignored.
