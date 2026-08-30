# Architecture Overview -- Zecpath ATS

## High-Level Flow

```
Raw Resume/JD Files (data/)
        |
        v
[Day 5] Text Extraction & Cleaning
        |
        v
[Day 8] Section Classification  <----  [Day 6] JD Parsing (parallel path)
        |                                       |
        v                                       v
[Day 9] Skill Extraction               (feeds into scoring)
[Day 10] Experience Parsing
[Day 11] Education Parsing
        |
        v
[Day 12] Semantic Matching (resume <-> JD)
        |
        v
[Day 13] ATS Scoring Engine (weighted, explainable)
        |
        v
[Day 14] Ranking & Shortlisting
        |
        v
[Day 15] Fairness & Bias Check (runs alongside scoring)
        |
        v
[Day 16] API Layer (exposes all of the above to Backend/Frontend)
```


## Design Principles (carried from Day 2)
- REST for synchronous operations (scoring), Queue+Webhook for
  asynchronous ones (extraction/parsing) -- see ATS_API_SPECIFICATION.md.
- Every record carries the Day 7 metadata standard (candidate_id, job_id,
  model_version, timestamp, stage, status) for traceability.
- Every scoring decision is explainable (Day 13) -- no black-box outputs.

## Module Dependency Map
- `parsers/` depends only on `utils/logger.py`.
- `ats_engine/` depends on `parsers/` outputs (skills, experience, education,
  semantic matches) plus its own scoring/ranking/fairness logic.
- `tests/` mirrors both, one test file per module.


