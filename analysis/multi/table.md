| Multi-SWE-bench | fable-5 | opus-4-8 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|
| ***C++* control (20 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **14** | 🥈 13 | 🥉 12 | 9 |
| Resolved % | 🥇 **70%** | 🥈 65% | 🥉 60% | 45% |
| Total cost | $30.07 | 🥉 $17.32 | 🥈 $14.91 | 🥇 **$7.64** |
| $/resolved | $2.15 | 🥉 $1.33 | 🥈 $1.24 | 🥇 **$0.85** |
| — Catch2 | 1/2 | 1/2 | 1/2 | 1/2 |
| — fmt | 0/5 | 0/5 | 0/5 | 0/5 |
| — json | 10/10 | 9/10 | 8/10 | 6/10 |
| — simdjson | 3/3 | 3/3 | 3/3 | 2/3 |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 0 | 2 |
| $/instance | $1.50 | $0.87 | $0.75 | $0.38 |
| Steps | 503 | 635 | 910 | 1,724 |
| Output tokens | 244k | 260k | 244k | 342k |
| Thinking (output) | 126k | 109k | 91k | 0k |
| Input tokens | 10.82M | 14.32M | 27.74M | 46.70M |
| - non-cached | 1k | 1k | 2k | 289k |
| - cache read | 10.20M | 13.68M | 26.89M | 45.55M |
| - cache write | 613k | 637k | 848k | 866k |
| Wall-clock | 1.4 h | 1.0 h | 0.9 h | 1.7 h |
| ***Rust* control (20 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **14** | 🥉 11 | 🥈 13 | 🥉 11 |
| Resolved % | 🥇 **70%** | 🥉 55% | 🥈 65% | 🥉 55% |
| Total cost | $17.86 | 🥉 $10.64 | 🥈 $9.46 | 🥇 **$5.49** |
| $/resolved | $1.28 | 🥉 $0.97 | 🥈 $0.73 | 🥇 **$0.50** |
| — bat | 0/1 | 0/1 | 0/1 | 0/1 |
| — clap | 11/12 | 8/12 | 9/12 | 7/12 |
| — fd | 1/1 | 1/1 | 1/1 | 1/1 |
| — nushell | 1/2 | 1/2 | 2/2 | 1/2 |
| — rayon | 1/1 | 1/1 | 1/1 | 1/1 |
| — tokio | 0/3 | 0/3 | 0/3 | 1/3 |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 0 | 0 |
| $/instance | $0.89 | $0.53 | $0.47 | $0.27 |
| Steps | 425 | 466 | 715 | 1,257 |
| Output tokens | 133k | 164k | 159k | 260k |
| Thinking (output) | 64k | 101k | 85k | 0k |
| Input tokens | 5.87M | 7.92M | 16.27M | 30.69M |
| - non-cached | 1k | 1k | 1k | 264k |
| - cache read | 5.41M | 7.47M | 15.63M | 29.65M |
| - cache write | 463k | 449k | 634k | 769k |
| Wall-clock | 1.1 h | 0.7 h | 0.7 h | 1.2 h |
| ***C++* variation (verify + 900s — exhibition) (20 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **14** | 🥈 13 | 🥉 12 | — |
| Resolved % | 🥇 **70%** | 🥈 65% | 🥉 60% | — |
| Total cost | $47.71 | 🥉 $32.21 | 🥈 $20.61 | 🥇 **$0.00** |
| $/resolved | 🥉 $3.41 | 🥈 $2.48 | 🥇 **$1.72** | — |
| — Catch2 | 1/2 | 1/2 | 1/2 | — |
| — fmt | 0/5 | 0/5 | 0/5 | — |
| — json | 10/10 | 9/10 | 8/10 | — |
| — simdjson | 3/3 | 3/3 | 3/3 | — |
| **Stats** | | | | |
| Empty patches | 2 | 2 | 2 | 0 |
| $/instance | $2.39 | $1.61 | $1.03 | — |
| Steps | 967 | 1,152 | 1,356 | 0 |
| Output tokens | 284k | 328k | 266k | 0k |
| Thinking (output) | 124k | 122k | 100k | — |
| Input tokens | 25.22M | 39.20M | 44.26M | 0k |
| - non-cached | 2k | 2k | 3k | 0k |
| - cache read | 24.50M | 38.43M | 43.29M | 0k |
| - cache write | 719k | 765k | 966k | 0k |
| Wall-clock | 2.0 h | 1.5 h | 1.3 h | 0.0 h |
| **tokio stack — *Rust* (org tokio-rs) (20 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 10 | 🥇 **11** | 🥇 **11** | 🥉 9 |
| Resolved % | 🥈 50% | 🥇 **55%** | 🥇 **55%** | 🥉 45% |
| Total cost | 🥉 $21.64 | $22.37 | 🥈 $10.69 | 🥇 **$7.78** |
| $/resolved | $2.16 | 🥉 $2.03 | 🥈 $0.97 | 🥇 **$0.86** |
| — tokio | 4/10 | 4/10 | 4/10 | 4/10 |
| — tracing | 6/10 | 7/10 | 7/10 | 5/10 |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 0 | 0 |
| $/instance | $1.08 | $1.12 | $0.53 | $0.39 |
| Steps | 451 | 671 | 641 | 1,473 |
| Output tokens | 166k | 308k | 168k | 327k |
| Thinking (output) | 78k | 179k | 69k | 0k |
| Input tokens | 7.74M | 18.97M | 19.23M | 47.76M |
| - non-cached | 1k | 1k | 1k | 254k |
| - cache read | 7.25M | 18.07M | 18.54M | 46.51M |
| - cache write | 486k | 901k | 695k | 994k |
| Wall-clock | 1.1 h | 1.8 h | 0.7 h | 1.4 h |
| **TOTAL — controls (variation excluded)** | | | | |
| Resolved | 🥇 **38/60** | 🥉 35/60 | 🥈 36/60 | 29/60 |
| Resolved % | 🥇 **63%** | 🥉 58% | 🥈 60% | 48% |
| Total cost | $69.57 | 🥉 $50.33 | 🥈 $35.07 | 🥇 **$20.91** |
| $/resolved | $1.83 | 🥉 $1.44 | 🥈 $0.97 | 🥇 **$0.72** |
| **Medal tally — counted in events** | | | | |
| **Resolved** | | | | |
| 🥇 gold | 3 | 1 | 1 | 0 |
| 🥈 silver | 1 | 2 | 1 | 0 |
| 🥉 bronze | 0 | 1 | 2 | 2 |
| **Total cost** | | | | |
| 🥇 gold | 0 | 0 | 0 | 4 |
| 🥈 silver | 0 | 0 | 4 | 0 |
| 🥉 bronze | 1 | 3 | 0 | 0 |
| **$/resolved** | | | | |
| 🥇 gold | 0 | 0 | 1 | 3 |
| 🥈 silver | 0 | 1 | 3 | 0 |
| 🥉 bronze | 1 | 3 | 0 | 0 |

Verdicts from the Multi-SWE judging panel; — means a contender has not entered or is unjudged.
