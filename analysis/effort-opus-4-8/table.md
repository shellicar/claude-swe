| Effort division — Claude Opus 4.8 (SWE-bench Verified) | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | | |
| **Results** | | | | | |
| Resolved | 48 | 48 | 🥉 51 | 🥈 52 | 🥇 **53** |
| Resolved % | 80% | 80% | 🥉 85% | 🥈 87% | 🥇 **88%** |
| Total cost | 🥇 **$8.73** | 🥈 $15.30 | 🥉 $21.00 | $54.91 | $124.02 |
| $/resolved | 🥇 **$0.18** | 🥈 $0.32 | 🥉 $0.41 | $1.06 | $2.34 |
| **Stats** | | | | | |
| Steps (total) | 560 | 746 | 887 | 1,453 | 2,103 |
| Turns/instance (avg) | 9.3 | 12.4 | 14.8 | 24.2 | 35.0 |
| Cost/turn (avg) | $0.016 | $0.021 | $0.024 | $0.038 | $0.059 |
| Output tokens | 150k | 281k | 400k | 996k | 2.25M |
| Thinking (output) | — | — | — | — | — |
| Input tokens | 4.25M | 8.49M | 12.08M | 38.59M | 93.53M |
| — non-cached | 1k | 1k | 2k | 3k | 4k |
| — cache read | 3.75M | 7.79M | 11.21M | 36.72M | 89.85M |
| — cache write | 498k | 700k | 862k | 1.86M | 3.67M |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 | 0 |
| Input tokens/turn (avg) | 7,581 | 11,379 | 13,614 | 26,559 | 44,473 |
| Output tokens/turn (avg) | 268 | 377 | 451 | 685 | 1,068 |
| Context window (peak, single turn) | 34k | 49k | 63k | 156k | 240k |
| Wall-clock (12-way parallel) | 0.7 h | 2.2 h | 2.1 h | 3.9 h | 8.0 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | | |
| **Results** | | | | | |
| Resolved | 🥉 30 | 28 | 🥇 **32** | 🥈 31 | 🥉 30 |
| Resolved % | 🥉 67% | 62% | 🥇 **71%** | 🥈 69% | 🥉 67% |
| Total cost | 🥇 **$22.84** | 🥈 $30.34 | 🥉 $33.97 | $80.88 | $203.65 |
| $/resolved | 🥇 **$0.76** | 🥉 $1.08 | 🥈 $1.06 | $2.61 | $6.79 |
| **Stats** | | | | | |
| Steps (total) | 1,002 | 1,090 | 1,217 | 1,801 | 2,643 |
| Turns/instance (avg) | 22.3 | 24.2 | 27.0 | 40.0 | 58.7 |
| Cost/turn (avg) | $0.023 | $0.028 | $0.028 | $0.045 | $0.077 |
| Output tokens | 373k | 542k | 578k | 1.34M | 3.30M |
| Thinking (output) | — | — | — | — | — |
| Input tokens | 16.87M | 20.45M | 24.67M | 66.22M | 185.71M |
| — non-cached | 2k | 2k | 2k | 4k | 5k |
| — cache read | 15.98M | 19.31M | 23.42M | 63.72M | 180.77M |
| — cache write | 884k | 1.14M | 1.25M | 2.49M | 4.93M |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 | 0 |
| Input tokens/turn (avg) | 16,834 | 18,766 | 20,273 | 36,766 | 70,266 |
| Output tokens/turn (avg) | 372 | 497 | 475 | 742 | 1,247 |
| Context window (peak, single turn) | 87k | 73k | 85k | 141k | 433k |
| Wall-clock (12-way parallel) | 1.6 h | 2.2 h | 2.3 h | 5.0 h | 11.8 h |
| **Combined — 105 *Python* events** | | | | | |
| **Results** | | | | | |
| Resolved | 🥈 78 | 🥉 76 | 🥇 **83** | 🥇 **83** | 🥇 **83** |
| Resolved % | 🥈 74% | 🥉 72% | 🥇 **79%** | 🥇 **79%** | 🥇 **79%** |
| Total cost | 🥇 **$31.57** | 🥈 $45.64 | 🥉 $54.97 | $135.79 | $327.67 |
| $/resolved | 🥇 **$0.40** | 🥈 $0.60 | 🥉 $0.66 | $1.64 | $3.95 |
| **Stats** | | | | | |
| Steps (total) | 1,562 | 1,836 | 2,104 | 3,254 | 4,746 |
| Turns/instance (avg) | 14.9 | 17.5 | 20.0 | 31.0 | 45.2 |
| Cost/turn (avg) | $0.020 | $0.025 | $0.026 | $0.042 | $0.069 |
| Output tokens | 522k | 822k | 978k | 2.33M | 5.54M |
| Thinking (output) | — | — | — | — | — |
| Input tokens | 21.11M | 28.94M | 36.75M | 104.81M | 279.24M |
| — non-cached | 3k | 4k | 4k | 7k | 9k |
| — cache read | 19.73M | 27.10M | 34.64M | 100.44M | 270.63M |
| — cache write | 1.38M | 1.84M | 2.11M | 4.36M | 8.60M |
| Failed tool calls (FormatError) | 0 | 0 | 2 | 0 | 0 |
| Input tokens/turn (avg) | 13,516 | 15,765 | 17,466 | 32,208 | 58,837 |
| Output tokens/turn (avg) | 334 | 448 | 465 | 717 | 1,168 |
| Context window (peak, single turn) | 87k | 73k | 85k | 156k | 433k |
| Wall-clock (12-way parallel) | 2.3 h | 4.4 h | 4.4 h | 8.9 h | 19.7 h |
| **Medal tally — per instance (105 events, 12 unsolved by every model)** | | | | | |
| 🥇 gold | 55 | 17 | 16 | 4 | 1 |
| 🥈 silver | 18 | 35 | 24 | 5 | 4 |
| 🥉 bronze | 4 | 21 | 40 | 12 | 5 |
| placing | 🥇 **1** | 🥈 **2** | 🥉 **3** | 4 | 5 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
