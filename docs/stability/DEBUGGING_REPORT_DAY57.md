# Debugging and Stabilization Report -- Day 57

## Method
1. Reproduce each problem on the existing code (ats_engine/run_bug_repro.py).
2. Fix the cause with the smallest change.
3. Add a test so the problem cannot return (tests/test_day57_stability.py).
4. Check the whole system with edge cases and random bad input (ats_engine/run_stability_check.py).

## Bugs found and fixed
| ID | Area | Symptom before | Cause | Fix |
|---|---|---|---|---|
| B1 | Scoring | An HR interview with no answers was scored 0.0 and counted as a real zero | The stage used the scorer's "no data" result as a score | Stage returns no score (None) |
| B2 | Scoring | Screening with no answers crashed (division by zero) | Average of an empty list | Stage returns no score |
| B3 | Scoring | Technical interview with no answers crashed (KeyError). The "no data" result also showed 0.0 and lacked keys | Incomplete result for the empty case | Full result with technical_score None. Stage returns no score |
| B4 | Scoring | Missing round scores (None) crashed the aggregator | The code assumed a dictionary | Anything but a dictionary counts as no scores |
| B5 | Conversation | Transcript cleanup crashed on a number | .strip() on a non-text value | Value converted to text first |
| B6 | Scoring | An unknown question type or level caused a KeyError | No validation | A clear ValueError. The technical stage skips and counts such questions |
| B7 | Governance | Audit log crashed when a detail held a date | Hash and file writer needed plain JSON values | Unknown values converted to text |
| B8 | Governance | A malformed consent record crashed the access check | Assumed a dictionary | Malformed consent counts as no consent |
| B9 | Governance | An access check with no user crashed | Assumed a user record | Denied as "no verified user" and logged |
| B10 | Governance | One bad date stopped the whole retention sweep | No error handling per record | Bad record skipped with a warning. Records with missing fields no longer crash the lists |
| B11 | Data pipeline | A wrong data key crashed the whole run. After the first fix it was silently treated as "no answers" | Lookup happened before error handling. Then the typo was invisible | Unknown keys are recorded as errors. A failed stage sends the candidate to Hold / Review (rule STAGE_ERROR) |
| B12 | Data pipeline | A candidate whose resume failed to upload could be Selected with confidence 0.84 (Day 56 finding) | A failed upload looked like any other missing round | Rule RESUME_FAILED. Hold / Review with the step "ask for a new upload" |
| B13 | Conversation | "I handle this kind of work every day" was treated as a hedge and got a pointless clarification | "kind of" matched as a hedge even as a noun phrase | "kind of" and "sort of" after words like this, that, what, any, every, the, a no longer count |
| A1 | API | Scores of 150 and -20 were accepted and gave an HR component of 1.5 and a score of 88.5 | No bounds on the score fields | Scores must be 0 to 100 |
| A2 | API | Answers of any length, empty IDs and any number of turns were accepted | No size limits | Answer max 5000 characters, IDs 1 to 100 characters, max 200 turns |
| A3 | API | An unexpected error returned plain "Internal Server Error" | No handler for unexpected errors | Same error shape as every other error, no internal details, logged |
| T1 | Test | A Day 56 test expected the failed-resume candidate to be "AI firmer than the human" | The test encoded the bug | Test updated. A new test keeps the "AI firmer" label covered |

## Results
| Measure | Before | After |
|---|---|---|
| Edge cases passed (30) | 11 | 30 |
| Random bad-input failures (300 candidates) | 5 | 0 |
| Day 56 consistency checks | 13 of 13 | 14 of 14 (a new check for failed resumes) |
| Day 56 agreement with the simulated reviewer | 7 of 12 | 8 of 12 |
| New automated tests | 0 | 30 |

## Lessons
1. "No data" must never become a zero. Several defaults were quiet scoring errors.
2. A test can encode a bug (T1). When behaviour changes on purpose, update the test and say why.
3. A first fix can hide a problem (B11). The new test caught it.
4. Pipeline problems are not candidate problems. A failed upload or stage needs a person.

## Final modules changed
| File | Change | Version |
|---|---|---|
| refined_decision_logic.py | RESUME_FAILED and STAGE_ERROR rules | decision_v1.2 |
| e2e_stages.py | Stages return no score when there is nothing to score. Technical skips bad questions | Day 57 |
| refined_intent.py | "kind of" and "sort of" as noun phrases | Day 57 |
| transcript_normalizer.py | Accepts non-text input | Day 57 |
| cross_round_aggregation_engine.py | Accepts missing score dictionary | Day 57 |
| technical_scoring_engine.py | Validation, safe empty result, non-text answers | Day 57 |
| governance_controls.py | Safer consent, user, audit and retention handling | Day 57 |
| run_e2e_simulation.py | Unknown data keys recorded as errors, resume status and stage errors passed to the decision, new check | Day 57 |
| hr_api_server.py | Input limits, score bounds, one error shape for unexpected errors | Day 57 |
| run_stability_check.py, run_bug_repro.py | New tools | Day 57 |

## Not fixed (still open)
1. ATS keyword inflation (Day 56 finding 2). The real ATS was not changed.
2. The stand-in HR estimates are generous. The real Day 35 and 36 analysers are not wired in.
3. The rounds-disagree rule on Rejected candidates adds review work. It needs real data.
4. API interviews are stored in memory and lost on restart. There is no authentication.
5. Two writers at the same time can interleave audit log lines. A real deployment needs a proper store.
6. Hedge wording is English only.
7. Human comparison still uses a placeholder reviewer.
8. Items from the Day 55 list: encrypted storage, real login, legal review, penetration test.

## Is the system production-ready?
No. It is more stable. On every input tested it no longer crashes, no longer turns "no data" into a zero, and sends pipeline failures to a person. It is still a pilot on simulated data. The Day 55 list of missing pieces still applies.