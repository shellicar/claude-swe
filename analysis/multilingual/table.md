| SWE-bench Multilingual | fable-5 | opus-4-8 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|
| ***Rust* — 7 repos (43 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **36** | 🥈 33 | 🥈 33 | 🥉 21 |
| Resolved % | 🥇 **84%** | 🥈 77% | 🥈 77% | 🥉 49% |
| Total cost | $47.62 | $28.22 | $28.36 | **$14.21** |
| $/resolved | $1.32 | $0.86 | $0.86 | **$0.68** |
| — axum | 7/7 | 7/7 | 6/7 | 3/7 |
| — bat | 6/8 | 5/8 | 5/8 | 2/8 |
| — coreutils | 3/5 | 2/5 | 2/5 | 2/5 |
| — nushell | 5/5 | 5/5 | 5/5 | 5/5 |
| — ripgrep | 2/2 | 2/2 | 2/2 | 2/2 |
| — ruff | 6/7 | 5/7 | 6/7 | 2/7 |
| — tokio | 7/9 | 7/9 | 7/9 | 5/9 |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 40 | 38 | 37 | 26 |
| Near misses (fixed, P2P broke) | 4 | 5 | 4 | 5 |
| Build-breakers (>20% P2P broke) | 1 | 2 | 1 | 6 |
| $/instance | $1.11 | $0.66 | $0.66 | $0.33 |
| Empty patches | 0 | 0 | 0 | 2 |
| Steps | 1,101 | 1,215 | 1,860 | 3,235 |
| Output tokens | 375k | 403k | 483k | 687k |
| Thinking (output) | 171k | 202k | 216k | 0k |
| Input tokens | 17.97M | 24.59M | 51.77M | 82.97M |
| - non-cached | 2k | 2k | 4k | 492k |
| - cache read | 17.02M | 23.58M | 50.15M | 80.71M |
| - cache write | 948k | 1.02M | 1.61M | 1.77M |
| Wall-clock | 2.3 h | 2.0 h | 2.0 h | 3.0 h |
| **fmtlib/fmt — *C++* (11 events)** | | | | |
| **Results** | | | | |
| Resolved | 3 | 🥉 4 | 🥇 **6** | 🥈 5 |
| Resolved % | 27% | 🥉 36% | 🥇 **55%** | 🥈 45% |
| Total cost | $9.80 | $7.60 | $8.71 | **$4.69** |
| $/resolved | $3.27 | $1.90 | $1.45 | **$0.94** |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 4 | 4 | 6 | 5 |
| Near misses (fixed, P2P broke) | 1 | 0 | 0 | 0 |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 | 5 |
| $/instance | $0.89 | $0.69 | $0.79 | $0.43 |
| Empty patches | 0 | 0 | 0 | 0 |
| Steps | 187 | 274 | 437 | 893 |
| Output tokens | 94k | 130k | 125k | 214k |
| Thinking (output) | 50k | 77k | 63k | 0k |
| Input tokens | 2.57M | 5.62M | 18.04M | 28.15M |
| - non-cached | 0k | 1k | 1k | 147k |
| - cache read | 2.36M | 5.35M | 17.63M | 27.42M |
| - cache write | 217k | 269k | 411k | 583k |
| Wall-clock | 0.5 h | 0.6 h | 0.5 h | 0.9 h |
| ***Go* — 5 repos (42 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥇 **37** | 🥉 30 | 🥈 31 | 25 |
| Resolved % | 🥇 **88%** | 🥉 71% | 🥈 74% | 60% |
| Total cost | $49.14 | $33.22 | $30.77 | **$19.21** |
| $/resolved | $1.33 | $1.11 | $0.99 | **$0.77** |
| — caddy | 12/14 | 10/14 | 8/14 | 8/14 |
| — gin | 8/8 | 5/8 | 5/8 | 4/8 |
| — hugo | 7/7 | 6/7 | 7/7 | 5/7 |
| — prometheus | 6/8 | 6/8 | 7/8 | 5/8 |
| — terraform | 4/5 | 3/5 | 4/5 | 3/5 |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 38 | 30 | 32 | 26 |
| Near misses (fixed, P2P broke) | 1 | 0 | 1 | 1 |
| Build-breakers (>20% P2P broke) | 1 | 2 | 1 | 1 |
| $/instance | $1.17 | $0.79 | $0.73 | $0.46 |
| Empty patches | 0 | 0 | 0 | 1 |
| Steps | 1,027 | 1,169 | 1,909 | 3,513 |
| Output tokens | 367k | 429k | 472k | 777k |
| Thinking (output) | 152k | 227k | 202k | 0k |
| Input tokens | 19.46M | 32.86M | 61.65M | 119.01M |
| - non-cached | 2k | 2k | 4k | 356k |
| - cache read | 18.47M | 31.80M | 60.15M | 115.96M |
| - cache write | 983k | 1.05M | 1.50M | 2.70M |
| Wall-clock | 2.2 h | 2.1 h | 1.9 h | 8.2 h |
| ***C++* variation (verify + 900s, same 11 — exhibition)** | | | | |
| **Results** | | | | |
| Resolved | 🥉 4 | 🥈 5 | 🥇 **6** | — |
| Resolved % | 🥉 36% | 🥈 45% | 🥇 **55%** | — |
| Total cost | $14.53 | $10.82 | $6.07 | **$0.00** |
| $/resolved | $3.63 | $2.16 | **$1.01** | — |
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
| Resolved | 🥇 **76/96** | 🥉 67/96 | 🥈 70/96 | 51/96 |
| Resolved % | 🥇 **79%** | 🥉 70% | 🥈 73% | 53% |
| Total cost | $106.56 | $69.04 | $67.84 | **$38.10** |
| $/resolved | $1.40 | $1.03 | $0.97 | **$0.75** |
| **Medal tally — counted in events** | | | | |
| 🥇 gold | 2 | 0 | 2 | 0 |
| 🥈 silver | 0 | 2 | 2 | 1 |
| 🥉 bronze | 1 | 2 | 0 | 1 |

Verdicts from the swebench judges; — means a contender has not entered or is unjudged.
