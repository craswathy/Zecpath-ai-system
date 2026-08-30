# Troubleshooting Notes -- Zecpath ATS

## Issue: Resume scores 0.0 on semantic similarity / missing SKILLS section
**Symptom**: `data/labeled_sections/<resume>_labeled.json` has no "SKILLS"
key, or all content dumped into one section (often "EDUCATION").

**Root cause**: Multi-column PDF layout. pdfplumber extracts text in an
order that interleaves columns, so section headings end up embedded
mid-sentence instead of alone on their own line. Day 8's classifier only
matches headings that appear as a standalone line.

**Fix applied**: Replaced the affected sample resume with a single-column
layout. Not a code fix -- a data workaround.

**Real fix (not yet implemented)**: Column-aware extraction, detecting
text block x-coordinates before reading order is finalized. Tracked in
IMPROVEMENT_BACKLOG.md.

**How to detect this if it happens again**:

type data\labeled_sections<resume>_labeled.json

If "SKILLS" key is missing or nearly all content sits under one section, suspect this issue.

## Issue: Zero candidates shortlisted despite reasonable-looking scores
**Symptom**: `run_ranking` reports `Shortlisted: 0` across all candidates.

**Root cause**: Threshold too strict relative to the score distribution.
The scoring formula requires strong performance across 4 independent
components simultaneously, so scores rarely reach 90+ the way simple
keyword-percentage ATS tools do.

**Fix applied**: Retuned threshold from 75 to 70 (shortlist) and 50 to 40
(review zone), based on actual observed score distribution in
`data/rankings/recruiter_report.txt`, not an arbitrary guess.

**How to detect this if it happens again**: Check
`data/rankings/recruiter_report.txt` for the real score spread before
assuming a threshold is correct.

## Issue: `ModuleNotFoundError: No module named 'parsers'` when running pytest
**Root cause**: Test file missing `sys.path.append(".")` before importing
from `parsers` or `ats_engine`.

**Fix**: Add these two lines at the top of any new test file:
```python

import sys
sys.path.append(".")
```

## Issue: Semantic model re-downloads or reloads slowly on every run
**Root cause**: `sentence-transformers` model isn't cached at the process
level if `get_model()`'s global `_model` variable resets between script runs.

**Fix**: This is expected for one-off script runs (Day 18's benchmark
confirmed model load is a fixed ~[X]s one-time cost). For production, keep
the model loaded in a long-running API process (Day 16) rather than
reloading per script execution.

## Issue: PowerShell won't run `conda activate`
**Root cause**: Windows execution policy blocks PowerShell scripts by default.

**Fix**:

Then close and reopen the terminal.