| Multi-SWE-bench | fable-5 | opus-4-8 | sonnet-5 |
|---|---|---|---|
| **cpp control (20 instances)** | | | |
| Instances | 20 | 20 | 20 |
| Resolved | 14 | 13 | 12 |
| Resolved % | 70% | 65% | 60% |
| $/resolved | $2.15 | $1.33 | $1.24 |
| Empty patches | 0 | 0 | 0 |
| Total cost | $30.07 | $17.32 | $14.91 |
| $/instance | $1.50 | $0.87 | $0.75 |
| Steps | 503 | 635 | 910 |
| Output tokens | 244k | 260k | 244k |
| Thinking (output) | 126k | 109k | 91k |
| Input tokens | 10.82M | 14.32M | 27.74M |
| - non-cached | 1k | 1k | 2k |
| - cache read | 10.20M | 13.68M | 26.89M |
| - cache write | 613k | 637k | 848k |
| Wall-clock | 1.4 h | 1.0 h | 0.9 h |
| **rust control (20 instances)** | | | |
| Instances | 20 | 20 | 20 |
| Resolved | 14 | 11 | 13 |
| Resolved % | 70% | 55% | 65% |
| $/resolved | $1.28 | $0.97 | $0.73 |
| Empty patches | 0 | 0 | 0 |
| Total cost | $17.86 | $10.64 | $9.46 |
| $/instance | $0.89 | $0.53 | $0.47 |
| Steps | 425 | 466 | 715 |
| Output tokens | 133k | 164k | 159k |
| Thinking (output) | 61k | 86k | 63k |
| Input tokens | 5.87M | 7.92M | 16.27M |
| - non-cached | 1k | 1k | 1k |
| - cache read | 5.41M | 7.47M | 15.63M |
| - cache write | 463k | 449k | 634k |
| Wall-clock | 1.1 h | 0.7 h | 0.7 h |
| **cpp variation (verify + 900s) (20 instances)** | | | |
| Instances | 20 | 20 | 20 |
| Resolved | 14 | 13 | 12 |
| Resolved % | 70% | 65% | 60% |
| $/resolved | $3.41 | $2.48 | $1.72 |
| Empty patches | 2 | 2 | 2 |
| Total cost | $47.71 | $32.21 | $20.61 |
| $/instance | $2.39 | $1.61 | $1.03 |
| Steps | 967 | 1,152 | 1,356 |
| Output tokens | 284k | 328k | 266k |
| Thinking (output) | 124k | 122k | 100k |
| Input tokens | 25.22M | 39.20M | 44.26M |
| - non-cached | 2k | 2k | 3k |
| - cache read | 24.50M | 38.43M | 43.29M |
| - cache write | 719k | 765k | 966k |
| Wall-clock | 2.0 h | 1.5 h | 1.3 h |

Verdicts from ByteDance's Multi-SWE harness; — means a leg is not yet marked.
