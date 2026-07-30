| High-effort division — every contender (SWE-bench Verified) | Claude Opus 4.8 | Claude Opus 5 | Claude Sonnet 5 | Claude Fable 5 |
|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥉 51 | 🥇 **56** | 🥉 51 | 🥈 55 |
| Resolved % | 🥉 85% | 🥇 **93%** | 🥉 85% | 🥈 92% |
| Total cost | 🥉 $21.00 | 🥈 $18.81 | 🥇 **$17.34** | $30.68 |
| $/resolved | 🥈 $0.41 | 🥇 **$0.34** | 🥇 **$0.34** | 🥉 $0.56 |
| **Stats** | | | | |
| Steps (total) | 887 | 795 | 1,383 | 657 |
| Turns/instance (avg) | 14.8 | 13.2 | 23.1 | 10.9 |
| Cost/turn (avg) | $0.024 | $0.024 | $0.013 | $0.047 |
| Output tokens | 400k | 326k | 388k | 309k |
| Thinking (output) | — | 151k | 186k | — |
| Input tokens | 12.08M | 10.43M | 23.67M | 6.80M |
| — non-cached | 2k | 2k | 3k | 1k |
| — cache read | 11.21M | 9.49M | 22.39M | 6.07M |
| — cache write | 862k | 947k | 1.28M | 731k |
| Failed tool calls (FormatError) | 1 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 13,614 | 13,124 | 17,113 | 10,356 |
| Output tokens/turn (avg) | 451 | 410 | 281 | 471 |
| Context window (peak, single turn) | 63k | 62k | 62k | 49k |
| Wall-clock (12-way parallel) | 2.1 h | 1.3 h | 2.0 h | 2.0 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 32 | 🥈 38 | 🥉 34 | 🥇 **39** |
| Resolved % | 71% | 🥈 84% | 🥉 76% | 🥇 **87%** |
| Total cost | 🥇 **$33.97** | 🥈 $37.65 | 🥉 $39.63 | $52.85 |
| $/resolved | 🥈 $1.06 | 🥇 **$0.99** | 🥉 $1.17 | $1.36 |
| **Stats** | | | | |
| Steps (total) | 1,217 | 1,131 | 2,206 | 743 |
| Turns/instance (avg) | 27.0 | 25.1 | 49.0 | 16.5 |
| Cost/turn (avg) | $0.028 | $0.033 | $0.018 | $0.071 |
| Output tokens | 578k | 595k | 725k | 536k |
| Thinking (output) | — | 321k | 368k | — |
| Input tokens | 24.67M | 28.54M | 71.86M | 12.84M |
| — non-cached | 2k | 2k | 4k | 1k |
| — cache read | 23.42M | 27.06M | 69.78M | 11.69M |
| — cache write | 1.25M | 1.48M | 2.08M | 1.15M |
| Failed tool calls (FormatError) | 1 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 20,273 | 25,235 | 32,575 | 17,278 |
| Output tokens/turn (avg) | 475 | 526 | 329 | 722 |
| Context window (peak, single turn) | 85k | 107k | 134k | 57k |
| Wall-clock (12-way parallel) | 2.3 h | 2.3 h | 3.5 h | 2.4 h |
| **Combined — 105 *Python* events** | | | | |
| **Results** | | | | |
| Resolved | 🥉 83 | 🥇 **94** | 🥈 85 | 🥇 **94** |
| Resolved % | 🥉 79% | 🥇 **90%** | 🥈 81% | 🥇 **90%** |
| Total cost | 🥇 **$54.97** | 🥈 $56.46 | 🥉 $56.97 | $83.53 |
| $/resolved | 🥈 $0.66 | 🥇 **$0.60** | 🥉 $0.67 | $0.89 |
| **Stats** | | | | |
| Steps (total) | 2,104 | 1,926 | 3,589 | 1,400 |
| Turns/instance (avg) | 20.0 | 18.3 | 34.2 | 13.3 |
| Cost/turn (avg) | $0.026 | $0.029 | $0.016 | $0.060 |
| Output tokens | 978k | 921k | 1.11M | 845k |
| Thinking (output) | — | 471k | 554k | — |
| Input tokens | 36.75M | 38.97M | 95.53M | 19.64M |
| — non-cached | 4k | 4k | 7k | 3k |
| — cache read | 34.64M | 36.55M | 92.16M | 17.76M |
| — cache write | 2.11M | 2.42M | 3.36M | 1.88M |
| Failed tool calls (FormatError) | 2 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 17,466 | 20,236 | 26,617 | 14,030 |
| Output tokens/turn (avg) | 465 | 478 | 310 | 604 |
| Context window (peak, single turn) | 85k | 107k | 134k | 57k |
| Wall-clock (12-way parallel) | 4.4 h | 3.5 h | 5.5 h | 4.4 h |
| **Medal tally — per instance (105 events, 4 unsolved by every model)** | | | | |
| 🥇 gold | 38 | 25 | 31 | 7 |
| 🥈 silver | 25 | 31 | 24 | 17 |
| 🥉 bronze | 12 | 32 | 18 | 26 |
| placing | 🥇 **1** | 🥉 **3** | 🥈 **2** | 4 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
