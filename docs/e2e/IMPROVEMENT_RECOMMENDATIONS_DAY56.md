# Improvement Recommendations -- Day 56

Based on the end-to-end test of 12 simulated candidates (docs/e2e/E2E_TEST_REPORT.md).
Stand-ins were used for resume parsing, ATS, screening, and the per-answer communication
and confidence estimates, and the human reviewer was an author-written placeholder.
Findings about those parts describe the test, not the real modules.

## Summary of the test
- 12 candidates through every stage: resume, ATS, screening, HR interview, technical interview, machine test, decision.
- 13 of 13 consistency checks passed (weights, points, confidence range, human review, determinism, audit chain, and more).
- AI and the simulated human agreed exactly on 7 of 12. Four disagreements were the AI deferring to a person, and one was the AI being firmer than the human.

## Findings and recommendations
| # | Finding | Evidence | Priority | Recommendation |
|---|---|---|---|---|
| 1 | A failed resume upload is treated like any other missing round, so a candidate can be Selected with no resume | e2e_08: ATS missing, Selected with confidence 0.84. The human would hold and ask again | High | Add a rule RESUME_FAILED: an unreadable resume moves Selected or Rejected to Hold / Review with the step "request a new upload". Show it as a risk in the report. Log it in the audit trail |
| 2 | ATS counts keywords, so a keyword-stuffed resume scores full marks | e2e_05: ATS 100, later rounds average 53.5. e2e_10: ATS 90, later rounds average 55.7 | Medium | Count a skill only when it appears with evidence (a project or a job), cap repeated words, and show "listed, no evidence" in the report |
| 3 | A very low resume score holds back a candidate whose interviews and test are excellent | e2e_06: ATS 0, later rounds about 90. AI Hold, human Selected | Medium | Keep the Hold, but label the reason "resume outlier, interviews strong" and offer a quick-confirm path. Check the real resume parser, because the stand-in found no skills |
| 4 | The rounds-disagree rule sends clearly weak candidates to review | e2e_04: weak everywhere, but resume 0 against HR 66 triggered the rule. Human Rejected | Low | With real data, decide whether the rule should apply to Rejected. It adds recruiter workload |
| 5 | The HR stage gave generous scores in this test | HR 66 for a weak candidate and 99.8 for strong ones. Consistency was fixed at 1.0 because no contradiction detector ran | Medium (test quality) | Wire the real Day 35 and 36 analysers and the contradiction detector into e2e_stages.py, then rerun |
| 6 | HR interview far above technical interview is common | 7 of 12 candidates (a smooth-talker pattern) | Low | Add "HR far above technical" as an information line in the report. The technical round already carries more weight for technical roles |
| 7 | The AI never recommended Rejected in this set | 0 of 12, while the simulated human rejected 3 | Information | Track the share of cases deferred to people. Tune the borderline and spread rules with real labelled data, not with this set |
| 8 | Evidence about AI against human judgment is thin | 12 candidates, one simulated reviewer | High (for evidence) | Use 2 or 3 real reviewers on REVIEW_PACKET.txt. Compare AI with each person, and people with each other, as the baseline. Scale to 50 or more candidates |
| 9 | Speed is not a bottleneck in the code tested | About 0.8 ms per candidate for this code | Information | Time the real ATS and model loading. Keep models loaded in a long-running service. Batch logging mode is already in place |
| 10 | Regressions can slip in between runs | The consistency checks only run when someone runs them | Medium | Run the end-to-end simulation after every change (it is in pytest) and keep a dated copy of the results to compare |

## Suggested order
1. Do first: 1 (resume failure rule), 5 (wire real analysers), 8 (real reviewers).
2. Next: 2 (evidence check in ATS), 3 (resume outlier label), 4 (review of the spread rule).
3. Later: 6, 7, 9, 10.

## Limits of this test
- Simulated candidates, stand-in stages, placeholder reviewer, 12 cases. No statistics should be drawn from it.
- It shows that the pipeline runs end to end, that its internal checks hold, and where the logic needs a closer look.