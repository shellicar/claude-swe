| SWE-bench Verified | Claude Fable 5 | Claude Fable 5 (2 Jul) | Claude Opus 4.8 | Claude Opus 4.7 | Claude Opus 4.6 | Claude Sonnet 4.6 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|---|---|---|---|
| **Standard — 60 problems (<1 h human effort)** | | | | | | | | |
| **Results** | | | | | | | | |
| Resolved | 🥈 55 | 🥇 **57** | 🥉 51 | 50 | 46 | 44 | 🥉 51 | 38 |
| Resolved % | 🥈 92% | 🥇 **95%** | 🥉 85% | 83% | 77% | 73% | 🥉 85% | 63% |
| Total cost | $30.68 | $28.51 | 🥉 $21.00 | $25.90 | $24.48 | $35.58 | 🥇 **$17.34** | 🥈 $17.90 |
| $/resolved | $0.56 | $0.50 | 🥈 $0.41 | $0.52 | $0.53 | $0.81 | 🥇 **$0.34** | 🥉 $0.47 |
| **Stats** | | | | | | | | |
| Steps | 657 | 647 | 887 | 1,179 | 1,236 | 1,953 | 1,383 | 3,663 |
| Output tokens | 309k | 282k | 400k | 409k | 327k | 954k | 388k | 980k |
| Thinking (output) | — | 135k | — | 190k | 127k | — | 186k | — |
| Input tokens | 6.80M | 6.21M | 12.08M | 19.69M | 17.01M | 49.81M | 23.67M | 94.68M |
| — non-cached | 1k | 1k | 2k | 1k | 669k | 2k | 3k | 656k |
| — cache read | 6.07M | 5.50M | 11.21M | 18.68M | 15.51M | 47.98M | 22.39M | 91.46M |
| — cache write | 731k | 711k | 862k | 1.01M | 831k | 1.83M | 1.28M | 2.56M |
| Wall-clock (12-way parallel) | 2.0 h | 1.6 h | 2.1 h | 1.7 h | 1.8 h | 4.9 h | 2.0 h | 3.5 h |
| **Hard — 45 problems (1+ h human effort)** | | | | | | | | |
| **Results** | | | | | | | | |
| Resolved | 🥈 39 | 🥇 **40** | 32 | 25 | 18 | 21 | 🥉 34 | 13 |
| Resolved % | 🥈 87% | 🥇 **89%** | 71% | 56% | 40% | 47% | 🥉 76% | 29% |
| Total cost | $52.85 | $54.79 | 🥈 $33.97 | $51.92 | $52.14 | $105.45 | 🥉 $39.63 | 🥇 **$21.41** |
| $/resolved | 🥉 $1.36 | $1.37 | 🥇 **$1.06** | $2.08 | $2.90 | $5.02 | 🥈 $1.17 | $1.65 |
| **Stats** | | | | | | | | |
| Steps | 743 | 796 | 1,217 | 1,718 | 1,799 | 3,025 | 2,206 | 3,832 |
| Output tokens | 536k | 525k | 578k | 703k | 676k | 2.06M | 725k | 1.05M |
| Thinking (output) | — | 283k | — | 346k | 299k | — | 368k | — |
| Input tokens | 12.84M | 15.20M | 24.67M | 50.51M | 50.22M | 197.31M | 71.86M | 126.48M |
| — non-cached | 1k | 2k | 2k | 2k | 309k | 3k | 4k | 497k |
| — cache read | 11.69M | 14.04M | 23.42M | 48.92M | 48.39M | 192.88M | 69.78M | 123.32M |
| — cache write | 1.15M | 1.16M | 1.25M | 1.58M | 1.52M | 4.43M | 2.08M | 2.66M |
| Wall-clock (12-way parallel) | 2.4 h | 2.5 h | 2.3 h | 2.9 h | 3.7 h | 10.4 h | 3.5 h | 3.5 h |
| **Combined — 105 problems** | | | | | | | | |
| **Results** | | | | | | | | |
| Resolved | 🥈 94 | 🥇 **97** | 83 | 75 | 64 | 65 | 🥉 85 | 51 |
| Resolved % | 🥈 90% | 🥇 **92%** | 79% | 71% | 61% | 62% | 🥉 81% | 49% |
| Total cost | $83.53 | $83.30 | 🥈 $54.97 | $77.82 | $76.61 | $141.03 | 🥉 $56.97 | 🥇 **$39.32** |
| $/resolved | $0.89 | $0.86 | 🥇 **$0.66** | $1.04 | $1.20 | $2.17 | 🥈 $0.67 | 🥉 $0.77 |
| **Stats** | | | | | | | | |
| Steps | 1,400 | 1,443 | 2,104 | 2,897 | 3,035 | 4,978 | 3,589 | 7,495 |
| Output tokens | 845k | 807k | 978k | 1.11M | 1.00M | 3.02M | 1.11M | 2.03M |
| Thinking (output) | — | 418k | — | 536k | 426k | — | 554k | — |
| Input tokens | 19.64M | 21.41M | 36.75M | 70.20M | 67.23M | 247.13M | 95.53M | 221.15M |
| — non-cached | 3k | 3k | 4k | 3k | 979k | 5k | 7k | 1.15M |
| — cache read | 17.76M | 19.54M | 34.64M | 67.60M | 63.90M | 240.86M | 92.16M | 214.78M |
| — cache write | 1.88M | 1.87M | 2.11M | 2.60M | 2.35M | 6.26M | 3.36M | 5.22M |
| Wall-clock (12-way parallel) | 4.4 h | 4.1 h | 4.4 h | 4.7 h | 5.6 h | 15.2 h | 5.5 h | 7.0 h |

Verdicts from the pinned swebench marker. Full caveats in report.md.
