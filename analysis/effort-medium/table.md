| Medium-effort division — every contender (SWE-bench Verified) | Claude Opus 5 | Claude Opus 4.8 | Claude Sonnet 5 |
|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥇 **55** | 🥈 48 | 🥉 46 |
| Resolved % | 🥇 **92%** | 🥈 80% | 🥉 77% |
| Total cost | 🥇 **$9.42** | 🥉 $15.30 | 🥈 $11.31 |
| $/resolved | 🥇 **$0.17** | 🥉 $0.32 | 🥈 $0.25 |
| **Stats** | | | |
| Steps (total) | 523 | 746 | 991 |
| Turns/instance (avg) | 8.7 | 12.4 | 16.5 |
| Cost/turn (avg) | $0.018 | $0.021 | $0.011 |
| Output tokens | 160k | 281k | 264k |
| Thinking (output) | 68k | — | 84k |
| Input tokens | 4.35M | 8.49M | 14.35M |
| — non-cached | 1k | 1k | 2k |
| — cache read | 3.78M | 7.79M | 13.46M |
| — cache write | 564k | 700k | 882k |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 8,315 | 11,379 | 14,476 |
| Output tokens/turn (avg) | 306 | 377 | 266 |
| Context window (peak, single turn) | 36k | 49k | 67k |
| Wall-clock (12-way parallel) | 0.6 h | 2.2 h | 1.0 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | |
| **Results** | | | |
| Resolved | 🥇 **33** | 🥉 28 | 🥈 31 |
| Resolved % | 🥇 **73%** | 🥉 62% | 🥈 69% |
| Total cost | 🥇 **$16.25** | 🥉 $30.34 | 🥈 $24.25 |
| $/resolved | 🥇 **$0.49** | 🥉 $1.08 | 🥈 $0.78 |
| **Stats** | | | |
| Steps (total) | 669 | 1,090 | 1,666 |
| Turns/instance (avg) | 14.9 | 24.2 | 37.0 |
| Cost/turn (avg) | $0.024 | $0.028 | $0.015 |
| Output tokens | 271k | 542k | 456k |
| Thinking (output) | 137k | — | 141k |
| Input tokens | 9.45M | 20.45M | 40.46M |
| — non-cached | 1k | 2k | 3k |
| — cache read | 8.62M | 19.31M | 38.93M |
| — cache write | 828k | 1.14M | 1.53M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 14,126 | 18,766 | 24,286 |
| Output tokens/turn (avg) | 404 | 497 | 274 |
| Context window (peak, single turn) | 43k | 73k | 91k |
| Wall-clock (12-way parallel) | 1.0 h | 2.2 h | 1.8 h |
| **Combined — 105 *Python* events** | | | |
| **Results** | | | |
| Resolved | 🥇 **88** | 🥉 76 | 🥈 77 |
| Resolved % | 🥇 **84%** | 🥉 72% | 🥈 73% |
| Total cost | 🥇 **$25.67** | 🥉 $45.64 | 🥈 $35.57 |
| $/resolved | 🥇 **$0.29** | 🥉 $0.60 | 🥈 $0.46 |
| **Stats** | | | |
| Steps (total) | 1,192 | 1,836 | 2,657 |
| Turns/instance (avg) | 11.4 | 17.5 | 25.3 |
| Cost/turn (avg) | $0.022 | $0.025 | $0.013 |
| Output tokens | 430k | 822k | 720k |
| Thinking (output) | 205k | — | 225k |
| Input tokens | 13.80M | 28.94M | 54.81M |
| — non-cached | 2k | 4k | 5k |
| — cache read | 12.40M | 27.10M | 52.39M |
| — cache write | 1.39M | 1.84M | 2.41M |
| Failed tool calls (FormatError) | 0 | 0 | 0 |
| Input tokens/turn (avg) | 11,576 | 15,765 | 20,627 |
| Output tokens/turn (avg) | 361 | 448 | 271 |
| Context window (peak, single turn) | 43k | 73k | 91k |
| Wall-clock (12-way parallel) | 1.7 h | 4.4 h | 2.8 h |
| **Medal tally — per instance (105 events, 10 unsolved by every model)** | | | |
| 🥇 gold | 52 | 6 | 37 |
| 🥈 silver | 25 | 38 | 20 |
| 🥉 bronze | 11 | 32 | 20 |
| placing | 🥇 **1** | 🥉 **3** | 🥈 **2** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
