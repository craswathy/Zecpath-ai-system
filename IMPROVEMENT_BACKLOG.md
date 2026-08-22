# Improvement Backlog -- Zecpath ATS

## High Priority
1. **Column-layout PDF parsing** -- Day 5/12 found that multi-column resume
   layouts cause pdfplumber to jumble text, breaking section detection
   downstream. Needs column-aware extraction (e.g. pdfplumber's
   layout-detection mode or a dedicated library like `pdfminer.six` with
   layout analysis).
2. **Threshold calibration needs more data** -- current 70/40 thresholds
   (Day 14) were tuned against only 10 resumes x 6 JDs. Needs validation
   against a much larger, more diverse dataset before production use.

## Medium Priority
3. **Skill dictionary coverage** -- Day 9's skill dictionary is manually
   curated and will miss skills not yet added. Needs periodic review as
   more real resumes are processed.
4. **Semantic similarity ceiling** -- Day 12 embeddings rarely score above
   0.7-0.8 even for strong matches (a general-purpose model, not
   resume-specific). Consider fine-tuning or a resume-specific model later.

## Low Priority / Future
5. **OCR support for scanned resumes** -- Day 5 found one resume with no
   text layer (scanned image). Needs pytesseract/OCR integration to handle.
6. **Group-level bias monitoring dashboard** -- Day 15's bias_checker exists
   as a function but has no dashboard/alerting; would need Recruiter
   Dashboard integration (Phase 9 in the PRD) to be actionable day-to-day.

## Notes
This backlog was compiled from real issues found during Day 12 debugging
(column-layout bug) and Day 14 threshold tuning (zero-shortlist issue),
not hypothetical concerns -- both are documented with reproduction steps
in their respective day's work.