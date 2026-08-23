# Stability Improvements -- Zecpath ATS

## Changes Made
1. **Graceful page-level failure in PDF extraction** -- previously, one
   corrupted page could raise an exception and abort extracting the entire
   resume. Now each page is wrapped individually; failures are logged and
   skipped, and extraction continues with whatever pages succeeded.
2. **Missing-data handling in ATS scoring (carried over from Day 13)** --
   already redistributes weight rather than crashing when a component is
   unavailable; confirmed this holds under noisier real-world input during
   Day 18 testing.
3. **Memory release utility** -- added explicit garbage collection after
   large batch operations (semantic matching across many resume-JD pairs),
   reducing risk of memory buildup during long-running batch jobs.

## Not Yet Addressed
- OCR fallback for scanned/image-based PDFs (tracked in Day 17's
  improvement backlog) -- still returns empty text rather than attempting
  OCR extraction.
- Column-aware text extraction -- still a known limitation, tracked for
  future work rather than fixed in this pass.