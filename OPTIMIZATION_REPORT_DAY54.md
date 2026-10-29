# Optimization and Refinement Report -- Day 54

## Scope
Reduce wrong decisions in the Day 51 and Day 52 pipeline and the Day 42 follow-up
logic. Method: build labelled scenarios, measure errors, change the logic, measure
again on a separate holdout set.

## Important limits of this evidence
- All scenarios and answers are simulated and written by the author.
- The reference decisions come from a written rubric (below), not from real
  recruiters or real hiring outcomes.
- The rubric sets the key-round level at 65, and the threshold sweep then selects
  65. That result is partly circular. It shows the method works, not that 65 is right.
- Both sets are small (23 and 12 candidates, 24 and 14 answers). Perfect holdout
  scores are an artifact of small, author-written sets, not proof of accuracy.
- Next step: repeat with real, consented, recruiter-labelled outcomes.

## Reference rubric (simulated recruiter judgement, does not use the engine's weights)
1. Integrity High: Hold / Review.
2. Fewer than 3 rounds scored, or the required round missing: Hold / Review.
3. Selected: mean of scored rounds 75 or above, every round 60 or above, key rounds
   for the role 65 or above.
4. Rejected: mean below 50, or two or more rounds below 45.
5. Otherwise Hold / Review.

## Error definitions
| Term | Meaning |
|---|---|
| False positive | Engine says Selected, rubric says not Selected |
| False negative | Engine says Rejected, rubric says not Rejected |
| Extra review | Engine says Hold / Review, rubric would decide. Workload, not harm |

## Findings
| # | Finding | Cause | Fix |
|---|---|---|---|
| 1 | Selected despite one weak key round (technical interview 45 or machine test 52, others 90 and above) | A weighted average hides one weak round. The floor of 40 only catches rounds below 40 | Rule CRITICAL_ROUND_WEAK: a key round for the role below 65 cannot give Selected |
| 2 | Selected with one very low round (screening 40, others 95) | The floor needs a round below 40, and 40 is not below 40. Disagreement between rounds is not checked | Rule ROUNDS_DISAGREE: best minus worst round of 50 or more moves Selected or Rejected to Hold / Review |
| 3 | Extra review: strong resume with poor interviews, and every round just above 75 | Borderline margin of 3 points in the Day 52 engine | Kept on purpose. Rejecting is the riskiest outcome, and the cost is only recruiter time |
| 4 | Off-topic answers got no follow-up (Day 45 demo) | The Day 42 classifier ignores the off-topic flag | Off-topic answers get a clarification follow-up |
| 5 | Long hedged answers got no follow-up | Depth check only looks at short answers | A hedged answer without a number or evidence phrase gets a clarification. Hedged means one strong hedge, or two hedges of any kind. "I think" alone does not count |

## Results (reference = written rubric)
Decisions:
| Set | Measure | Before | After |
|---|---|---|---|
| Development (23) | Agree with rubric | 17 | 21 |
| Development | False positives | 4 | 0 |
| Development | False negatives | 0 | 0 |
| Development | Extra review | 2 | 2 |
| Holdout (12) | Agree with rubric | 9 | 12 |
| Holdout | False positives | 3 | 0 |
| Holdout | False negatives | 0 | 0 |

Follow-up detection (needs a follow-up?):
| Set | Measure | Before | After |
|---|---|---|---|
| Development (24 answers) | Recall | 0.38 | 1.0 |
| Development | Precision | 1.0 | 1.0 |
| Holdout (14 answers) | Recall | 0.25 | 1.0 |
| Holdout | Precision | 1.0 | 1.0 |

## Threshold choice
Key-round floor (40, 50, 60, 65, 70) and spread limit (30, 40, 50, none) were tested
on the development set only. 9 settings reached the best score (0 errors, 2 extra
review). The least intrusive of those was chosen: the highest spread limit (50), then
the lowest floor (65). The development data cannot separate the settings inside that
group, so these values need real data to confirm. The holdout set was run once, after
the choice.

## Consistency across rounds
The ROUNDS_DISAGREE rule checks whether the best and worst round are 50 points apart.
Such a candidate goes to a recruiter, because one of the rounds is probably unreliable
(for example a resume that overstates skills).

## Processing speed
| Measure | Value |
|---|---|
| Normal logging, microseconds per candidate | 142.6 |
| Batch mode, microseconds per candidate | 29.2 |
| Difference | 79.5 percent faster |

Scoring one candidate takes microseconds. The only avoidable cost found was per-candidate
log writes, and batch mode (a context manager) silences them during bulk scoring. Real
waiting time comes from loading models once per process (Whisper, sentence-transformers,
and the 30 to 76 seconds the semantic matcher test takes in pytest). Moving to a
long-running service that loads models once is the meaningful speed improvement.

## Changes made (no Day 51 or Day 52 file was edited)
| File | Change |
|---|---|
| refined_decision_logic.py | Wraps the Day 52 decision. Two new rules, and batch_mode |
| refined_intent.py | Wraps the Day 42 follow-up classifier. Off-topic and hedge handling |
| run_optimization_analysis.py | Rubric, error counting, threshold sweep, before and after |
| run_speed_benchmark.py | Speed measurement |

## Not changed
- Aptitude and situational scoring (keyword hints), communication scoring, weights
  of the aggregation. No evidence was gathered on them.
- The Day 25 intent classifier. The refinement works at the follow-up level.

## Open items
1. Real recruiter-labelled data to replace the written rubric.
2. A larger holdout set, never used for tuning.
3. Review whether the borderline margin (3 points) should be 2 once real data exists.
4. A speaker-independent test for hedge wording. Hedge patterns here are English phrases
   and can penalise some speaking styles and non-native phrasing. Review before real use.