# End-to-End AI Test Report -- Day 56

Simulated candidates only. Stand-ins are used for resume parsing, ATS, screening and the per-answer communication and confidence estimates (see e2e_stages.py).

## 1. Pipeline results

| Candidate | ATS | Screening | HR | Technical | Machine | Fit % | AI decision | Confidence |
|---|---|---|---|---|---|---|---|---|
| e2e_01 | 90.0 | 100.0 | 99.8 | 81.7 | 85 | 89.0 | Selected | 0.91 |
| e2e_02 | 90.0 | 100.0 | 99.8 | 61.1 | 70 | 78.3 | Hold / Review | 0.68 |
| e2e_03 | 52.5 | 60.0 | 88.4 | 61.1 | 58 | 64.2 | Hold / Review | 0.73 |
| e2e_04 | 0.0 | 33.3 | 66.6 | 27.4 | 30 | 32.2 | Hold / Review | 0.75 |
| e2e_05 | 100.0 | 60.0 | 88.4 | 27.4 | 45 | 54.0 | Hold / Review | 0.56 |
| e2e_06 | 0.0 | 100.0 | 99.8 | 81.7 | 88 | 80.9 | Hold / Review | 0.63 |
| e2e_07 | 90.0 | 100.0 | 99.8 | 81.7 | 85 | 89.0 | Hold / Review | 0.71 |
| e2e_08 | - | 100.0 | 99.8 | 81.7 | 85 | 88.9 | Selected | 0.84 |
| e2e_09 | 90.0 | 100.0 | - | - | - | 96.0 | Hold / Review | 0.4 |
| e2e_10 | 90.0 | 60.0 | 99.8 | 27.4 | 40 | 53.2 | Hold / Review | 0.57 |
| e2e_11 | 52.5 | 100.0 | 99.8 | 27.4 | 50 | 58.4 | Hold / Review | 0.6 |
| e2e_12 | 52.5 | 60.0 | 99.8 | 61.1 | 75 | 70.0 | Hold / Review | 0.67 |

## 2. Consistency checks (13 of 13 passed)

| Check | Result | Detail |
|---|---|---|
| Weights add up to 1.0 | PASS | 12 of 12 candidates |
| Round points add up to the hiring fit | PASS | 12 of 12 candidates |
| Confidence is between 0 and 1 | PASS | 12 of 12 candidates |
| Stage scores are 0 to 100 or empty | PASS | 12 of 12 candidates |
| Human review required and still empty | PASS | 12 of 12 candidates |
| Integrity High never leads to Rejected | PASS | 12 of 12 candidates |
| Missing required round gives Hold / Review | PASS | 12 of 12 candidates |
| Preliminary result gives Hold / Review | PASS | 12 of 12 candidates |
| No stage raised an error | PASS | 12 of 12 candidates |
| Every vague or off-topic HR answer got a follow-up | PASS | 0 missed |
| Same input gives the same result (deterministic) | PASS |  |
| Behavioral label never changes a decision | PASS |  |
| Audit log chain is intact | PASS |  |

## 3. Inconsistencies found across stages

| Candidate | Finding | Detail |
|---|---|---|
| e2e_02 | HR interview far above technical interview | HR 99.8, technical 61.1 |
| e2e_03 | HR interview far above technical interview | HR 88.4, technical 61.1 |
| e2e_04 | Stage scores disagree | best 66.6, worst 0.0 |
| e2e_04 | Later rounds far above resume score | ATS 0.0, later rounds average 41.3 |
| e2e_04 | HR interview far above technical interview | HR 66.6, technical 27.4 |
| e2e_05 | Stage scores disagree | best 100.0, worst 27.4 |
| e2e_05 | Resume score far above later rounds | ATS 100.0, later rounds average 53.6 (possible keyword inflation) |
| e2e_05 | HR interview far above technical interview | HR 88.4, technical 27.4 |
| e2e_06 | Stage scores disagree | best 100.0, worst 0.0 |
| e2e_06 | Later rounds far above resume score | ATS 0.0, later rounds average 89.8 |
| e2e_08 | Resume upload failed | Scored without the ATS round. The weight was shared among other rounds. |
| e2e_10 | Stage scores disagree | best 99.8, worst 27.4 |
| e2e_10 | Resume score far above later rounds | ATS 90.0, later rounds average 55.7 (possible keyword inflation) |
| e2e_10 | HR interview far above technical interview | HR 99.8, technical 27.4 |
| e2e_11 | Stage scores disagree | best 100.0, worst 27.4 |
| e2e_11 | HR interview far above technical interview | HR 99.8, technical 27.4 |
| e2e_12 | Stage scores disagree | best 99.8, worst 52.5 |
| e2e_12 | HR interview far above technical interview | HR 99.8, technical 61.1 |

## 4. AI compared with human judgment (source: real reviewers)

Exact agreement: 7 of 12

| Candidate | AI | Human | Result |
|---|---|---|---|
| e2e_01 | Selected | Selected | match |
| e2e_02 | Hold / Review | Hold / Review | match |
| e2e_03 | Hold / Review | Hold / Review | match |
| e2e_04 | Hold / Review | Rejected | AI deferred to a person |
| e2e_05 | Hold / Review | Rejected | AI deferred to a person |
| e2e_06 | Hold / Review | Selected | AI deferred to a person |
| e2e_07 | Hold / Review | Hold / Review | match |
| e2e_08 | Selected | Hold / Review | AI firmer than the human |
| e2e_09 | Hold / Review | Hold / Review | match |
| e2e_10 | Hold / Review | Hold / Review | match |
| e2e_11 | Hold / Review | Rejected | AI deferred to a person |
| e2e_12 | Hold / Review | Hold / Review | match |
