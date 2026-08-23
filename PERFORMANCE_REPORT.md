# Performance Report -- Zecpath ATS

## Method
Benchmarked using ats_engine/performance_benchmark.py across the 10-resume
test set, measuring wall-clock time for text extraction and semantic
model operations before and after optimization.

## Baseline (Before Optimization)
- Text extraction: [X] files, total [X]s, avg [X]s/file
- Semantic model load (one-time): [X]s
- Semantic model inference (per comparison): [X]s

## After Optimization
- Text extraction: [X]s avg/file (per-page error handling added, doesn't
  slow down clean files, prevents total failure on files with one bad page)
- Semantic model: batch encoding added (embed_batch) -- reduces per-item
  overhead when scoring many resumes against many JDs at once (Day 12's
  60-comparison run benefits directly from this)

## Optimizations Applied
1. **Batch embedding** -- encode multiple texts in one model call instead
   of one-by-one, reducing repeated overhead.
2. **Per-page extraction error handling** -- a single corrupted/unreadable
   page no longer fails the entire resume; only that page is skipped and logged.
3. **Explicit garbage collection utility** -- added for batch-processing
   scenarios where tensor objects from the semantic model could otherwise
   accumulate in memory across a large run.

## Known Remaining Bottlenecks
- Semantic model first-call load time (~[X]s) is a fixed one-time cost per
  process start -- could be mitigated in production by keeping a long-running
  API server (Day 16) with the model pre-loaded, rather than reloading per script run.
- Column-layout PDF parsing (documented in Day 12/17) remains a correctness
  issue, not just a performance one -- noisy resume handling improved
  error resilience but does not yet fix the underlying column-jumbling.