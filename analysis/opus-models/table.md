| Opus division — the lineage (SWE-bench Verified) | Claude Opus 4.6 | Claude Opus 4.7 | Claude Opus 4.8 | Claude Opus 5 |
|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 46 | 🥉 50 | 🥈 51 | 🥇 **56** |
| Resolved % | 77% | 🥉 83% | 🥈 85% | 🥇 **93%** |
| Total cost | 🥉 $24.48 | $25.90 | 🥈 $21.00 | 🥇 **$18.81** |
| $/resolved | $0.53 | 🥉 $0.52 | 🥈 $0.41 | 🥇 **$0.34** |
| **Stats** | | | | |
| Steps (total) | 1,236 | 1,179 | 887 | 795 |
| Turns/instance (avg) | 20.6 | 19.6 | 14.8 | 13.2 |
| Cost/turn (avg) | $0.020 | $0.022 | $0.024 | $0.024 |
| Output tokens | 327k | 409k | 400k | 326k |
| Thinking (output) | 127k | 190k | — | 151k |
| Input tokens | 17.01M | 19.69M | 12.08M | 10.43M |
| — non-cached | 669k | 1k | 2k | 2k |
| — cache read | 15.51M | 18.68M | 11.21M | 9.49M |
| — cache write | 831k | 1.01M | 862k | 947k |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 13,758 | 16,704 | 13,614 | 13,124 |
| Output tokens/turn (avg) | 265 | 347 | 451 | 410 |
| Context window (peak, single turn) | 73k | 73k | 63k | 62k |
| Wall-clock (12-way parallel) | 1.8 h | 1.7 h | 2.1 h | 1.3 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 18 | 🥉 25 | 🥈 32 | 🥇 **38** |
| Resolved % | 40% | 🥉 56% | 🥈 71% | 🥇 **84%** |
| Total cost | $52.14 | 🥉 $51.92 | 🥇 **$33.97** | 🥈 $37.65 |
| $/resolved | $2.90 | 🥉 $2.08 | 🥈 $1.06 | 🥇 **$0.99** |
| **Stats** | | | | |
| Steps (total) | 1,799 | 1,718 | 1,217 | 1,131 |
| Turns/instance (avg) | 40.0 | 38.2 | 27.0 | 25.1 |
| Cost/turn (avg) | $0.029 | $0.030 | $0.028 | $0.033 |
| Output tokens | 676k | 703k | 578k | 595k |
| Thinking (output) | 299k | 346k | — | 321k |
| Input tokens | 50.22M | 50.51M | 24.67M | 28.54M |
| — non-cached | 309k | 2k | 2k | 2k |
| — cache read | 48.39M | 48.92M | 23.42M | 27.06M |
| — cache write | 1.52M | 1.58M | 1.25M | 1.48M |
| Failed tool calls (FormatError) | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 27,916 | 29,398 | 20,273 | 25,235 |
| Output tokens/turn (avg) | 376 | 409 | 475 | 526 |
| Context window (peak, single turn) | 129k | 117k | 85k | 107k |
| Wall-clock (12-way parallel) | 3.7 h | 2.9 h | 2.3 h | 2.3 h |
| **Combined — 105 *Python* events** | | | | |
| **Results** | | | | |
| Resolved | 64 | 🥉 75 | 🥈 83 | 🥇 **94** |
| Resolved % | 61% | 🥉 71% | 🥈 79% | 🥇 **90%** |
| Total cost | 🥉 $76.61 | $77.82 | 🥇 **$54.97** | 🥈 $56.46 |
| $/resolved | $1.20 | 🥉 $1.04 | 🥈 $0.66 | 🥇 **$0.60** |
| **Stats** | | | | |
| Steps (total) | 3,035 | 2,897 | 2,104 | 1,926 |
| Turns/instance (avg) | 28.9 | 27.6 | 20.0 | 18.3 |
| Cost/turn (avg) | $0.025 | $0.027 | $0.026 | $0.029 |
| Output tokens | 1.00M | 1.11M | 978k | 921k |
| Thinking (output) | 426k | 536k | — | 471k |
| Input tokens | 67.23M | 70.20M | 36.75M | 38.97M |
| — non-cached | 979k | 3k | 4k | 4k |
| — cache read | 63.90M | 67.60M | 34.64M | 36.55M |
| — cache write | 2.35M | 2.60M | 2.11M | 2.42M |
| Failed tool calls (FormatError) | 0 | 0 | 2 | 0 |
| Input tokens/turn (avg) | 22,150 | 24,232 | 17,466 | 20,236 |
| Output tokens/turn (avg) | 331 | 384 | 465 | 478 |
| Context window (peak, single turn) | 129k | 117k | 85k | 107k |
| Wall-clock (12-way parallel) | 5.6 h | 4.7 h | 4.4 h | 3.5 h |
| **Medal tally — per instance (105 events, 7 unsolved by every model)** | | | | |
| 🥇 gold | 4 | 13 | 46 | 35 |
| 🥈 silver | 12 | 25 | 26 | 24 |
| 🥉 bronze | 21 | 22 | 6 | 23 |
| placing | 4 | 🥉 **3** | 🥇 **1** | 🥈 **2** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
