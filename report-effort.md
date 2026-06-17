| _ | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| **Standard: 60 problems (<1 h human effort)** | | | | | |
| Resolved (out of 60) | 48 | 48 | 51 | 52 | **53** |
| Resolved % | 80% | 80% | 85% | 87% | **88%** |
| Total cost | $8.73 | $15.30 | $21.00 | $54.91 | $124.02 |
| $ / resolved | **$0.18** | $0.32 | $0.41 | $1.06 | $2.34 |
| Steps | 560 | 746 | 887 | 1,453 | 2,103 |
| Output tokens | 150k | 281k | 400k | 996k | 2.25M |
| Thinking (output) | 61k | 152k | ❔ | 666k | 1.62M |
| Input tokens | 4.2M | 8.5M | 12.1M | 38.6M | 93.5M |
| - non-cached | 1.1k | 1.5k | 1.8k | 2.9k | 4.2k |
| - cache read | 3.7M | 7.8M | 11.2M | 36.7M | 89.9M |
| - cache write | 498k | 700k | 862k | 1.86M | 3.67M |
| Wall-clock | 0.7 h | 2.2 h | 2.1 h | 3.9 h | 8.0 h |
| **Hard: 45 problems (1+ h human effort)** | | | | | |
| Resolved (out of 45) | 30 | 28 | **32** | 31 | 30 |
| Resolved % | 67% | 62% | **71%** | 69% | 67% |
| Total cost | $22.84 | $30.34 | $33.97 | $80.88 | $203.65 |
| $ / resolved | **$0.76** | $1.08 | $1.06 | $2.61 | $6.79 |
| Steps | 1,002 | 1,090 | 1,217 | 1,801 | 2,643 |
| Output tokens | 373k | 542k | 578k | 1.34M | 3.30M |
| Thinking (output) | 160k | 281k | ❔ | 848k | 2.47M |
| Input tokens | 16.9M | 20.5M | 24.7M | 66.2M | 185.7M |
| - non-cached | 2.0k | 2.2k | 2.4k | 3.6k | 5.3k |
| - cache read | 16.0M | 19.3M | 23.4M | 63.7M | 180.8M |
| - cache write | 884k | 1.14M | 1.25M | 2.49M | 4.93M |
| Wall-clock | 1.6 h | 2.2 h | 2.3 h | 5.0 h | 11.8 h |
| **Combined: 105 problems** | | | | | |
| Resolved (out of 105) | 78 | 76 | **83** | 83 | 83 |
| Resolved % | 74% | 72% | **79%** | 79% | 79% |
| Total cost | $31.57 | $45.64 | $54.97 | $135.79 | $327.67 |
| $ / resolved | **$0.40** | $0.60 | $0.66 | $1.64 | $3.95 |
| Steps | 1,562 | 1,836 | 2,104 | 3,254 | 4,746 |
| Output tokens | 522k | 822k | 978k | 2.33M | 5.54M |
| Thinking (output) | 221k | 433k | ❔ | 1.51M | 4.10M |
| Input tokens | 21.1M | 28.9M | 36.7M | 104.8M | 279.2M |
| - non-cached | 3.1k | 3.7k | 4.2k | 6.5k | 9.5k |
| - cache read | 19.7M | 27.1M | 34.6M | 100.4M | 270.6M |
| - cache write | 1.38M | 1.84M | 2.11M | 4.36M | 8.60M |
| Wall-clock | 2.3 h | 4.4 h | 4.4 h | 8.9 h | 19.7 h |

**Note:**

- Claude Opus 4.8 at five effort levels on SWE-bench Verified

**Caveats:**

- High's thinking wasn't captured when I ran it initially
- Capped at 250 steps / $25 per attempt
- Wall-clock is total API time, also affected by my machine's load
