| Low-effort division — every contender (SWE-bench Verified) | Claude Opus 5 | Claude Opus 4.8 | Claude Sonnet 5 |
|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥇 **48** | 🥇 **48** | 🥈 46 |
| Resolved % | 🥇 **80%** | 🥇 **80%** | 🥈 77% |
| Total cost | 🥇 **$5.50** | 🥉 $8.73 | 🥈 $7.66 |
| $/resolved | 🥇 **$0.11** | 🥉 $0.18 | 🥈 $0.17 |
| **Stats** | | | |
| Steps (total) | 393 | 560 | 753 |
| Turns/instance (avg) | 6.5 | 9.3 | 12.6 |
| Cost/turn (avg) | $0.014 | $0.016 | $0.010 |
| Output tokens | 84k | 150k | 186k |
| Thinking (output) | 21k | — | 56k |
| Input tokens | 2.32M | 4.25M | 8.86M |
| — non-cached | 1k | 1k | 2k |
| — cache read | 1.94M | 3.75M | 8.22M |
| — cache write | 387k | 498k | 639k |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 5,916 | 7,581 | 11,770 |
| Output tokens/turn (avg) | 214 | 268 | 247 |
| Context window (peak, single turn) | 26k | 34k | 46k |
| Wall-clock (12-way parallel) | 0.3 h | 0.7 h | 0.7 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥈 26 | 🥇 **30** | 🥉 21 |
| Resolved % | 🥈 58% | 🥇 **67%** | 🥉 47% |
| Total cost | 🥇 **$9.23** | 🥉 $22.84 | 🥈 $12.92 |
| $/resolved | 🥇 **$0.35** | 🥉 $0.76 | 🥈 $0.62 |
| **Stats** | | | |
| Steps (total) | 461 | 1,002 | 1,036 |
| Turns/instance (avg) | 10.2 | 22.3 | 23.0 |
| Cost/turn (avg) | $0.020 | $0.023 | $0.012 |
| Output tokens | 157k | 373k | 301k |
| Thinking (output) | 53k | — | 79k |
| Input tokens | 4.33M | 16.87M | 17.03M |
| — non-cached | 1k | 2k | 2k |
| — cache read | 3.79M | 15.98M | 16.07M |
| — cache write | 546k | 884k | 955k |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 9,400 | 16,834 | 16,436 |
| Output tokens/turn (avg) | 340 | 372 | 290 |
| Context window (peak, single turn) | 28k | 87k | 61k |
| Wall-clock (12-way parallel) | 0.6 h | 1.6 h | 1.1 h |
| **Combined — 105 *Python* events** | | | |
| **Results** | | | |
| Resolved | 🥈 74 | 🥇 **78** | 🥉 67 |
| Resolved % | 🥈 70% | 🥇 **74%** | 🥉 64% |
| Total cost | 🥇 **$14.72** | 🥉 $31.57 | 🥈 $20.58 |
| $/resolved | 🥇 **$0.20** | 🥉 $0.40 | 🥈 $0.31 |
| **Stats** | | | |
| Steps (total) | 854 | 1,562 | 1,789 |
| Turns/instance (avg) | 8.1 | 14.9 | 17.0 |
| Cost/turn (avg) | $0.017 | $0.020 | $0.012 |
| Output tokens | 241k | 522k | 487k |
| Thinking (output) | 74k | — | 135k |
| Input tokens | 6.66M | 21.11M | 25.89M |
| — non-cached | 2k | 3k | 4k |
| — cache read | 5.72M | 19.73M | 24.29M |
| — cache write | 933k | 1.38M | 1.59M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 7,797 | 13,516 | 14,472 |
| Output tokens/turn (avg) | 282 | 334 | 272 |
| Context window (peak, single turn) | 28k | 87k | 61k |
| Wall-clock (12-way parallel) | 1.0 h | 2.3 h | 1.8 h |
| **Medal tally — per instance (105 events, 17 unsolved by every model)** | | | |
| 🥇 gold | 34 | 14 | 40 |
| 🥈 silver | 34 | 25 | 15 |
| 🥉 bronze | 6 | 39 | 12 |
| placing | 🥈 **2** | 🥉 **3** | 🥇 **1** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
