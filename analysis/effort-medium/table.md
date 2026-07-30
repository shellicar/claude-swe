| Medium-effort division — every contender (SWE-bench Verified) | Claude Opus 4.8 | Claude Opus 5 |
|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | |
| **Results** | | |
| Resolved | 🥈 48 | 🥇 **55** |
| Resolved % | 🥈 80% | 🥇 **92%** |
| Total cost | 🥈 $15.30 | 🥇 **$9.42** |
| $/resolved | 🥈 $0.32 | 🥇 **$0.17** |
| **Stats** | | |
| Steps (total) | 746 | 523 |
| Turns/instance (avg) | 12.4 | 8.7 |
| Cost/turn (avg) | $0.021 | $0.018 |
| Output tokens | 281k | 160k |
| Thinking (output) | — | 68k |
| Input tokens | 8.49M | 4.35M |
| — non-cached | 1k | 1k |
| — cache read | 7.79M | 3.78M |
| — cache write | 700k | 564k |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 11,379 | 8,315 |
| Output tokens/turn (avg) | 377 | 306 |
| Context window (peak, single turn) | 49k | 36k |
| Wall-clock (12-way parallel) | 2.2 h | 0.6 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | |
| **Results** | | |
| Resolved | 🥈 28 | 🥇 **33** |
| Resolved % | 🥈 62% | 🥇 **73%** |
| Total cost | 🥈 $30.34 | 🥇 **$16.25** |
| $/resolved | 🥈 $1.08 | 🥇 **$0.49** |
| **Stats** | | |
| Steps (total) | 1,090 | 669 |
| Turns/instance (avg) | 24.2 | 14.9 |
| Cost/turn (avg) | $0.028 | $0.024 |
| Output tokens | 542k | 271k |
| Thinking (output) | — | 137k |
| Input tokens | 20.45M | 9.45M |
| — non-cached | 2k | 1k |
| — cache read | 19.31M | 8.62M |
| — cache write | 1.14M | 828k |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 18,766 | 14,126 |
| Output tokens/turn (avg) | 497 | 404 |
| Context window (peak, single turn) | 73k | 43k |
| Wall-clock (12-way parallel) | 2.2 h | 1.0 h |
| **Combined — 105 *Python* events** | | |
| **Results** | | |
| Resolved | 🥈 76 | 🥇 **88** |
| Resolved % | 🥈 72% | 🥇 **84%** |
| Total cost | 🥈 $45.64 | 🥇 **$25.67** |
| $/resolved | 🥈 $0.60 | 🥇 **$0.29** |
| **Stats** | | |
| Steps (total) | 1,836 | 1,192 |
| Turns/instance (avg) | 17.5 | 11.4 |
| Cost/turn (avg) | $0.025 | $0.022 |
| Output tokens | 822k | 430k |
| Thinking (output) | — | 205k |
| Input tokens | 28.94M | 13.80M |
| — non-cached | 4k | 2k |
| — cache read | 27.10M | 12.40M |
| — cache write | 1.84M | 1.39M |
| Failed tool calls (FormatError) | 0 | 0 |
| Input tokens/turn (avg) | 15,765 | 11,576 |
| Output tokens/turn (avg) | 448 | 361 |
| Context window (peak, single turn) | 73k | 43k |
| Wall-clock (12-way parallel) | 4.4 h | 1.7 h |
| **Medal tally — per instance (105 events, 14 unsolved by every model)** | | |
| 🥇 gold | 17 | 74 |
| 🥈 silver | 59 | 14 |
| 🥉 bronze | 0 | 0 |
| placing | 🥈 **2** | 🥇 **1** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
