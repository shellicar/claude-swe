| SWE-bench Multilingual | fable-5 | opus-4-8 | sonnet-5 |
|---|---|---|---|
| **rust (tokio-rs/tokio, 9 instances)** | | | |
| Instances | 9 | 9 | 9 |
| Resolved | 7 | 7 | 7 |
| Resolved % | 78% | 78% | 78% |
| Bug fixed (F2P clean) | 8 | 8 | 8 |
| Near misses (fixed, P2P broke) | 1 | 1 | 1 |
| Build-breakers (>20% P2P broke) | 0 | 0 | 0 |
| Total cost | $4.99 | $2.90 | $2.90 |
| $/resolved | $0.71 | $0.41 | $0.41 |
| $/instance | $0.55 | $0.32 | $0.32 |
| Empty patches | 0 | 0 | 0 |
| Steps | 110 | 138 | 197 |
| Output tokens | 48k | 51k | 70k |
| Thinking (output) | 22k | 22k | 36k |
| Input tokens | 1.20M | 1.77M | 3.68M |
| - non-cached | 0k | 0k | 0k |
| - cache read | 1.08M | 1.64M | 3.46M |
| - cache write | 122k | 131k | 215k |
| Wall-clock | 0.3 h | 0.2 h | 0.3 h |
| **cpp (fmtlib/fmt, 11 instances)** | | | |
| Instances | 11 | 11 | 11 |
| Resolved | 3 | 4 | 6 |
| Resolved % | 27% | 36% | 55% |
| Bug fixed (F2P clean) | 4 | 4 | 6 |
| Near misses (fixed, P2P broke) | 1 | 0 | 0 |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 |
| Total cost | $9.80 | $7.60 | $8.71 |
| $/resolved | $3.27 | $1.90 | $1.45 |
| $/instance | $0.89 | $0.69 | $0.79 |
| Empty patches | 0 | 0 | 0 |
| Steps | 187 | 274 | 437 |
| Output tokens | 94k | 130k | 125k |
| Thinking (output) | 50k | 77k | 63k |
| Input tokens | 2.57M | 5.62M | 18.04M |
| - non-cached | 0k | 1k | 1k |
| - cache read | 2.36M | 5.35M | 17.63M |
| - cache write | 217k | 269k | 411k |
| Wall-clock | 0.5 h | 0.6 h | 0.5 h |
| **cpp variation (verify + 900s, same 11)** | | | |
| Instances | 11 | 11 | 11 |
| Resolved | 4 | 5 | 6 |
| Resolved % | 36% | 45% | 55% |
| Bug fixed (F2P clean) | 4 | 5 | 6 |
| Near misses (fixed, P2P broke) | 0 | 0 | 0 |
| Build-breakers (>20% P2P broke) | 5 | 5 | 5 |
| Total cost | $14.53 | $10.82 | $6.07 |
| $/resolved | $3.63 | $2.16 | $1.01 |
| $/instance | $1.32 | $0.98 | $0.55 |
| Empty patches | 0 | 0 | 0 |
| Steps | 272 | 361 | 436 |
| Output tokens | 128k | 149k | 114k |
| Thinking (output) | 69k | 86k | 48k |
| Input tokens | 4.97M | 10.47M | 10.12M |
| - non-cached | 1k | 1k | 1k |
| - cache read | 4.69M | 10.15M | 9.74M |
| - cache write | 277k | 323k | 385k |
| Wall-clock | 0.7 h | 0.7 h | 0.5 h |

Verdicts from the swebench marker; — means a leg is not yet marked or never ran.
