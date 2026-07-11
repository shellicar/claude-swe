| claude-swe — all experiments | fable-5 | opus-4-8 | opus-4-7 | opus-4-6 | sonnet-4-6 | sonnet-5 | haiku-4-5 |
|---|---|---|---|---|---|---|---|
| **SWE-bench Verified** | | | | | | | |
| standard (60) | 55 (92%) | 51 (85%) | 50 (83%) | 46 (77%) | 44 (73%) | 51 (85%) | 38 (63%) |
| — cost/resolved | $0.56 | $0.41 | $0.52 | $0.53 | $0.81 | $0.34 | $0.47 |
| hard (45) | 39 (87%) | 32 (71%) | 25 (56%) | 18 (40%) | 21 (47%) | 34 (76%) | 13 (29%) |
| — cost/resolved | $1.36 | $1.06 | $2.08 | $2.90 | $5.02 | $1.17 | $1.65 |
| **SWE-bench Pro** | | | | | | | |
| tutanota ts (20) | 17 (85%) | 11 (55%) | — | — | — | 14 (70%) | — |
| — cost/resolved | $2.54 | $2.14 | — | — | — | $1.80 | — |
| NodeBB js (44) | 42 (95%) | 35 (80%) | — | — | — | 32 (73%) | — |
| — cost/resolved | $1.87 | $1.10 | — | — | — | $1.47 | — |
| **SWE-bench Multilingual** | | | | | | | |
| rust: tokio (9) | 7 (78%) | 7 (78%) | — | — | — | 7 (78%) | — |
| — cost/resolved | $0.71 | $0.41 | — | — | — | $0.41 | — |
| cpp: fmt (11) | 3 (27%) | 4 (36%) | — | — | — | 6 (55%) | — |
| — cost/resolved | $3.27 | $1.90 | — | — | — | $1.45 | — |
| cpp variation (11) | 4 (36%) | 5 (45%) | — | — | — | 6 (55%) | — |
| — cost/resolved | $3.63 | $2.16 | — | — | — | $1.01 | — |
| **Multi-SWE-bench** | | | | | | | |
| cpp control (20) | 14 (70%) | 13 (65%) | — | — | — | 12 (60%) | — |
| — cost/resolved | $2.15 | $1.33 | — | — | — | $1.24 | — |
| rust control (20) | 14 (70%) | 11 (55%) | — | — | — | 13 (65%) | — |
| — cost/resolved | $1.28 | $0.97 | — | — | — | $0.73 | — |
| cpp variation (20) | 14 (70%) | 13 (65%) | — | — | — | 12 (60%) | — |
| — cost/resolved | $3.41 | $2.48 | — | — | — | $1.72 | — |
| **TOTAL — all controls (variations excluded)** | | | | | | | |
| resolved / attempted | 191/229 (83%) | 164/229 (72%) | 75/105 (71%) | 64/105 (61%) | 65/105 (62%) | 169/229 (74%) | 51/105 (49%) |
| — cost/resolved | $1.40 | $0.95 | $1.04 | $1.20 | $2.17 | $0.98 | $0.77 |

Resolved n (%) and cost per resolved, per selection. — = not run or not yet marked. Details per dataset in analysis/<dataset>/table.md.
