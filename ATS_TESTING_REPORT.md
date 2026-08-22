# ATS System Testing Report -- Zecpath

## Scope
Tested the full pipeline (Days 5-16) across the 10-resume, 6-JD sample set,
covering both technical and non-technical roles, and a mix of experience
levels (see TEST_SET_CATEGORIZATION.md).

## Method
1. Categorized test set by domain, tech/non-tech, and seniority.
2. Ran the full pipeline end to end for every resume-JD pair.
3. Manually reviewed AI decisions against human judgment for each case
   (see MANUAL_REVIEW_COMPARISON.md).
4. Computed precision/recall from the manual review (see testing_metrics.py output).

## Results Summary
- Precision: [fill in from testing_metrics.py output]
- Recall: [fill in from testing_metrics.py output]
- Mismatch cases: [fill in count and brief description of each]

## Key Findings
- [Tech vs non-tech]: [note whether accuracy differed noticeably between categories]
- [Fresher vs senior]: [note whether accuracy differed by experience level]
- [Known bug]: One resume's semantic score was affected by a column-layout
  PDF parsing issue (see Day 12), which likely lowered its scores across
  all downstream metrics until the source file was replaced.

## See Also
- Full improvement backlog: IMPROVEMENT_BACKLOG.md
- Raw score data: data/ats_scores/
- Manual review detail: MANUAL_REVIEW_COMPARISON.md