| SWE-bench Multilingual | fable-5 | opus-4-8 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|
| ***Rust* — 7 repos (43 events)** | | | | |
| **Results** | | | | |
| Resolved | 7 | 7 | 7 | — |
| Resolved % | 16% | 16% | 16% | — |
| Total cost | 🥉 $4.99 | 🥇 **$2.90** | 🥇 **$2.90** | 🥈 $3.14 |
| $/resolved | 🥈 $0.71 | 🥇 **$0.41** | 🥇 **$0.41** | — |
| — axum | 0/7 | 0/7 | 0/7 | — |
| — bat | 0/8 | 0/8 | 0/8 | — |
| — coreutils | 0/5 | 0/5 | 0/5 | — |
| — nushell | 0/5 | 0/5 | 0/5 | — |
| — ripgrep | 0/2 | 0/2 | 0/2 | — |
| — ruff | 0/7 | 0/7 | 0/7 | — |
| — tokio | 7/9 | 7/9 | 7/9 | — |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 8 | 8 | 8 | — |
| Near misses (fixed, P2P broke) | 1 | 1 | 1 | — |
| Build-breakers (>20% P2P broke) | 0 | 0 | 0 | — |
| $/instance | $0.55 | $0.32 | $0.32 | $0.52 |
| Empty patches | 0 | 0 | 0 | 2 |
| Steps | 110 | 138 | 197 | 744 |
| Output tokens | 48k | 51k | 70k | 163k |
| Thinking (output) | 22k | 22k | 36k | 0k |
| Input tokens | 1.20M | 1.77M | 3.68M | 20.01M |
| - non-cached | 0k | 0k | 0k | 61k |
| - cache read | 1.08M | 1.64M | 3.46M | 19.71M |
| - cache write | 122k | 131k | 215k | 239k |
| Wall-clock | 0.3 h | 0.2 h | 0.3 h | 0.8 h |
| **fmtlib/fmt — *C++* (11 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥉 3 | 🥈 4 | 🥇 **6** | — |
| Resolved % | 🥉 27% | 🥈 36% | 🥇 **55%** | — |
| Total cost | $9.80 | 🥈 $7.60 | 🥉 $8.71 | 🥇 **$0.00** |
| $/resolved | 🥉 $3.27 | 🥈 $1.90 | 🥇 **$1.45** | — |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 4 | 4 | 6 | — |
| Near misses (fixed, P2P broke) | 1 | 0 | 0 | — |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 | — |
| $/instance | $0.89 | $0.69 | $0.79 | — |
| Empty patches | 0 | 0 | 0 | 0 |
| Steps | 187 | 274 | 437 | 0 |
| Output tokens | 94k | 130k | 125k | 0k |
| Thinking (output) | 50k | 77k | 63k | 0k |
| Input tokens | 2.57M | 5.62M | 18.04M | 0k |
| - non-cached | 0k | 1k | 1k | 0k |
| - cache read | 2.36M | 5.35M | 17.63M | 0k |
| - cache write | 217k | 269k | 411k | 0k |
| Wall-clock | 0.5 h | 0.6 h | 0.5 h | 0.0 h |
| ***C++* variation (verify + 900s, same 11 — exhibition)** | | | | |
| **Results** | | | | |
| Resolved | 🥉 4 | 🥈 5 | 🥇 **6** | — |
| Resolved % | 🥉 36% | 🥈 45% | 🥇 **55%** | — |
| Total cost | $14.53 | 🥉 $10.82 | 🥈 $6.07 | 🥇 **$0.00** |
| $/resolved | 🥉 $3.63 | 🥈 $2.16 | 🥇 **$1.01** | — |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 4 | 5 | 6 | — |
| Near misses (fixed, P2P broke) | 0 | 0 | 0 | — |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 | — |
| $/instance | $1.32 | $0.98 | $0.55 | — |
| Empty patches | 0 | 0 | 0 | 0 |
| Steps | 272 | 361 | 436 | 0 |
| Output tokens | 128k | 149k | 114k | 0k |
| Thinking (output) | 69k | 86k | 48k | — |
| Input tokens | 4.97M | 10.47M | 10.12M | 0k |
| - non-cached | 1k | 1k | 1k | 0k |
| - cache read | 4.69M | 10.15M | 9.74M | 0k |
| - cache write | 277k | 323k | 385k | 0k |
| Wall-clock | 0.7 h | 0.7 h | 0.5 h | 0.0 h |
| **TOTAL — controls (variation excluded)** | | | | |
| Resolved | 🥉 10/20 | 🥈 11/20 | 🥇 **13/20** | — |
| Resolved % | 🥉 50% | 🥈 55% | 🥇 **65%** | — |
| Total cost | 🥉 $14.79 | 🥇 **$10.51** | 🥈 $11.61 | — |
| $/resolved | 🥉 $1.48 | 🥈 $0.96 | 🥇 **$0.89** | — |
| **Medal tally** | | | | |
| **Resolved** | | | | |
| 🥇 gold | 0 | 0 | 2 | 0 |
| 🥈 silver | 0 | 2 | 0 | 0 |
| 🥉 bronze | 2 | 0 | 0 | 0 |
| **Total cost** | | | | |
| 🥇 gold | 0 | 1 | 1 | 2 |
| 🥈 silver | 0 | 1 | 1 | 1 |
| 🥉 bronze | 1 | 1 | 1 | 0 |
| **$/resolved** | | | | |
| 🥇 gold | 0 | 1 | 3 | 0 |
| 🥈 silver | 1 | 2 | 0 | 0 |
| 🥉 bronze | 2 | 0 | 0 | 0 |

Verdicts from the swebench judges; — means a contender has not entered or is unjudged.
