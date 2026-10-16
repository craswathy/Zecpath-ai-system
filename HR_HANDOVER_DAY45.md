# HR Interview AI -- Handover (Day 45)

Status: pilot-ready for internal use with simulated data. Not yet approved
for real candidate data. See the readiness checklist.

## What is delivered
- HR interview module (ats_engine/): question bank, phase state machine,
  follow-up engine, communication and confidence scoring, HR scoring
  engine, recruiter summary, unified hiring-fit score
- REST API (ats_engine/hr_api_server.py)
- Final demo runner (ats_engine/run_final_demo.py) and demo dataset
  (data/demo_dataset/hr_demo_candidates.json)
- Documents: HR_AI_ARCHITECTURE.md, HR_API_SPECIFICATION.md, developer
  handbook, OPTIMIZATION_REPORT_DAY42.md, CHANGELOG.md

## How to run
1. conda activate zecpath-ai
2. pytest tests/
3. python -m ats_engine.run_final_demo
4. uvicorn ats_engine.hr_api_server:app --reload (then open /docs)

## Readiness checklist
| Item | Status |
|---|---|
| Unit and integration tests passing | Done |
| Explanation stored with every score | Done |
| Missing data excluded, never invented | Done |
| Component floor against hidden weak areas | Done |
| Architecture, API and developer documents | Done |
| Follow-up cap and repeat prevention | Done |
| Speech-to-text confidence kept out of the score (Day 43 fix) | [confirm: applied or not applied] |
| Authentication and authorization on the API | Not built |
| Persistent sessions (currently in memory) | Not built |
| Consent check before an interview | Designed, not wired in |
| Retention and human-review controls | Designed, not wired in |
| Encryption of stored data | Not built |
| Thresholds tuned on real interview data | Not done |

## Known limitations
See HR_AI_ARCHITECTURE.md section 8 and HR_API_SPECIFICATION.md section 11.

## Recommended next steps
1. Add authentication and persistent storage to the API.
2. Wire in the consent and human-review controls.
3. Collect real, consented interview data and tune the bands (75 / 50),
   the component floor (0.5) and the reliability minimum (4).
4. Move speech-to-text behind a queue with a webhook (Day 2 pattern).

## Contact for questions
[your name and email]