| Prompt-scaffolding division (bash only) — SWE-bench Verified hard, Sonnet 5 | Sonnet 5 — bash (control) | Sonnet 5 — minimal prompt (pen-down fallback) | Sonnet 5 — no ritual (pen-down only) | Sonnet 5 — exec tool, no ritual (pen-down only) |
|---|---|---|---|---|
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 34 | 🥈 34 | 🥇 **38** | 🥉 33 |
| Resolved % | 🥈 76% | 🥈 76% | 🥇 **84%** | 🥉 73% |
| Total cost | 🥉 $39.63 | 🥈 $33.84 | 🥇 **$33.22** | $40.51 |
| $/resolved | 🥉 $1.17 | 🥈 $1.00 | 🥇 **$0.87** | $1.23 |
| **Stats** | | | | |
| Steps (total) | 2,206 | 2,111 | 2,045 | 2,067 |
| Turns/instance (avg) | 49.0 | 46.9 | 45.4 | 45.9 |
| Cost/turn (avg) | $0.018 | $0.016 | $0.016 | $0.020 |
| Output tokens | 725k | 628k | 631k | 804k |
| Thinking (output) | — | — | — | — |
| Input tokens | 71.86M | 59.17M | 57.11M | 69.12M |
| — non-cached | 4k | 4k | 4k | 4k |
| — cache read | 69.78M | 57.23M | 55.19M | 66.89M |
| — cache write | 2.08M | 1.93M | 1.91M | 2.23M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 32,575 | 28,029 | 27,925 | 33,442 |
| Output tokens/turn (avg) | 329 | 297 | 309 | 389 |
| Context window (peak, single turn) | 134k | 93k | 117k | 127k |
| Wall-clock (12-way parallel) | 3.5 h | 2.4 h | 2.4 h | 2.7 h |
| **Medal tally — per instance (45 events, 4 unsolved by every model)** | | | | |
| 🥇 gold | 12 | 12 | 11 | 6 |
| 🥈 silver | 8 | 7 | 15 | 8 |
| 🥉 bronze | 8 | 10 | 9 | 7 |
| placing | 🥇 **1** | 🥈 **2** | 🥉 **3** | 4 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
