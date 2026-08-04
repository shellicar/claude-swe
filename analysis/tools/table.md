| Exec-grammar division — SWE-bench Verified hard, Sonnet 5 | Control | Exec Arm 1 | ExecV1, aligned | ExecV2, aligned | ExecV3, aligned (bash-named) | ExecV3, aligned (exec-named) | ExecV3, no ritual |
|---|---|---|---|---|---|---|---|
| **Variables** | **Control** | **Exec Arm 1** | **ExecV1, aligned** | **ExecV2, aligned** | **ExecV3, aligned (bash-named)** | **ExecV3, aligned (exec-named)** | **ExecV3, no ritual** |
| Shell tool | bash | ExecV3 | ExecV1 | ExecV2 | ExecV3 | ExecV3 | ExecV3 |
| Tool name shown to model | bash | bash | bash | bash | bash | exec | bash |
| Input encoding | raw string | JSON | JSON | JSON | JSON | JSON | JSON |
| Prompt | bash | bash (mismatched) | exec-aligned | exec-aligned | exec-aligned | exec-aligned | exec-aligned |
| Extra tools | — | — | — | — | — | — | — |
| Submission | ritual | ritual | ritual | ritual | ritual | ritual | pen-down |
| Output format | text | block | block | block | block | block | block |
| **Hard — 45 *Python* events (1+ h human effort)** | **Control** | **Exec Arm 1** | **ExecV1, aligned** | **ExecV2, aligned** | **ExecV3, aligned (bash-named)** | **ExecV3, aligned (exec-named)** | **ExecV3, no ritual** |
| **Results** | | | | | | | |
| Resolved | 🥇 **34** | 🥉 32 | 🥉 32 | 🥈 33 | 🥇 **34** | 🥈 33 | 🥈 33 |
| Resolved % | 🥇 **76%** | 🥉 71% | 🥉 71% | 🥈 73% | 🥇 **76%** | 🥈 73% | 🥈 73% |
| Total cost | 🥇 **$39.63** | $51.74 | $50.69 | $43.62 | $42.11 | 🥉 $40.84 | 🥈 $40.51 |
| $/resolved | 🥇 **$1.17** | $1.62 | $1.58 | $1.32 | 🥉 $1.24 | 🥉 $1.24 | 🥈 $1.23 |
| **Stats** | | | | | | | |
| Steps (total) | 2,206 | 2,395 | 2,345 | 2,184 | 2,118 | 2,063 | 2,067 |
| Turns/instance (avg) | 49.0 | 53.2 | 52.1 | 48.5 | 47.1 | 45.8 | 45.9 |
| Cost/turn (avg) | $0.018 | $0.022 | $0.022 | $0.020 | $0.020 | $0.020 | $0.020 |
| Output tokens | 725k | 938k | 920k | 796k | 799k | 771k | 804k |
| Thinking (output) | — | — | — | — | — | — | — |
| Input tokens | 71.86M | 96.23M | 92.98M | 78.02M | 72.18M | 71.06M | 69.12M |
| — non-cached | 4k | 5k | 5k | 4k | 4k | 4k | 4k |
| — cache read | 69.78M | 93.68M | 90.37M | 75.62M | 69.72M | 68.75M | 66.89M |
| — cache write | 2.08M | 2.55M | 2.60M | 2.39M | 2.45M | 2.30M | 2.23M |
| Failed tool calls (FormatError) | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Input tokens/turn (avg) | 32,575 | 40,181 | 39,651 | 35,724 | 34,080 | 34,443 | 33,442 |
| Output tokens/turn (avg) | 329 | 392 | 392 | 365 | 377 | 374 | 389 |
| Context window (peak, single turn) | 134k | 166k | 149k | 119k | 111k | 118k | 127k |
| Wall-clock (12-way parallel) | 3.5 h | 3.5 h | 3.2 h | 2.8 h | 3.3 h | 2.8 h | 2.7 h |
| **Medal tally — per instance (45 events, 4 unsolved by every arm)** | **Control** | **Exec Arm 1** | **ExecV1, aligned** | **ExecV2, aligned** | **ExecV3, aligned (bash-named)** | **ExecV3, aligned (exec-named)** | **ExecV3, no ritual** |
| **medals** | | | | | | | |
| 🥇 gold | 14 | 5 | 1 | 3 | 4 | 7 | 7 |
| 🥈 silver | 4 | 3 | 4 | 8 | 5 | 6 | 10 |
| 🥉 bronze | 4 | 3 | 6 | 8 | 6 | 6 | 3 |
| placing | 🥇 **1** | 4 | 7 | 6 | 5 | 🥉 **3** | 🥈 **2** |

Verdicts from the pinned swebench judges. Full caveats in report.md.

| Tool-alternatives division — SWE-bench Verified hard, Sonnet 5 | Control | +90 bloat tools | +Edit/Write/Read, neutral | +Edit/Write/Read, prefer | ExecV3 +Edit/Write/Read | ExecV3 +EWR, plain output |
|---|---|---|---|---|---|---|
| **Variables** | **Control** | **+90 bloat tools** | **+Edit/Write/Read, neutral** | **+Edit/Write/Read, prefer** | **ExecV3 +Edit/Write/Read** | **ExecV3 +EWR, plain output** |
| Shell tool | bash | bash | bash | bash | ExecV3 | ExecV3 |
| Tool name shown to model | bash | bash | bash | bash | bash | bash |
| Input encoding | raw string | raw string | raw string | raw string | JSON | JSON |
| Prompt | bash | bash | bash | bash + prefer | bash + prefer | bash + prefer |
| Extra tools | — | +90 unusable | Edit/Write/Read | Edit/Write/Read | Edit/Write/Read | Edit/Write/Read |
| Submission | ritual | ritual | ritual | ritual | ritual | ritual |
| Output format | text | text | text | text | block | plain |
| **Hard — 45 *Python* events (1+ h human effort)** | **Control** | **+90 bloat tools** | **+Edit/Write/Read, neutral** | **+Edit/Write/Read, prefer** | **ExecV3 +Edit/Write/Read** | **ExecV3 +EWR, plain output** |
| **Results** | | | | | | |
| Resolved | 🥉 34 | 🥈 35 | 🥉 34 | 🥇 **36** | 33 | 32 |
| Resolved % | 🥉 76% | 🥈 78% | 🥉 76% | 🥇 **80%** | 73% | 71% |
| Total cost | 🥈 $39.63 | $56.72 | 🥉 $40.01 | 🥇 **$34.36** | $45.14 | $46.20 |
| $/resolved | 🥈 $1.17 | $1.62 | 🥉 $1.18 | 🥇 **$0.95** | $1.37 | $1.44 |
| **Stats** | | | | | | |
| Steps (total) | 2,206 | 2,052 | 2,250 | 2,129 | 2,207 | 2,208 |
| Turns/instance (avg) | 49.0 | 45.6 | 50.0 | 47.3 | 49.0 | 49.1 |
| Cost/turn (avg) | $0.018 | $0.028 | $0.018 | $0.016 | $0.020 | $0.021 |
| Output tokens | 725k | 669k | 662k | 580k | 798k | 825k |
| Thinking (output) | — | — | — | — | — | — |
| Input tokens | 71.86M | 132.47M | 75.73M | 64.07M | 84.20M | 85.70M |
| — non-cached | 4k | 4k | 4k | 4k | 4k | 4k |
| — cache read | 69.78M | 130.46M | 73.60M | 62.21M | 81.91M | 83.34M |
| — cache write | 2.08M | 2.01M | 2.13M | 1.86M | 2.29M | 2.35M |
| Failed tool calls (FormatError) | 0 | 1 | 1 | 0 | 2 | 0 |
| Input tokens/turn (avg) | 32,575 | 64,558 | 33,659 | 30,096 | 38,151 | 38,812 |
| Output tokens/turn (avg) | 329 | 326 | 294 | 273 | 362 | 374 |
| Context window (peak, single turn) | 134k | 141k | 115k | 130k | 161k | 147k |
| Wall-clock (12-way parallel) | 3.5 h | 2.4 h | 2.8 h | 2.7 h | 3.0 h | 3.0 h |
| **Medal tally — per instance (45 events, 6 unsolved by every arm)** | **Control** | **+90 bloat tools** | **+Edit/Write/Read, neutral** | **+Edit/Write/Read, prefer** | **ExecV3 +Edit/Write/Read** | **ExecV3 +EWR, plain output** |
| **medals** | | | | | | |
| 🥇 gold | 7 | 0 | 12 | 11 | 5 | 4 |
| 🥈 silver | 13 | 2 | 7 | 7 | 6 | 3 |
| 🥉 bronze | 8 | 3 | 7 | 8 | 4 | 8 |
| placing | 🥉 **3** | 6 | 🥇 **1** | 🥈 **2** | 4 | 5 |

Verdicts from the pinned swebench judges. Full caveats in report.md.

| Plain-text encoding division — SWE-bench Verified hard, Sonnet 5 | Control | ExecV3, plain-text (symbolic) | ExecV3, plain-text (symbolic, loud) | ExecV3, plain-text (keyword) |
|---|---|---|---|---|
| **Variables** | **Control** | **ExecV3, plain-text (symbolic)** | **ExecV3, plain-text (symbolic, loud)** | **ExecV3, plain-text (keyword)** |
| Shell tool | bash | ExecV3 | ExecV3 | ExecV3 |
| Tool name shown to model | bash | bash | bash | bash |
| Input encoding | raw string | text (symbolic) | text (symbolic) | text (keyword) |
| Prompt | bash | text-aligned | text-aligned + loud | keyword-aligned |
| Extra tools | — | — | — | — |
| Submission | ritual | ritual | ritual | ritual |
| Output format | text | block | block | block |
| **Hard — 45 *Python* events (1+ h human effort)** | **Control** | **ExecV3, plain-text (symbolic)** | **ExecV3, plain-text (symbolic, loud)** | **ExecV3, plain-text (keyword)** |
| **Results** | | | | |
| Resolved | 🥇 **34** | 🥇 **34** | 🥈 31 | 🥉 30 |
| Resolved % | 🥇 **76%** | 🥇 **76%** | 🥈 69% | 🥉 67% |
| Total cost | 🥇 **$39.63** | $74.56 | 🥉 $66.07 | 🥈 $53.05 |
| $/resolved | 🥇 **$1.17** | $2.19 | 🥉 $2.13 | 🥈 $1.77 |
| **Stats** | | | | |
| Steps (total) | 2,206 | 3,824 | 3,775 | 2,410 |
| Turns/instance (avg) | 49.0 | 85.0 | 83.9 | 53.6 |
| Cost/turn (avg) | $0.018 | $0.019 | $0.018 | $0.022 |
| Output tokens | 725k | 1.29M | 1.17M | 926k |
| Thinking (output) | — | — | — | — |
| Input tokens | 71.86M | 148.35M | 128.55M | 86.21M |
| — non-cached | 4k | 8k | 7k | 5k |
| — cache read | 69.78M | 145.26M | 125.68M | 82.36M |
| — cache write | 2.08M | 3.08M | 2.87M | 3.85M |
| Failed tool calls (FormatError) | 0 | 0 | 375 | 5 |
| Input tokens/turn (avg) | 32,575 | 38,795 | 34,054 | 35,773 |
| Output tokens/turn (avg) | 329 | 338 | 311 | 384 |
| Context window (peak, single turn) | 134k | 143k | 156k | 151k |
| Wall-clock (12-way parallel) | 3.5 h | 5.0 h | 6.1 h | 18.5 h |
| **Medal tally — per instance (45 events, 5 unsolved by every arm)** | **Control** | **ExecV3, plain-text (symbolic)** | **ExecV3, plain-text (symbolic, loud)** | **ExecV3, plain-text (keyword)** |
| **medals** | | | | |
| 🥇 gold | 25 | 3 | 2 | 10 |
| 🥈 silver | 5 | 9 | 10 | 10 |
| 🥉 bronze | 2 | 12 | 10 | 9 |
| placing | 🥇 **1** | 🥉 **3** | 4 | 🥈 **2** |

Verdicts from the pinned swebench judges. Full caveats in report.md.
