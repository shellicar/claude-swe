| Tool & execution-mechanism division — SWE-bench Verified hard, Sonnet 5 | Control | Exec Arm 1 | ExecV1, aligned | ExecV2, aligned | ExecV3, aligned (bash-named) | ExecV3, aligned (exec-named) | ExecV3, no ritual | +90 bloat tools | +Edit/Write/Read, neutral | +Edit/Write/Read, prefer | ExecV3 +Edit/Write/Read | ExecV3 +EWR, plain output |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Variables** | | | | | | | | | | | | |
| Shell tool | bash | ExecV3 | ExecV1 | ExecV2 | ExecV3 | ExecV3 | ExecV3 | bash | bash | bash | ExecV3 | ExecV3 |
| Tool name shown to model | bash | bash | bash | bash | bash | exec | bash | bash | bash | bash | bash | bash |
| Prompt | bash | bash (mismatched) | exec-aligned | exec-aligned | exec-aligned | exec-aligned | exec-aligned | bash | bash | bash + prefer | bash + prefer | bash + prefer |
| Extra tools | — | — | — | — | — | — | — | +90 unusable | Edit/Write/Read | Edit/Write/Read | Edit/Write/Read | Edit/Write/Read |
| Submission | ritual | ritual | ritual | ritual | ritual | ritual | pen-down | ritual | ritual | ritual | ritual | ritual |
| Output format | text | block | block | block | block | block | block | text | text | text | block | plain |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | | | | | | | | | |
| **Results** | | | | | | | | | | | | |
| Resolved | 🥉 34 | 32 | 32 | 33 | 🥉 34 | 33 | 33 | 🥈 35 | 🥉 34 | 🥇 **36** | 33 | 32 |
| Resolved % | 🥉 76% | 71% | 71% | 73% | 🥉 76% | 73% | 73% | 🥈 78% | 🥉 76% | 🥇 **80%** | 73% | 71% |
| Total cost | 🥈 $39.63 | $51.74 | $50.69 | $43.62 | $42.11 | $40.84 | $40.51 | $56.72 | 🥉 $40.01 | 🥇 **$34.36** | $45.14 | $46.20 |
| $/resolved | 🥈 $1.17 | $1.62 | $1.58 | $1.32 | $1.24 | $1.24 | $1.23 | $1.62 | 🥉 $1.18 | 🥇 **$0.95** | $1.37 | $1.44 |
| **Stats** | | | | | | | | | | | | |
| Steps (total) | 2,206 | 2,395 | 2,345 | 2,184 | 2,118 | 2,063 | 2,067 | 2,052 | 2,250 | 2,129 | 2,207 | 2,208 |
| Turns/instance (avg) | 49.0 | 53.2 | 52.1 | 48.5 | 47.1 | 45.8 | 45.9 | 45.6 | 50.0 | 47.3 | 49.0 | 49.1 |
| Cost/turn (avg) | $0.018 | $0.022 | $0.022 | $0.020 | $0.020 | $0.020 | $0.020 | $0.028 | $0.018 | $0.016 | $0.020 | $0.021 |
| Output tokens | 725k | 938k | 920k | 796k | 799k | 771k | 804k | 669k | 662k | 580k | 798k | 825k |
| Thinking (output) | — | — | — | — | — | — | — | — | — | — | — | — |
| Input tokens | 71.86M | 96.23M | 92.98M | 78.02M | 72.18M | 71.06M | 69.12M | 132.47M | 75.73M | 64.07M | 84.20M | 85.70M |
| — non-cached | 4k | 5k | 5k | 4k | 4k | 4k | 4k | 4k | 4k | 4k | 4k | 4k |
| — cache read | 69.78M | 93.68M | 90.37M | 75.62M | 69.72M | 68.75M | 66.89M | 130.46M | 73.60M | 62.21M | 81.91M | 83.34M |
| — cache write | 2.08M | 2.55M | 2.60M | 2.39M | 2.45M | 2.30M | 2.23M | 2.01M | 2.13M | 1.86M | 2.29M | 2.35M |
| Input tokens/turn (avg) | 32,575 | 40,181 | 39,651 | 35,724 | 34,080 | 34,443 | 33,442 | 64,558 | 33,659 | 30,096 | 38,151 | 38,812 |
| Output tokens/turn (avg) | 329 | 392 | 392 | 365 | 377 | 374 | 389 | 326 | 294 | 273 | 362 | 374 |
| Context window (peak, single turn) | 134k | 166k | 149k | 119k | 111k | 118k | 127k | 141k | 115k | 130k | 161k | 147k |
| Wall-clock (12-way parallel) | 3.5 h | 3.5 h | 3.2 h | 2.8 h | 3.3 h | 2.8 h | 2.7 h | 2.4 h | 2.8 h | 2.7 h | 3.0 h | 3.0 h |
| **Medal tally — counted in events** | | | | | | | | | | | | |
| 🥇 gold | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 🥈 silver | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 🥉 bronze | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
