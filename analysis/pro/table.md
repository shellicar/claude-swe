| SWE-bench Pro | fable-5 | opus-4-8 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|
| **tutanota — *TypeScript* (all 20 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **17** | 🥉 11 | 🥈 14 | 7 |
| Resolved % | 🥇 **85%** | 🥉 55% | 🥈 70% | 35% |
| Total cost | $43.19 | ⚪ $23.57 | 🟤 $25.22 | 🟡 **$8.54** |
| $/resolved | $2.54 | 🟤 $2.14 | ⚪ $1.80 | 🟡 **$1.22** |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 1 | 2 |
| $/instance | $2.16 | $1.18 | $1.26 | $0.43 |
| Steps | 645 | 694 | 1,146 | 1,715 |
| Output tokens | 273k | 313k | 369k | 365k |
| Thinking (output) | 131k | 163k | 188k | 0k |
| Input tokens | 19.70M | 22.05M | 51.62M | 54.00M |
| - non-cached | 1k | 1k | 2k | 181k |
| - cache read | 18.84M | 21.23M | 50.40M | 52.81M |
| - cache write | 855k | 819k | 1.21M | 1.01M |
| Wall-clock | 1.7 h | 1.4 h | 1.4 h | 1.9 h |
| **NodeBB — *JavaScript* (all 44 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **42** | 🥈 35 | 🥉 32 | 18 |
| Resolved % | 🥇 **95%** | 🥈 80% | 🥉 73% | 41% |
| Total cost | $78.57 | ⚪ $38.59 | 🟤 $47.18 | 🟡 **$14.08** |
| $/resolved | $1.87 | ⚪ $1.10 | 🟤 $1.47 | 🟡 **$0.78** |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 1 | 0 |
| $/instance | $1.79 | $0.88 | $1.07 | $0.32 |
| Steps | 1,187 | 1,336 | 2,487 | 2,849 |
| Output tokens | 578k | 521k | 654k | 645k |
| Thinking (output) | 307k | 262k | 303k | 0k |
| Input tokens | 31.54M | 34.27M | 97.59M | 81.15M |
| - non-cached | 2k | 3k | 5k | 453k |
| - cache read | 29.96M | 32.80M | 95.25M | 78.67M |
| - cache write | 1.58M | 1.47M | 2.34M | 2.03M |
| Wall-clock | 3.3 h | 2.3 h | 2.8 h | 2.7 h |
| **element-web — *JavaScript* (20 of 56 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 19 | 🥉 17 | 🥇 **20** | 3 |
| Resolved % | 🥈 95% | 🥉 85% | 🥇 **100%** | 15% |
| Total cost | $93.77 | ⚪ $25.95 | 🟤 $50.86 | 🟡 **$7.81** |
| $/resolved | $4.94 | 🟡 **$1.53** | ⚪ $2.54 | 🟤 $2.60 |
| **Stats** | | | | |
| Empty patches | 1 | 0 | 0 | 0 |
| $/instance | $4.69 | $1.30 | $2.54 | $0.39 |
| Steps | 756 | 750 | 1,319 | 1,382 |
| Output tokens | 305k | 330k | 361k | 394k |
| Thinking (output) | 149k | 159k | 154k | 0k |
| Input tokens | 26.05M | 25.17M | 71.74M | 44.01M |
| - non-cached | 2k | 2k | 3k | 221k |
| - cache read | 21.49M | 24.28M | 64.81M | 42.71M |
| - cache write | 4.56M | 889k | 6.93M | 1.08M |
| Wall-clock | 8.7 h | 1.4 h | 6.2 h | 1.5 h |
| ***Go* (25 of 280 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥈 22 | 🥉 21 | 🥇 **23** | 13 |
| Resolved % | 🥈 88% | 🥉 84% | 🥇 **92%** | 52% |
| Total cost | $45.84 | 🟤 $30.13 | ⚪ $27.46 | 🟡 **$9.75** |
| $/resolved | $2.08 | 🟤 $1.43 | ⚪ $1.19 | 🟡 **$0.75** |
| **Stats** | | | | |
| Empty patches | 0 | 0 | 0 | 0 |
| $/instance | $1.83 | $1.21 | $1.10 | $0.39 |
| Steps | 730 | 941 | 1,444 | 1,844 |
| Output tokens | 319k | 397k | 404k | 483k |
| Thinking (output) | 167k | 208k | 185k | 0k |
| Input tokens | 19.93M | 29.14M | 56.08M | 56.41M |
| - non-cached | 1k | 2k | 3k | 249k |
| - cache read | 19.06M | 28.16M | 54.76M | 54.89M |
| - cache write | 866k | 977k | 1.32M | 1.28M |
| Wall-clock | 1.8 h | 1.9 h | 1.8 h | 2.0 h |
| **TOTAL — all selections** | | | | |
| Resolved | 🥇 **100/109** | 🥉 84/109 | 🥈 89/109 | 41/109 |
| Resolved % | 🥇 **92%** | 🥉 77% | 🥈 82% | 38% |
| Total cost | $261.36 | ⚪ $118.24 | 🟤 $150.73 | 🟡 **$40.18** |
| $/resolved | $2.61 | ⚪ $1.41 | 🟤 $1.69 | 🟡 **$0.98** |
| **Medal tally — counted in events** | | | | |
| 🥇 gold | 2 | 0 | 2 | 0 |
| 🥈 silver | 2 | 1 | 1 | 0 |
| 🥉 bronze | 0 | 3 | 1 | 0 |

Verdicts from the Scale judging panel; — means a contender has not entered or is unjudged.
