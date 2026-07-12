| SWE-bench Multilingual | fable-5 | opus-4-8 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|
| ***Rust* — 7 repos (43 events)** | | | | |
| **Results** | | | | |
| Resolved | 7 | 7 | 7 | — |
| Resolved % | 16% | 16% | 16% | — |
| Total cost | $7.53 | 🥈 $4.06 | 🥉 $4.45 | 🥇 **$3.76** |
| $/resolved | 🥉 $1.08 | 🥇 **$0.58** | 🥈 $0.64 | — |
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
| $/instance | $0.75 | $0.41 | $0.44 | $0.42 |
| Empty patches | 0 | 0 | 0 | 2 |
| Steps | 167 | 187 | 278 | 905 |
| Output tokens | 61k | 66k | 94k | 193k |
| Thinking (output) | 28k | 30k | 50k | 0k |
| Input tokens | 2.63M | 2.93M | 6.86M | 23.28M |
| - non-cached | 0k | 0k | 1k | 88k |
| - cache read | 2.47M | 2.77M | 6.58M | 22.85M |
| - cache write | 160k | 163k | 282k | 340k |
| Wall-clock | 0.4 h | 0.3 h | 0.4 h | 0.9 h |
| **fmtlib/fmt — *C++* (11 events)** | | | | |
| **Results** | | | | |
| Resolved | 🥉 3 | 🥈 4 | 🥇 **6** | — |
| Resolved % | 🥉 27% | 🥈 36% | 🥇 **55%** | — |
| Total cost | $9.80 | 🥈 $7.60 | 🥉 $8.71 | 🥇 **$4.69** |
| $/resolved | 🥉 $3.27 | 🥈 $1.90 | 🥇 **$1.45** | — |
| **Stats** | | | | |
| Bug fixed (F2P clean) | 4 | 4 | 6 | — |
| Near misses (fixed, P2P broke) | 1 | 0 | 0 | — |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 | — |
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
| Resolved | — | — | — | — |
| Resolved % | — | — | — | — |
| Total cost | $0.00 | $0.00 | $0.00 | $0.00 |
| $/resolved | — | — | — | — |
| **Stats** | | | | |
| Bug fixed (F2P clean) | — | — | — | — |
| Near misses (fixed, P2P broke) | — | — | — | — |
| Build-breakers (>20% P2P broke) | — | — | — | — |
| $/instance | — | — | — | — |
| Empty patches | 0 | 0 | 0 | 0 |
| Steps | 0 | 0 | 0 | 0 |
| Output tokens | 0k | 0k | 0k | 0k |
| Thinking (output) | 0k | 0k | 0k | 0k |
| Input tokens | 0k | 0k | 0k | 0k |
| - non-cached | 0k | 0k | 0k | 0k |
| - cache read | 0k | 0k | 0k | 0k |
| - cache write | 0k | 0k | 0k | 0k |
| Wall-clock | 0.0 h | 0.0 h | 0.0 h | 0.0 h |
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
| Resolved | 🥉 10/21 | 🥈 11/21 | 🥇 **13/21** | — |
| Resolved % | 🥉 48% | 🥈 52% | 🥇 **62%** | — |
| Total cost | 🥉 $17.33 | 🥇 **$11.66** | 🥈 $13.16 | — |
| $/resolved | 🥉 $1.73 | 🥈 $1.06 | 🥇 **$1.01** | — |
| **Medal tally** | | | | |
| **Resolved** | | | | |
| 🥇 gold | 0 | 0 | 2 | 0 |
| 🥈 silver | 0 | 2 | 0 | 0 |
| 🥉 bronze | 2 | 0 | 0 | 0 |
| **Total cost** | | | | |
| 🥇 gold | 0 | 0 | 0 | 3 |
| 🥈 silver | 0 | 2 | 1 | 0 |
| 🥉 bronze | 0 | 1 | 2 | 0 |
| **$/resolved** | | | | |
| 🥇 gold | 0 | 1 | 2 | 0 |
| 🥈 silver | 0 | 2 | 1 | 0 |
| 🥉 bronze | 3 | 0 | 0 | 0 |

Verdicts from the swebench judges; — means a contender has not entered or is unjudged.
