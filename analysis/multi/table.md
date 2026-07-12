| Multi-SWE-bench | fable-5 | opus-4-8 | sonnet-5 |
|---|---|---|---|
| **cpp control (20 instances)** | | | |
| **Results** | | | |
| Resolved | **14** 🏆 | 13 | 12 |
| Resolved % | **70%** 🏆 | 65% | 60% |
| Total cost | $30.07 | $17.32 | **$14.91** 🏆 |
| $/resolved | $2.15 | $1.33 | **$1.24** 🏆 |
| — Catch2 | 1/2 | 1/2 | 1/2 |
| — fmt | 0/5 | 0/5 | 0/5 |
| — json | 10/10 | 9/10 | 8/10 |
| — simdjson | 3/3 | 3/3 | 3/3 |
| **Stats** | | | |
| Empty patches | 0 | 0 | 0 |
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
| **Results** | | | |
| Resolved | **14** 🏆 | 11 | 13 |
| Resolved % | **70%** 🏆 | 55% | 65% |
| Total cost | $17.86 | $10.64 | **$9.46** 🏆 |
| $/resolved | $1.28 | $0.97 | **$0.73** 🏆 |
| — bat | 0/1 | 0/1 | 0/1 |
| — clap | 11/12 | 8/12 | 9/12 |
| — fd | 1/1 | 1/1 | 1/1 |
| — nushell | 1/2 | 1/2 | 2/2 |
| — rayon | 1/1 | 1/1 | 1/1 |
| — tokio | 0/3 | 0/3 | 0/3 |
| **Stats** | | | |
| Empty patches | 0 | 0 | 0 |
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
| **Results** | | | |
| Resolved | **14** 🏆 | 13 | 12 |
| Resolved % | **70%** 🏆 | 65% | 60% |
| Total cost | $47.71 | $32.21 | **$20.61** 🏆 |
| $/resolved | $3.41 | $2.48 | **$1.72** 🏆 |
| — Catch2 | 1/2 | 1/2 | 1/2 |
| — fmt | 0/5 | 0/5 | 0/5 |
| — json | 10/10 | 9/10 | 8/10 |
| — simdjson | 3/3 | 3/3 | 3/3 |
| **Stats** | | | |
| Empty patches | 2 | 2 | 2 |
| $/instance | $2.39 | $1.61 | $1.03 |
| Steps | 967 | 1,152 | 1,356 |
| Output tokens | 284k | 328k | 266k |
| Thinking (output) | 124k | 122k | 100k |
| Input tokens | 25.22M | 39.20M | 44.26M |
| - non-cached | 2k | 2k | 3k |
| - cache read | 24.50M | 38.43M | 43.29M |
| - cache write | 719k | 765k | 966k |
| Wall-clock | 2.0 h | 1.5 h | 1.3 h |
| **tokio stack (org tokio-rs) (20 instances)** | | | |
| **Results** | | | |
| Resolved | 10 | **11** 🏆 | **11** 🏆 |
| Resolved % | 50% | **55%** 🏆 | **55%** 🏆 |
| Total cost | $21.64 | $22.37 | **$10.69** 🏆 |
| $/resolved | $2.16 | $2.03 | **$0.97** 🏆 |
| — tokio | 4/10 | 4/10 | 4/10 |
| — tracing | 6/10 | 7/10 | 7/10 |
| **Stats** | | | |
| Empty patches | 0 | 0 | 0 |
| $/instance | $1.08 | $1.12 | $0.53 |
| Steps | 451 | 671 | 641 |
| Output tokens | 166k | 308k | 168k |
| Thinking (output) | 74k | 168k | 65k |
| Input tokens | 7.74M | 18.97M | 19.23M |
| - non-cached | 1k | 1k | 1k |
| - cache read | 7.25M | 18.07M | 18.54M |
| - cache write | 486k | 901k | 695k |
| Wall-clock | 1.1 h | 1.8 h | 0.7 h |

Verdicts from ByteDance's Multi-SWE harness; — means a leg is not yet marked.
