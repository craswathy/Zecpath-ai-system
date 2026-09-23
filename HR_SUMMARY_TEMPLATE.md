# HR Interview Structured Summary Template -- Zecpath

## Template Fields

| Field | Source | Description |
|---|---|---|
| candidate_id | -- | Unique candidate identifier |
| overall_hr_score | Day 37 | Final weighted HR interview score (0-100) |
| overall_performance_summary | Day 39 | One-line categorical summary (Strong / Adequate / Below-expectation) |
| strengths | Days 37, 38, 35 | High-scoring components, correct reasoning answers, strong communication |
| weaknesses | Days 37, 38, 35 | Low-scoring components, incorrect reasoning, weak communication |
| cultural_fit_indicators | Days 38, 36 | Collaboration signals from situational judgment, stress/composure signals |
| risk_flags | Days 36, 37 | Contradictions, low score reliability, negative sentiment |
| narrative | Day 39 | Auto-generated natural-language paragraph combining all fields above |

## Design Principle
Every field in this summary traces back to a specific, already-built
pipeline stage -- nothing here is newly invented data. Day 39's role is
purely synthesis: turning six days' worth of structured JSON output
(Days 33, 35, 36, 37, 38) into one readable narrative a recruiter can
act on without opening any of the underlying JSON files themselves.

## Sample Output Location
See data/hr_interview_summaries/ for generated reports (JSON + text format).