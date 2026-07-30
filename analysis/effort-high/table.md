| High-effort division — every contender (SWE-bench Verified) | Claude Fable 5 | Claude Opus 5 | Claude Opus 4.8 | Claude Sonnet 5 |
|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 55 | 🥇 **56** | 🥉 51 | 🥉 51 |
| Resolved % | 🥈 92% | 🥇 **93%** | 🥉 85% | 🥉 85% |
| Total cost | $30.68 | 🥈 $18.81 | 🥉 $21.00 | 🥇 **$17.34** |
| $/resolved | 🥉 $0.56 | 🥇 **$0.34** | 🥈 $0.41 | 🥇 **$0.34** |
| **Stats** | | | | |
| Steps (total) | 657 | 795 | 887 | 1,383 |
| Turns/instance (avg) | 10.9 | 13.2 | 14.8 | 23.1 |
| Cost/turn (avg) | $0.047 | $0.024 | $0.024 | $0.013 |
| Output tokens | 309k | 326k | 400k | 388k |
| Thinking (output) | — | 151k | — | 186k |
| Input tokens | 6.80M | 10.43M | 12.08M | 23.67M |
| — non-cached | 1k | 2k | 2k | 3k |
| — cache read | 6.07M | 9.49M | 11.21M | 22.39M |
| — cache write | 731k | 947k | 862k | 1.28M |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 10,356 | 13,124 | 13,614 | 17,113 |
| Output tokens/turn (avg) | 471 | 410 | 451 | 281 |
| Context window (peak, single turn) | 49k | 62k | 63k | 62k |
| Wall-clock (12-way parallel) | 2.0 h | 1.3 h | 2.1 h | 2.0 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **39** | 🥈 38 | 32 | 🥉 34 |
| Resolved % | 🥇 **87%** | 🥈 84% | 71% | 🥉 76% |
| Total cost | $52.85 | 🥈 $37.65 | 🥇 **$33.97** | 🥉 $39.63 |
| $/resolved | $1.36 | 🥇 **$0.99** | 🥈 $1.06 | 🥉 $1.17 |
| **Stats** | | | | |
| Steps (total) | 743 | 1,131 | 1,217 | 2,206 |
| Turns/instance (avg) | 16.5 | 25.1 | 27.0 | 49.0 |
| Cost/turn (avg) | $0.071 | $0.033 | $0.028 | $0.018 |
| Output tokens | 536k | 595k | 578k | 725k |
| Thinking (output) | — | 321k | — | 368k |
| Input tokens | 12.84M | 28.54M | 24.67M | 71.86M |
| — non-cached | 1k | 2k | 2k | 4k |
| — cache read | 11.69M | 27.06M | 23.42M | 69.78M |
| — cache write | 1.15M | 1.48M | 1.25M | 2.08M |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 17,278 | 25,235 | 20,273 | 32,575 |
| Output tokens/turn (avg) | 722 | 526 | 475 | 329 |
| Context window (peak, single turn) | 57k | 107k | 85k | 134k |
| Wall-clock (12-way parallel) | 2.4 h | 2.3 h | 2.3 h | 3.5 h |
| **Combined — 105 *Python* events** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **94** | 🥇 **94** | 🥉 83 | 🥈 85 |
| Resolved % | 🥇 **90%** | 🥇 **90%** | 🥉 79% | 🥈 81% |
| Total cost | $83.53 | 🥈 $56.46 | 🥇 **$54.97** | 🥉 $56.97 |
| $/resolved | $0.89 | 🥇 **$0.60** | 🥈 $0.66 | 🥉 $0.67 |
| **Stats** | | | | |
| Steps (total) | 1,400 | 1,926 | 2,104 | 3,589 |
| Turns/instance (avg) | 13.3 | 18.3 | 20.0 | 34.2 |
| Cost/turn (avg) | $0.060 | $0.029 | $0.026 | $0.016 |
| Output tokens | 845k | 921k | 978k | 1.11M |
| Thinking (output) | — | 471k | — | 554k |
| Input tokens | 19.64M | 38.97M | 36.75M | 95.53M |
| — non-cached | 3k | 4k | 4k | 7k |
| — cache read | 17.76M | 36.55M | 34.64M | 92.16M |
| — cache write | 1.88M | 2.42M | 2.11M | 3.36M |
| Failed tool calls (FormatError) | 0 | 0 | 2 | 0 |
| Input tokens/turn (avg) | 14,030 | 20,236 | 17,466 | 26,617 |
| Output tokens/turn (avg) | 604 | 478 | 465 | 310 |
| Context window (peak, single turn) | 57k | 107k | 85k | 134k |
| Wall-clock (12-way parallel) | 4.4 h | 3.5 h | 4.4 h | 5.5 h |
| **Medal tally — per instance (105 events, 4 unsolved by every model)** | | | | |
| 🥇 gold | 7 | 25 | 38 | 31 |
| 🥈 silver | 17 | 31 | 25 | 24 |
| 🥉 bronze | 26 | 32 | 12 | 18 |
| placing | 4 | 🥉 **3** | 🥇 **1** | 🥈 **2** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
