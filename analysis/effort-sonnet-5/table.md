| Effort division — Claude Sonnet 5 (SWE-bench Verified) | low | medium | high |
|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥈 46 | 🥈 46 | 🥇 **51** |
| Resolved % | 🥈 77% | 🥈 77% | 🥇 **85%** |
| Total cost | 🥇 **$7.66** | 🥈 $11.31 | 🥉 $17.34 |
| $/resolved | 🥇 **$0.17** | 🥈 $0.25 | 🥉 $0.34 |
| **Stats** | | | |
| Steps (total) | 753 | 991 | 1,383 |
| Turns/instance (avg) | 12.6 | 16.5 | 23.1 |
| Cost/turn (avg) | $0.010 | $0.011 | $0.013 |
| Output tokens | 186k | 264k | 388k |
| Thinking (output) | 56k | 84k | 186k |
| Input tokens | 8.86M | 14.35M | 23.67M |
| — non-cached | 2k | 2k | 3k |
| — cache read | 8.22M | 13.46M | 22.39M |
| — cache write | 639k | 882k | 1.28M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 11,770 | 14,476 | 17,113 |
| Output tokens/turn (avg) | 247 | 266 | 281 |
| Context window (peak, single turn) | 46k | 67k | 62k |
| Wall-clock (12-way parallel) | 0.7 h | 1.0 h | 2.0 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥉 21 | 🥈 31 | 🥇 **34** |
| Resolved % | 🥉 47% | 🥈 69% | 🥇 **76%** |
| Total cost | 🥇 **$12.92** | 🥈 $24.25 | 🥉 $39.63 |
| $/resolved | 🥇 **$0.62** | 🥈 $0.78 | 🥉 $1.17 |
| **Stats** | | | |
| Steps (total) | 1,036 | 1,666 | 2,206 |
| Turns/instance (avg) | 23.0 | 37.0 | 49.0 |
| Cost/turn (avg) | $0.012 | $0.015 | $0.018 |
| Output tokens | 301k | 456k | 725k |
| Thinking (output) | 79k | 141k | 368k |
| Input tokens | 17.03M | 40.46M | 71.86M |
| — non-cached | 2k | 3k | 4k |
| — cache read | 16.07M | 38.93M | 69.78M |
| — cache write | 955k | 1.53M | 2.08M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 16,436 | 24,286 | 32,575 |
| Output tokens/turn (avg) | 290 | 274 | 329 |
| Context window (peak, single turn) | 61k | 91k | 134k |
| Wall-clock (12-way parallel) | 1.1 h | 1.8 h | 3.5 h |
| **Combined — 105 *Python* events** | | | |
| **Results** | | | |
| Resolved | 🥉 67 | 🥈 77 | 🥇 **85** |
| Resolved % | 🥉 64% | 🥈 73% | 🥇 **81%** |
| Total cost | 🥇 **$20.58** | 🥈 $35.57 | 🥉 $56.97 |
| $/resolved | 🥇 **$0.31** | 🥈 $0.46 | 🥉 $0.67 |
| **Stats** | | | |
| Steps (total) | 1,789 | 2,657 | 3,589 |
| Turns/instance (avg) | 17.0 | 25.3 | 34.2 |
| Cost/turn (avg) | $0.012 | $0.013 | $0.016 |
| Output tokens | 487k | 720k | 1.11M |
| Thinking (output) | 135k | 225k | 554k |
| Input tokens | 25.89M | 54.81M | 95.53M |
| — non-cached | 4k | 5k | 7k |
| — cache read | 24.29M | 52.39M | 92.16M |
| — cache write | 1.59M | 2.41M | 3.36M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 14,472 | 20,627 | 26,617 |
| Output tokens/turn (avg) | 272 | 271 | 310 |
| Context window (peak, single turn) | 61k | 91k | 134k |
| Wall-clock (12-way parallel) | 1.8 h | 2.8 h | 5.5 h |
| **Medal tally — per instance (105 events, 13 unsolved by every model)** | | | |
| 🥇 gold | 55 | 22 | 15 |
| 🥈 silver | 11 | 43 | 21 |
| 🥉 bronze | 1 | 12 | 49 |
| placing | 🥇 **1** | 🥈 **2** | 🥉 **3** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
