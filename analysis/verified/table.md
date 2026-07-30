| SWE-bench Verified — latest-generation division | Claude Fable 5 | Claude Opus 5 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 55 | 🥇 **56** | 🥉 51 | 38 |
| Resolved % | 🥈 92% | 🥇 **93%** | 🥉 85% | 63% |
| Total cost | $30.68 | 🥉 $18.81 | 🥇 **$17.34** | 🥈 $17.90 |
| $/resolved | 🥉 $0.56 | 🥇 **$0.34** | 🥇 **$0.34** | 🥈 $0.47 |
| **Stats** | | | | |
| Steps (total) | 657 | 795 | 1,383 | 3,663 |
| Turns/instance (avg) | 10.9 | 13.2 | 23.1 | 61.0 |
| Cost/turn (avg) | $0.047 | $0.024 | $0.013 | $0.005 |
| Output tokens | 309k | 326k | 388k | 980k |
| Thinking (output) | — | 151k | 186k | — |
| Input tokens | 6.80M | 10.43M | 23.67M | 94.68M |
| — non-cached | 1k | 2k | 3k | 656k |
| — cache read | 6.07M | 9.49M | 22.39M | 91.46M |
| — cache write | 731k | 947k | 1.28M | 2.56M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 10,356 | 13,124 | 17,113 | 25,847 |
| Output tokens/turn (avg) | 471 | 410 | 281 | 268 |
| Context window (peak, single turn) | 49k | 62k | 62k | 107k |
| Wall-clock (12-way parallel) | 2.0 h | 1.3 h | 2.0 h | 3.5 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **39** | 🥈 38 | 🥉 34 | 13 |
| Resolved % | 🥇 **87%** | 🥈 84% | 🥉 76% | 29% |
| Total cost | $52.85 | 🥈 $37.65 | 🥉 $39.63 | 🥇 **$21.41** |
| $/resolved | 🥉 $1.36 | 🥇 **$0.99** | 🥈 $1.17 | $1.65 |
| **Stats** | | | | |
| Steps (total) | 743 | 1,131 | 2,206 | 3,832 |
| Turns/instance (avg) | 16.5 | 25.1 | 49.0 | 85.2 |
| Cost/turn (avg) | $0.071 | $0.033 | $0.018 | $0.006 |
| Output tokens | 536k | 595k | 725k | 1.05M |
| Thinking (output) | — | 321k | 368k | — |
| Input tokens | 12.84M | 28.54M | 71.86M | 126.48M |
| — non-cached | 1k | 2k | 4k | 497k |
| — cache read | 11.69M | 27.06M | 69.78M | 123.32M |
| — cache write | 1.15M | 1.48M | 2.08M | 2.66M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 17,278 | 25,235 | 32,575 | 33,006 |
| Output tokens/turn (avg) | 722 | 526 | 329 | 275 |
| Context window (peak, single turn) | 57k | 107k | 134k | 101k |
| Wall-clock (12-way parallel) | 2.4 h | 2.3 h | 3.5 h | 3.5 h |
| **Combined — 105 *Python* events** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **94** | 🥇 **94** | 🥈 85 | 🥉 51 |
| Resolved % | 🥇 **90%** | 🥇 **90%** | 🥈 81% | 🥉 49% |
| Total cost | $83.53 | 🥈 $56.46 | 🥉 $56.97 | 🥇 **$39.32** |
| $/resolved | $0.89 | 🥇 **$0.60** | 🥈 $0.67 | 🥉 $0.77 |
| **Stats** | | | | |
| Steps (total) | 1,400 | 1,926 | 3,589 | 7,495 |
| Turns/instance (avg) | 13.3 | 18.3 | 34.2 | 71.4 |
| Cost/turn (avg) | $0.060 | $0.029 | $0.016 | $0.005 |
| Output tokens | 845k | 921k | 1.11M | 2.03M |
| Thinking (output) | — | 471k | 554k | — |
| Input tokens | 19.64M | 38.97M | 95.53M | 221.15M |
| — non-cached | 3k | 4k | 7k | 1.15M |
| — cache read | 17.76M | 36.55M | 92.16M | 214.78M |
| — cache write | 1.88M | 2.42M | 3.36M | 5.22M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 14,030 | 20,236 | 26,617 | 29,507 |
| Output tokens/turn (avg) | 604 | 478 | 310 | 271 |
| Context window (peak, single turn) | 57k | 107k | 134k | 107k |
| Wall-clock (12-way parallel) | 4.4 h | 3.5 h | 5.5 h | 7.0 h |
| **Medal tally — per instance (105 events, 5 unsolved by every model)** | | | | |
| 🥇 gold | 13 | 37 | 45 | 5 |
| 🥈 silver | 20 | 39 | 18 | 17 |
| 🥉 bronze | 33 | 15 | 15 | 18 |
| placing | 🥉 **3** | 🥈 **2** | 🥇 **1** | 4 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
