| _ | Claude Fable 5 | Claude Opus 4.8 | Claude Opus 4.7 | Claude Opus 4.6 | Claude Sonnet 4.6 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|---|---|---|
| **Standard: 60 problems (<1 h human effort)** | | | | | | | |
| Resolved (out of 60) | **55** | 51 | 50 | 46 | 44 | 51 | 38 |
| Resolved % | **92%** | 85% | 83% | 77% | 73% | 85% | 63% |
| Total cost | $30.68 | $21.00 | $25.90 | $24.48 | $35.58 | $17.34 | $17.90 |
| $ / resolved | $0.56 | $0.41 | $0.52 | $0.53 | $0.81 | **$0.34** | $0.47 |
| Steps | 657 | 887 | 1,179 | 1,236 | 1,953 | 1,383 | 3,663 |
| Output tokens | 309k | 400k | 409k | 327k | 954k | 388k | 980k |
| Thinking (output) | ❔ | ❔ | 190k | 127k | ❔ | 186k | 🚫 |
| Input tokens | 6.8M | 12.1M | 19.7M | 17.0M | 49.8M | 23.7M | 94.7M |
| - non-cached | 1.3k | 1.8k | 1.5k | 669k | 2.1k | 2.8k | 656k |
| - cache read | 6.1M | 11.2M | 18.7M | 15.5M | 48.0M | 22.4M | 91.5M |
| - cache write | 731k | 862k | 1.01M | 831k | 1.83M | 1.28M | 2.56M |
| Wall-clock (12-way parallel) | 2.0 h | 2.1 h | 1.7 h | 1.8 h | 4.9 h | 2.0 h | 3.5 h |
| **Hard: 45 problems (1+ h human effort)** | | | | | | | |
| Resolved (out of 45) | **39** | 32 | 25 | 18 | 21 | 34 | 13 |
| Resolved % | **87%** | 71% | 56% | 40% | 47% | 76% | 29% |
| Total cost | $52.85 | $33.97 | $51.92 | $52.14 | $105.45 | $39.63 | $21.41 |
| $ / resolved | $1.36 | **$1.06** | $2.08 | $2.90 | $5.02 | $1.17 | $1.65 |
| Steps | 743 | 1,217 | 1,718 | 1,799 | 3,025 | 2,206 | 3,832 |
| Output tokens | 536k | 578k | 703k | 676k | 2.06M | 725k | 1.05M |
| Thinking (output) | ❔ | ❔ | 346k | 299k | ❔ | 368k | 🚫 |
| Input tokens | 12.8M | 24.7M | 50.5M | 50.2M | 197.3M | 71.9M | 126.5M |
| - non-cached | 1.5k | 2.4k | 1.9k | 309k | 3.1k | 4.4k | 497k |
| - cache read | 11.7M | 23.4M | 48.9M | 48.4M | 192.9M | 69.8M | 123.3M |
| - cache write | 1.15M | 1.25M | 1.58M | 1.52M | 4.43M | 2.08M | 2.66M |
| Wall-clock (12-way parallel) | 2.4 h | 2.3 h | 2.9 h | 3.7 h | 10.4 h | 3.5 h | 3.5 h |
| **Combined: 105 problems** | | | | | | | |
| Resolved (out of 105) | **94** | 83 | 75 | 64 | 65 | 85 | 51 |
| Resolved % | **90%** | 79% | 71% | 61% | 62% | 81% | 49% |
| Total cost | $83.53 | $54.97 | $77.82 | $76.61 | $141.03 | $56.97 | $39.31 |
| $ / resolved | $0.89 | **$0.66** | $1.04 | $1.20 | $2.17 | $0.67 | $0.77 |
| Steps | 1,400 | 2,104 | 2,897 | 3,035 | 4,978 | 3,589 | 7,495 |
| Output tokens | 845k | 978k | 1.11M | 1.00M | 3.02M | 1.11M | 2.03M |
| Thinking (output) | ❔ | ❔ | 536k | 426k | ❔ | 554k | 🚫 |
| Input tokens | 19.6M | 36.7M | 70.2M | 67.2M | 247.1M | 95.5M | 221.2M |
| - non-cached | 2.8k | 4.2k | 3.4k | 979k | 5.2k | 7.2k | 1.15M |
| - cache read | 17.8M | 34.6M | 67.6M | 63.9M | 240.9M | 92.2M | 214.8M |
| - cache write | 1.88M | 2.11M | 2.60M | 2.35M | 6.26M | 3.36M | 5.22M |
| Wall-clock (12-way parallel) | 4.4 h | 4.4 h | 4.7 h | 5.6 h | 15.2 h | 5.5 h | 7.0 h |

**Note:**

- Using SWE-bench Verified, which is Python open source projects on GitHub, with tests
- This tests problem solving and generating code that can be automatically tested
- The model is given the issue and a ready-made environment, and has to submit a patch - no communication involved, just problem solving and coding
- Resolved means the model submitted a patch that passed the tests
- The difficulty is the benchmark's time estimation (human fix time)
- Standard = 60 problems sampled from the under-1-hour ones; Hard = all 45 problems rated over an hour

**Caveats:**

- Haiku 4.5 ran without adaptive thinking (not supported); the others ran with it
- Custom harness and system prompt - the numbers compare these seven runs against each other, not against published leaderboards
- Attempts were capped at 250 steps / $25; attempts that hit the caps count as unresolved (e.g. two Sonnet hard attempts)
- Wall-clock is total time across 12 parallel workers on one machine - roughly 5x the true API service time. The gap is local overhead under that load, not the API; treat it as a relative cost signal, not latency
- Thinking (output) tokens were captured at the wire for Opus 4.6/4.7 (shared-proxy capture) and Sonnet 5 (per-leg proxy). ❔ = thinking was on but not recorded that run; 🚫 = model has no thinking mode
- Thinking effort was omitted, which should default to high (note Anthropic recommends xhigh for Opus 4.7/4.8 coding, so those two are conservative relative to that guidance)
