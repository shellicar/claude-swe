# Results

Model comparison on SWE-bench Verified. Scaffold: patched mini-swe-agent (identity block, prompt caching, no sampling params), `swebench-local.yaml` held identical across all models, plus `thinking-adaptive.yaml` for every model except Haiku 4.5 (rejects adaptive thinking: `"adaptive thinking is not supported on this model"`, proven 2026-06-10). Generation and marking both local; see CLAUDE.md for the pipeline.

> Earlier micro-batch results (two passes, four models) were run **without** any thinking configuration — Opus/Sonnet/Haiku ran thinking-less while Fable's always-on adaptive thinking ran by default, an asymmetry that invalidates the comparison. Those tables live in git history; superseded by the runs below.

## Main experiment — results (2026-06-11)

Frozen papers: `instances-standard.txt` (60, stratified difficulty × repo, seed 42) and `instances-hard.txt` (45, census of every instance rated over an hour). 4 models × 2 sets, one pass (`run-experiment.sh`); marked locally (`eval-experiment.sh`).

**Method corrections during the run:** (1) the scaffold's default `cost_limit: 3.0` produced 28 cap-starved empty patches, concentrated on the expensive models — a censor on the cost variable. Cap raised to $25 (loop guard only) and the 28 instances redone; the correction moved Fable's standard score from 44 to 55. (2) Four orphaned legs from a cancelled earlier invocation ran concurrently with the experiment; their output is quarantined in `discarded/`, excluded from everything. (3) Two Sonnet hard instances exhausted the generous guards (250 steps / $25) and stand as genuine failures.

### Resolved

| | Standard (60) | Hard (45) | Overall (105) |
|---|---|---|---|
| **Fable 5** | **55 — 92%** | **39 — 87%** | **94 — 90%** |
| Opus 4.8 | 51 — 85% | 32 — 71% | 83 — 79% |
| Sonnet 4.6 | 44 — 73% | 21 — 47% | 65 — 62% |
| Haiku 4.5 | 38 — 63% | 13 — 29% | 51 — 49% |

### Economics and effort

| Metric | Opus 4.8 | Fable 5 | Haiku 4.5 | Sonnet 4.6 |
|---|---|---|---|---|
| Total cost | $54.97 | $83.53 | $39.31 | $141.03 |
| $/resolved (overall) | **$0.66** | $0.89 | $0.77 | $2.17 |
| $/resolved (standard) | $0.41 | $0.56 | $0.47 | $0.81 |
| $/resolved (hard) | $1.06 | $1.36 | $1.65 | $5.02 |
| Total steps | 2,104 | **1,400** | 7,495 | 4,978 |
| Output tokens | 978k | 845k | 2.03M | 3.02M |
| API time | 4.4h | 4.4h | 7.0h | 15.2h |

### Findings

- **The $3 cap was a thumb on the scale.** Before the correction, Fable read as tied with Opus on standard (44 vs 46); uncensored it wins both sets decisively. Cost caps in agent scaffolds censor exactly the models whose per-step spend is highest — any benchmark using them under-reports expensive models.
- **Fable 5 is the best model on both papers and the most step-efficient** — fewest steps of any model while resolving the most. Its marginal solve over Opus cost ~$2.60.
- **Opus 4.8 is the value baseline:** cheapest per resolved task on both sets.
- **Sonnet 4.6 is a pricing trap for this workload:** mid-tier token price, flagship-level spend (most expensive leg of the experiment at $141 total), bottom-tier hard-set results, and a grind disposition (sustained high spend per turn across very long trajectories; two instances ran to the guards and died).
- **Haiku 4.5 is a viable cascade bottom for easy work** ($0.47/resolved standard) and useless on hard (29%).
- Patch sizes: median 5–8 changed lines on standard, 28–45 on hard — the work is diagnosis, not code volume.
- Thinking-token split per leg is not in these tables: litellm's `reasoning_tokens` mapping proved unreliable; ground truth lives in `mitm/api-timing.jsonl` (`output_tokens_details.thinking_tokens`), but the standard-set window is contaminated by the concurrent zombie legs. Hard-set thinking analysis is clean and available if wanted.

### Caveats

One pass per cell (no repeats — per-instance verdicts are single observations). All-Python, well-tested mature repos, perfectly-specified issues, pre-built environments: results bound "well-specified problems on well-tested code", not legacy/greenfield/ops work. Identity prompt added to scaffold — not comparable to public mini-swe-agent leaderboard numbers.
