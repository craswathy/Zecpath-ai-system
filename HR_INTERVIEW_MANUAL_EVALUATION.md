# HR Interview Manual Evaluation -- Zecpath

## Method

Simulated 4 distinct candidate profiles (confident, hesitant, inexperienced,
overqualified) through the full HR scoring and summary pipeline (Days
37-39), then manually compared the AI's score and narrative against what
a human interviewer would reasonably conclude for each profile.

## Comparison

| Candidate Type | AI Score | AI Narrative Verdict | Manual Expectation | Match? |
|---|---:|---|---|---|
| confident_candidate | 95.5 | Strong overall HR interview performance | Strong performance | Yes |
| hesitant_candidate | 75.8 | Strong overall HR interview performance | Adequate, confidence coaching needed | No |
| inexperienced_candidate | 64.9 | Adequate HR interview performance with some areas for improvement | Below-expectation on role-specific depth | No |
| overqualified_candidate | 86.6 | Strong overall HR interview performance, contradiction flagged | Strong but flagged for contradiction review | Yes |

## Scoring Inconsistencies Found

**hesitant_candidate** was categorized "Strong" (75.8 crosses the 75-point
threshold) despite a confidence component of only 0.49 -- clearly the
weakest score of any component across all four candidates. High relevance
(0.82) and perfect consistency (1.0) carried the weighted average over the
"Strong" line, masking a real, specific weakness a human interviewer would
have flagged immediately. The narrative text itself correctly says "Areas
to probe further include weak confidence" -- but the headline verdict
("Strong overall") contradicts that detail sitting one line below it.

**inexperienced_candidate** was categorized "Adequate" (64.9) despite a
relevance component of only 0.47 -- the lowest relevance score of any
candidate, reflecting off-topic and vague answers. A human interviewer
assessing role-specific depth would likely call this "Below-expectation,"
not "Adequate," since relevance is arguably the most job-relevant
component and was clearly failing here.

**Root cause**: `summarize_overall_hr_performance()` (Day 39) buckets purely
on the final weighted score (`>=75` Strong, `>=50` Adequate,
`<50` Below-expectation) without checking whether any single critical
component (relevance or confidence) is disproportionately weak. A
candidate can have one seriously weak component fully offset by strong
scores elsewhere and still get bucketed into a more favorable category
than the underlying detail supports.