| Effort division — Claude Opus 5 (SWE-bench Verified) | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | | |
| **Results** | | | | | |
| Resolved | 48 | 55 | 🥉 56 | 🥈 58 | 🥇 **59** |
| Resolved % | 80% | 92% | 🥉 93% | 🥈 97% | 🥇 **98%** |
| Total cost | 🥇 **$5.50** | 🥈 $9.42 | 🥉 $18.81 | $36.76 | $64.38 |
| $/resolved | 🥇 **$0.11** | 🥈 $0.17 | 🥉 $0.34 | $0.63 | $1.09 |
| **Stats** | | | | | |
| Steps (total) | 393 | 523 | 795 | 1,171 | 1,619 |
| Turns/instance (avg) | 6.5 | 8.7 | 13.2 | 19.5 | 27.0 |
| Cost/turn (avg) | $0.014 | $0.018 | $0.024 | $0.031 | $0.040 |
| Output tokens | 84k | 160k | 326k | 636k | 1.09M |
| Thinking (output) | 21k | 68k | 151k | 361k | 661k |
| Input tokens | 2.32M | 4.35M | 10.43M | 23.90M | 46.73M |
| — non-cached | 1k | 1k | 2k | 2k | 3k |
| — cache read | 1.94M | 3.78M | 9.49M | 22.35M | 44.35M |
| — cache write | 387k | 564k | 947k | 1.55M | 2.38M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 5,916 | 8,315 | 13,124 | 20,408 | 28,862 |
| Output tokens/turn (avg) | 214 | 306 | 410 | 543 | 675 |
| Context window (peak, single turn) | 26k | 36k | 62k | 72k | 159k |
| Wall-clock (12-way parallel) | 0.3 h | 0.6 h | 1.3 h | 2.4 h | 3.9 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | | |
| **Results** | | | | | |
| Resolved | 26 | 33 | 🥉 38 | 🥈 41 | 🥇 **44** |
| Resolved % | 58% | 73% | 🥉 84% | 🥈 91% | 🥇 **98%** |
| Total cost | 🥇 **$9.23** | 🥈 $16.25 | 🥉 $37.65 | $70.14 | $96.03 |
| $/resolved | 🥇 **$0.35** | 🥈 $0.49 | 🥉 $0.99 | $1.71 | $2.18 |
| **Stats** | | | | | |
| Steps (total) | 461 | 669 | 1,131 | 1,585 | 1,891 |
| Turns/instance (avg) | 10.2 | 14.9 | 25.1 | 35.2 | 42.0 |
| Cost/turn (avg) | $0.020 | $0.024 | $0.033 | $0.044 | $0.051 |
| Output tokens | 157k | 271k | 595k | 1.03M | 1.42M |
| Thinking (output) | 53k | 137k | 321k | 602k | 899k |
| Input tokens | 4.33M | 9.45M | 28.54M | 61.84M | 85.30M |
| — non-cached | 1k | 1k | 2k | 3k | 4k |
| — cache read | 3.79M | 8.62M | 27.06M | 59.48M | 82.20M |
| — cache write | 546k | 828k | 1.48M | 2.35M | 3.10M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 1 | 0 |
| Input tokens/turn (avg) | 9,400 | 14,126 | 25,235 | 39,016 | 45,107 |
| Output tokens/turn (avg) | 340 | 404 | 526 | 648 | 752 |
| Context window (peak, single turn) | 28k | 43k | 107k | 135k | 134k |
| Wall-clock (12-way parallel) | 0.6 h | 1.0 h | 2.3 h | 3.7 h | 5.0 h |
| **Combined — 105 *Python* events** | | | | | |
| **Results** | | | | | |
| Resolved | 74 | 88 | 🥉 94 | 🥈 99 | 🥇 **103** |
| Resolved % | 70% | 84% | 🥉 90% | 🥈 94% | 🥇 **98%** |
| Total cost | 🥇 **$14.72** | 🥈 $25.67 | 🥉 $56.46 | $106.89 | $160.42 |
| $/resolved | 🥇 **$0.20** | 🥈 $0.29 | 🥉 $0.60 | $1.08 | $1.56 |
| **Stats** | | | | | |
| Steps (total) | 854 | 1,192 | 1,926 | 2,756 | 3,510 |
| Turns/instance (avg) | 8.1 | 11.4 | 18.3 | 26.2 | 33.4 |
| Cost/turn (avg) | $0.017 | $0.022 | $0.029 | $0.039 | $0.046 |
| Output tokens | 241k | 430k | 921k | 1.66M | 2.52M |
| Thinking (output) | 74k | 205k | 471k | 963k | 1.56M |
| Input tokens | 6.66M | 13.80M | 38.97M | 85.74M | 132.03M |
| — non-cached | 2k | 2k | 4k | 6k | 7k |
| — cache read | 5.72M | 12.40M | 36.55M | 81.83M | 126.55M |
| — cache write | 933k | 1.39M | 2.42M | 3.90M | 5.47M |
| Failed tool calls (FormatError) | 0 | 0 | 0 | 2 | 0 |
| Input tokens/turn (avg) | 7,797 | 11,576 | 20,236 | 31,110 | 37,614 |
| Output tokens/turn (avg) | 282 | 361 | 478 | 603 | 717 |
| Context window (peak, single turn) | 28k | 43k | 107k | 135k | 159k |
| Wall-clock (12-way parallel) | 1.0 h | 1.7 h | 3.5 h | 6.1 h | 8.9 h |
| **Medal tally — per instance (105 events, 1 unsolved by every model)** | | | | | |
| 🥇 gold | 66 | 23 | 7 | 4 | 4 |
| 🥈 silver | 8 | 64 | 16 | 10 | 3 |
| 🥉 bronze | 0 | 1 | 69 | 15 | 13 |
| placing | 🥇 **1** | 🥈 **2** | 🥉 **3** | 4 | 5 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
