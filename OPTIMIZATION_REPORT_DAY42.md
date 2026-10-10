# HR Interview AI Optimization Report -- Day 42

## Scope
Stability and consistency fixes for the HR interview system (Days 33-41),
driven by problems found in earlier testing (Day 40) and by reviewing the code.

## Fixes

| Area | Problem found | Fix |
|---|---|---|
| False positive | hesitant_candidate (75.8) labelled "Strong" despite confidence 0.49 | Component floor: any component below 0.5 downgrades the band one level |
| False negative/positive | inexperienced_candidate (64.9) labelled "Adequate" despite relevance 0.47 | Same floor, now "Below-expectation" |
| Yes/no extraction | "I know" returned "no"; "not sure" returned "yes" (substring matching) | Whole-word regex, unsure checked first |
| Scoring anomaly | Runner filled missing communication/confidence with a fake 50 | Missing components excluded, weight redistributed |
| Follow-up stability | Empty answers got no clarification; short concrete answers over-probed; no total cap | Empty -> clarification; numbers count as detail; cap of 6 follow-ups per interview |
| Transcript cleanup | Stutters kept, stray commas after fillers, "one" turned into "1" in "one of the projects" | Stutter collapse, punctuation cleanup, number words converted only before units |
| Speed | Fillers removed with one regex pass per filler | Single combined pattern |

## Accuracy Evaluation (4 simulated profiles)

| Profile | Score | Verdict before | Verdict after | Manual expectation |
|---|---|---|---|---|
| confident | 95.5 | Strong | Strong | Strong |
| hesitant | 75.8 | Strong | Adequate | Adequate, confidence coaching |
| inexperienced | 64.9 | Adequate | Below-expectation | Below-expectation |
| overqualified | 86.6 | Strong + contradiction note | Strong + contradiction note | Strong, flagged for review |

Before: 2/4 matched. After: 4/4 matched.

## Performance (microseconds per call, from data/hr_performance_*.json)

| Function | Before | After |
|---|---|---|
| normalize_transcript_text | 24.8 µs | 25.1 µs |
| classify_follow_up_need | 2.2 µs | 2.2 µs |
| compute_hr_interview_score | 9.9 µs | 9.7 µs |

The HR scoring path is not compute-bound; each function runs in microseconds.
Real latency in the full system comes from loading models (Whisper,
sentence-transformers), a one-time cost per process. A long-running server
that loads models once is the meaningful speed improvement, as noted in Day 18.

## Limitations
- The floor (0.5) and bands (75 / 50) were chosen after seeing the same 4
  profiles that exposed the problem, so 4/4 is not independent validation.
- hesitant_candidate's confidence (0.49) sits just under the floor. The fix
  is sensitive to that exact value, and the threshold needs tuning on more data.
- Stutter collapse also merges legitimate repeats such as "had had".
- All testing uses simulated per-turn data, not real interviews.