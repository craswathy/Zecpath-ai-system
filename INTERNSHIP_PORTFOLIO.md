# Internship Portfolio -- C R Aswathy

**Role:** Data Science Engineer Intern, Zecser Business LLP (remote, Kochi)
**Duration:** Aug 2026 to Nov 2026, 70-day plan
**Project:** Zecpath AI hiring platform, AI engine
**Repository:** github.com/craswathy (Zecpath AI repository)
**Background:** M.Sc. Statistics, Christ College (Autonomous), 2026

## 1. Summary
I built the AI engine for a hiring platform in Python. It parses resumes and job
descriptions, scores and ranks candidates with an explainable method, scores
AI screening and interview answers, and combines all rounds into one
recommendation that a human reviews. I tested it, documented it and prepared a
demonstration.

## 2. What I built, by phase
| Days | Phase | Outcome |
|---|---|---|
| 1-20 | Resume and job parsing, ATS scoring | Structured profiles, weighted explainable score, ranking, fairness check, API stub |
| 21-32 | Eligibility and AI screening | Question bank, speech-to-text, answer scoring, state machine, edge cases |
| 33-45 | HR interview AI | Follow-ups, communication and confidence scoring, summaries, ethics review |
| 46-57 | Technical round, aggregation, decision | Technical scoring, cross-round aggregation, decision engine, governance, stability testing |
| 58-62 | Proposal, integration, scaling, monitoring, handbook | Roadmap, API schemas, performance work, observability plan, technical handbook |
| 63-69 | Demo, review, polish, release, submission | Demo dataset, mock demo, bug fixing, release validation, final package |

## 3. Evidence
| Measure | Result | Where to verify |
|---|---|---|
| Automated tests | [ ] passing of [ ] | `pytest tests/` |
| Modules | [ ] | `MODULE_INDEX.md` |
| Matching speed-up from caching and batching | [ ]x on 10 resumes by 6 jobs | `data/performance_day60.json` |
| Edge cases handled | [ ] of [ ] | `python -m ats_engine.run_stability_check` |
| Release validator problems | [ ] | `python -m ats_engine.release_validator` |
| Demo candidates | 8 fictional | `demo_dataset_day63/` |

## 4. Skills used
- Python, pytest, FastAPI, Git and GitHub
- NLP: sentence-transformer embeddings, cosine similarity, VADER sentiment, Whisper
- Statistics in practice: weighted scoring, threshold tuning, distribution and bias checks, validation design
- Engineering: API design, JSON schemas, logging, performance tuning, documentation

## 5. Challenges and what I learned
- **A strong score hid a weak round.** I added component and round floors and checked the fix with automated tests, not by eye.
- **A bug fix that hid the real error.** My own test caught it, so a failed stage now always goes to a person.
- **Optimisation.** The speed-up came from removing repeated encoding, not from a better model, and I checked the scores were unchanged.
- **Small data.** I learned to report limits plainly, because results on a few cases show behaviour, not accuracy.

## 6. Honest limits
Tested on small simulated data, with no real calls, database or deployment, and
accuracy on real hiring data is unmeasured. See `AI_ROADMAP.md`.

## 7. Key documents
`README.md`, `ZECPATH_AI_TECHNICAL_HANDBOOK.md`, `DOCUMENTATION_INDEX.md`,
`AI_ROADMAP.md`, `BUG_FIX_REPORT_DAY68.md`, `FINAL_SYSTEM_VALIDATION_DAY68.md`.

## 8. Reflection
[Two or three sentences in your own words: what you learned about building
AI systems, what you would do differently, and where you want to grow.]