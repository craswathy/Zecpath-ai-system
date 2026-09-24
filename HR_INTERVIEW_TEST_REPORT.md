# HR Interview System Test Report -- Zecpath

## Scope

End-to-end test of the HR interview scoring and summary pipeline (Days
33-39), using 4 simulated candidate profiles designed to cover distinct
failure/success modes: confident, hesitant, inexperienced, and overqualified.

## Results

- 2/4 candidate profiles matched manual evaluation expectations (confident_candidate, overqualified_candidate).
- 2/4 showed a categorical mismatch between the AI's headline verdict and manual expectation, even though the underlying component scores and narrative detail were themselves accurate (hesitant_candidate, inexperienced_candidate) -- see `HR_INTERVIEW_MANUAL_EVALUATION.md` for full detail.
- All 121 unit tests pass, including the two new Day 40 tests confirming confident scores higher than hesitant, and contradictions correctly lower the consistency component.

## Improvement Recommendations

1. **Add a component-floor check to the overall verdict logic.** `summarize_overall_hr_performance()` should not classify a candidate as "Strong" if any single component score falls below a minimum threshold (e.g. 0.5), regardless of the weighted total. This would have correctly caught hesitant_candidate's weak confidence (0.49) and inexperienced_candidate's weak relevance (0.47) rather than letting strong scores elsewhere mask them.

2. **Weight relevance more conservatively when it's the weakest link.** Relevance is arguably the most job-critical component; a candidate scoring below ~0.5 on relevance specifically should likely cap the overall verdict at "Adequate" at most, never "Strong," even if other components are excellent.

3. **Integrate Day 38's aptitude/situational judgment scores directly into the Day 37 core HR score**, not just the Day 39 narrative summary -- currently aptitude results are referenced only at the summary layer, so a candidate's reasoning ability doesn't influence the numeric hr_interview_score itself.

4. **Contradiction detection worked as designed** -- overqualified_candidate's 1 contradiction correctly lowered its consistency component (0.6 vs. 1.0 for all other candidates) and surfaced in the risk-flags narrative. No change needed here; this should be considered validated.

## Known Limitations

- All 4 profiles used simulated per-turn data, not real voice interviews -- same limitation as Day 30's screening test, consistent across both systems.
- Small sample (4 profiles) -- broader validation would need many more simulated and, ideally, real candidate interviews before the component-floor threshold in Recommendation 1 could be tuned with confidence rather than picked as a reasonable starting guess.