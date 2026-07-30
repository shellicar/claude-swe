# Experiment matrix

What has been run, what is planned, and which cells are deliberately left empty.
Named `experiment-matrix.md` rather than `table.md` to avoid colliding with the
generated `analysis/*/table.md` cards.

## The four dimensions

| dimension | values | notes |
|---|---|---|
| **meet** (sport) | verified (105), multi (60), multilingual (96), pro (109) | instance counts are per leg |
| **model** | opus-4-6, opus-4-7, opus-4-8, **opus-5**, sonnet-4-6, **sonnet-5**, **fable-5**, haiku-4-5 | bold = current generation |
| **effort** | low, medium, high (default), xhigh, max | `high` is the default leg in `main`; the sweep omits it rather than running it twice |
| **arm** | bash control + 21 scaffolding/tool arms | all arms are verified/hard only |

The full cross-product is 4 × 8 × 5 × 22 = **3,520 legs**, so the matrix is
deliberately sparse: each experiment moves one dimension and holds the rest
fixed.

## Done

| what | meet | models | effort | instances |
|---|---|---|---|---|
| `main` | verified | all 8 | default | 840 |
| `effort-sweep` | verified | opus-4-8, opus-5, sonnet-5, fable-5 | low/medium/xhigh/max | 1,680 |
| `multi` | multi | fable-5, haiku-4-5, opus-4-8, sonnet-5 | default | 264 |
| `multilingual` | multilingual | fable-5, haiku-4-5, opus-4-8, sonnet-5 | default | 384 |
| `pro` | pro | fable-5, haiku-4-5, opus-4-8, sonnet-5 | default | 436 |
| 16 tool/exec/prompt arms | verified/hard | sonnet-5 | default | 720 |

Effort curves now exist for four models on verified. Key result: effort was
flat above `high` for Opus 4.8 (83 resolved at high, xhigh and max alike) but
climbs the whole way for Opus 5 (94 → 99 → 103), so **every effort finding is
model-specific** and the old "don't pay for xhigh/max" rule does not
generalise.

## Planned

### 1. Opus 5 on the other sports

The current-generation model is missing from every meet except verified.
Sonnet 5 is already in all of them, so only Opus 5 needs adding.

| meet | instances | order | why |
|---|---|---|---|
| `multi` | 60 | first | cheapest, fastest feedback |
| `multilingual` | 96 | second | |
| `pro` | 109 | last | marks through Scale's harness, not swebench's — more failure modes |

**265 instances.** Each meet's analyser declares its own model roster
(`analyse-multi.py`, `analyse-multilingual.py`, `analyse-pro.py`), so the
roster is declared in ~6 places across the repo. Centralise it before adding
Opus 5 to three more files, not after.

### 2. Opus 5 effort sweep on 1–2 arms

The question: do the scaffolding/tool findings hold for a different model, and
does effort change which arm wins? Every arm result today is a **Sonnet 5 at
default effort** finding.

The control already exists: `effort-sweep/opus-5-*` **is** the bash control at
each effort level, so an arm only needs its own five levels.

| per arm | instances |
|---|---|
| default effort (the arm itself) | 45 |
| low/medium/xhigh/max | 180 |
| **per arm total** | **225** |

Two arms: **450 instances**. Not all 21 — that would be 4,725 instances for
one model, and the arms' own contest is already settled for Sonnet 5. Pick the
two that carry the most signal (e.g. the exec-grammar winner and the bash
control's closest challenger) rather than sweeping the field.

## Deliberately empty

| cell | why |
|---|---|
| older models (opus-4-6/4-7, sonnet-4-6) on new meets | superseded; kept only as lineage history on verified |
| haiku-4-5 effort sweep | pre-4.6 generation, does not support adaptive thinking |
| all 21 arms × all models | combinatorial explosion for little marginal signal |
| all arms × all effort levels | same; 1–2 arms answers whether the findings transfer |
| `cpp-variation`, `fmt-variation` | variation experiments, not model contests |
| `walker-*` arms | 0/45 — the aborted run; the walker has since changed materially (empty `"$@"`, glob fixes, PIPESTATUS, umask, exec, procsub, concurrent pipelines), so any rerun starts fresh |

## Total planned work

**715 instances** — 265 for the sports, 450 for two arms' effort curves.
