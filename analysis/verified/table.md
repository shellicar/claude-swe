| SWE-bench Verified — latest-generation division | Claude Fable 5 | Claude Opus 4.8 | Claude Sonnet 5 | Claude Haiku 4.5 |
|---|---|---|---|---|
| **Standard — 60 *Python* events (<1 h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **55** | 🥈 51 | 🥈 51 | 🥉 38 |
| Resolved % | 🥇 **92%** | 🥈 85% | 🥈 85% | 🥉 63% |
| Total cost | $30.68 | 🥉 $21.00 | 🥇 **$17.34** | 🥈 $17.90 |
| $/resolved | $0.56 | 🥈 $0.41 | 🥇 **$0.34** | 🥉 $0.47 |
| **Stats** | | | | |
| Steps | 657 | 887 | 1,383 | 3,663 |
| Output tokens | 309k | 400k | 388k | 980k |
| Thinking (output) | — | — | 186k | — |
| Input tokens | 6.80M | 12.08M | 23.67M | 94.68M |
| — non-cached | 1k | 2k | 3k | 656k |
| — cache read | 6.07M | 11.21M | 22.39M | 91.46M |
| — cache write | 731k | 862k | 1.28M | 2.56M |
| Wall-clock (12-way parallel) | 2.0 h | 2.1 h | 2.0 h | 3.5 h |
| **Hard — 45 *Python* events (1+ h human effort)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **39** | 🥉 32 | 🥈 34 | 13 |
| Resolved % | 🥇 **87%** | 🥉 71% | 🥈 76% | 29% |
| Total cost | $52.85 | 🥈 $33.97 | 🥉 $39.63 | 🥇 **$21.41** |
| $/resolved | 🥉 $1.36 | 🥇 **$1.06** | 🥈 $1.17 | $1.65 |
| **Stats** | | | | |
| Steps | 743 | 1,217 | 2,206 | 3,832 |
| Output tokens | 536k | 578k | 725k | 1.05M |
| Thinking (output) | — | — | 368k | — |
| Input tokens | 12.84M | 24.67M | 71.86M | 126.48M |
| — non-cached | 1k | 2k | 4k | 497k |
| — cache read | 11.69M | 23.42M | 69.78M | 123.32M |
| — cache write | 1.15M | 1.25M | 2.08M | 2.66M |
| Wall-clock (12-way parallel) | 2.4 h | 2.3 h | 3.5 h | 3.5 h |
| **Combined — 105 *Python* events** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **94** | 🥉 83 | 🥈 85 | 51 |
| Resolved % | 🥇 **90%** | 🥉 79% | 🥈 81% | 49% |
| Total cost | $83.53 | 🥈 $54.97 | 🥉 $56.97 | 🥇 **$39.32** |
| $/resolved | $0.89 | 🥇 **$0.66** | 🥈 $0.67 | 🥉 $0.77 |
| **Stats** | | | | |
| Steps | 1,400 | 2,104 | 3,589 | 7,495 |
| Output tokens | 845k | 978k | 1.11M | 2.03M |
| Thinking (output) | — | — | 554k | — |
| Input tokens | 19.64M | 36.75M | 95.53M | 221.15M |
| — non-cached | 3k | 4k | 7k | 1.15M |
| — cache read | 17.76M | 34.64M | 92.16M | 214.78M |
| — cache write | 1.88M | 2.11M | 3.36M | 5.22M |
| Wall-clock (12-way parallel) | 4.4 h | 4.4 h | 5.5 h | 7.0 h |
| **Medal tally — counted in events** | | | | |
| 🥇 gold | 3 | 0 | 0 | 0 |
| 🥈 silver | 0 | 1 | 3 | 0 |
| 🥉 bronze | 0 | 2 | 0 | 1 |

Verdicts from the pinned swebench judges. Full caveats in report.md.
