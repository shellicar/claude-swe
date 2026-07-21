| Tool-alternatives division — SWE-bench Verified hard, Sonnet 5 | Sonnet 5 — bash (control) | Sonnet 5 — Arm 1: schema bloat (bash + 90 unusable tools) | Sonnet 5 — Arm 2: +Edit/Write/Read, neutral | Sonnet 5 — Arm 3: +Edit/Write/Read, prompted to prefer them | Sonnet 5 — Arm 4: ExecV3 instead of bash, +Edit/Write/Read | Sonnet 5 — Arm 5: Arm 4, exec output flattened to plain text |
|---|---|---|---|---|---|---|
| **Hard — 45 *Python* events (1+ h human effort)** | | | | | | |
| **Results** | | | | | | |
| Resolved | 🥉 34 | 🥈 35 | 🥉 34 | 🥇 **36** | 33 | — |
| Resolved % | 🥉 76% | 🥈 78% | 🥉 76% | 🥇 **80%** | 73% | — |
| Total cost | 🥈 $39.63 | $56.72 | 🥉 $40.01 | 🥇 **$34.36** | $45.14 | — |
| $/resolved | 🥈 $1.17 | $1.62 | 🥉 $1.18 | 🥇 **$0.95** | $1.37 | — |
| **Stats** | | | | | | |
| Steps (total) | 2,206 | 2,052 | 2,250 | 2,129 | 2,207 | — |
| Turns/instance (avg) | 49.0 | 45.6 | 50.0 | 47.3 | 49.0 | — |
| Cost/turn (avg) | $0.018 | $0.028 | $0.018 | $0.016 | $0.020 | — |
| Output tokens | 725k | 669k | 662k | 580k | 798k | — |
| Thinking (output) | — | — | — | — | — | — |
| Input tokens | 71.86M | 132.47M | 75.73M | 64.07M | 84.20M | — |
| — non-cached | 4k | 4k | 4k | 4k | 4k | — |
| — cache read | 69.78M | 130.46M | 73.60M | 62.21M | 81.91M | — |
| — cache write | 2.08M | 2.01M | 2.13M | 1.86M | 2.29M | — |
| Input tokens/turn (avg) | 32,575 | 64,558 | 33,659 | 30,096 | 38,151 | — |
| Output tokens/turn (avg) | 329 | 326 | 294 | 273 | 362 | — |
| Context window (peak, single turn) | 134k | 141k | 115k | 130k | 161k | — |
| Wall-clock (12-way parallel) | 3.5 h | 2.4 h | 2.8 h | 2.7 h | 3.0 h | — |
| **Medal tally — counted in events** | | | | | | |
| 🥇 gold | 0 | 0 | 0 | 1 | 0 | 0 |
| 🥈 silver | 0 | 1 | 0 | 0 | 0 | 0 |
| 🥉 bronze | 1 | 0 | 1 | 0 | 0 | 0 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
