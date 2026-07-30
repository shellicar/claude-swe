| Low-effort division — every contender (SWE-bench Verified) | Claude Opus 4.8 | Claude Opus 5 |
|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | |
| **Results** | | |
| Resolved | 48 | 48 |
| Resolved % | 80% | 80% |
| Total cost | 🥈 $8.73 | 🥇 **$5.50** |
| $/resolved | 🥈 $0.18 | 🥇 **$0.11** |
| **Stats** | | |
| Steps (total) | 560 | 393 |
| Turns/instance (avg) | 9.3 | 6.5 |
| Cost/turn (avg) | $0.016 | $0.014 |
| Output tokens | 150k | 84k |
| Thinking (output) | — | 21k |
| Input tokens | 4.25M | 2.32M |
| — non-cached | 1k | 1k |
| — cache read | 3.75M | 1.94M |
| — cache write | 498k | 387k |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 7,581 | 5,916 |
| Output tokens/turn (avg) | 268 | 214 |
| Context window (peak, single turn) | 34k | 26k |
| Wall-clock (12-way parallel) | 0.7 h | 0.3 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | |
| **Results** | | |
| Resolved | 🥇 **30** | 🥈 26 |
| Resolved % | 🥇 **67%** | 🥈 58% |
| Total cost | 🥈 $22.84 | 🥇 **$9.23** |
| $/resolved | 🥈 $0.76 | 🥇 **$0.35** |
| **Stats** | | |
| Steps (total) | 1,002 | 461 |
| Turns/instance (avg) | 22.3 | 10.2 |
| Cost/turn (avg) | $0.023 | $0.020 |
| Output tokens | 373k | 157k |
| Thinking (output) | — | 53k |
| Input tokens | 16.87M | 4.33M |
| — non-cached | 2k | 1k |
| — cache read | 15.98M | 3.79M |
| — cache write | 884k | 546k |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 16,834 | 9,400 |
| Output tokens/turn (avg) | 372 | 340 |
| Context window (peak, single turn) | 87k | 28k |
| Wall-clock (12-way parallel) | 1.6 h | 0.6 h |
| **Combined — 105 *Python* events** | | |
| **Results** | | |
| Resolved | 🥇 **78** | 🥈 74 |
| Resolved % | 🥇 **74%** | 🥈 70% |
| Total cost | 🥈 $31.57 | 🥇 **$14.72** |
| $/resolved | 🥈 $0.40 | 🥇 **$0.20** |
| **Stats** | | |
| Steps (total) | 1,562 | 854 |
| Turns/instance (avg) | 14.9 | 8.1 |
| Cost/turn (avg) | $0.020 | $0.017 |
| Output tokens | 522k | 241k |
| Thinking (output) | — | 74k |
| Input tokens | 21.11M | 6.66M |
| — non-cached | 3k | 2k |
| — cache read | 19.73M | 5.72M |
| — cache write | 1.38M | 933k |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 13,516 | 7,797 |
| Output tokens/turn (avg) | 334 | 282 |
| Context window (peak, single turn) | 87k | 28k |
| Wall-clock (12-way parallel) | 2.3 h | 1.0 h |
| **Medal tally — per instance (105 events, 20 unsolved by every model)** | | |
| 🥇 gold | 22 | 63 |
| 🥈 silver | 56 | 11 |
| 🥉 bronze | 0 | 0 |
| placing | 🥈 **2** | 🥇 **1** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
