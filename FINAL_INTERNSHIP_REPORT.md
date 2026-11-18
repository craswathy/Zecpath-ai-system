# Final Internship Report -- C R Aswathy

**Organisation:** Zecser Business LLP (remote, Kochi)
**Role:** Data Science Engineer Intern
**Project:** Zecpath AI hiring platform, AI engine
**Period:** Aug 2026 to Nov 2026 (70-day plan)

## 1. Objective
Build the AI engine for an AI hiring platform: structure resumes and job
descriptions, score and rank candidates explainably, run screening and
interview scoring, and combine all rounds into one recommendation for a human
reviewer.

## 2. What was delivered
| Area | Delivered |
|---|---|
| Resume and job parsing | Extraction, section detection, skills, experience, education, schemas |
| ATS | Weighted score, semantic matching, ranking, fairness checks |
| Screening and HR interview | Question bank, speech-to-text, answer scoring, communication and confidence scoring, follow-ups |
| Technical round and decision | Technical scoring, cross-round aggregation, decision engine with safety rules |
| Governance | Consent, access control, audit log, retention rules |
| APIs | ATS, HR and decision endpoints, JSON schemas for five AI services |
| Operations | Logging, metrics, alert rules, performance tuning, scalability plan |
| Quality | 331 automated tests, edge-case and random-input tests, release validator |
| Documentation | Handbook, architecture, onboarding, index, roadmap |
| Demo | 8 fictional candidates, demo script, presentation deck |

## 3. Results
| Measure | Result | Verify with |
|---|---|---|
| Automated tests | 331 of 331 passing | pytest tests/ |
| Modules | 151 | MODULE_INDEX.md |
| Matching speed-up | 9.3x, 10 resumes by 6 jobs | data/performance_day60.json |
| Edge cases | 30 of 30 passing | python -m ats_engine.run_stability_check |
| Release validator problems | 0 | python -m ats_engine.release_validator |

## 4. Challenges and how I handled them
- A strong score could hide a weak round. I added component and round floors and tested them.
- A bug fix hid the real error, and my own test caught it.
- Missing data. I redistribute weight and never invent a value.
- Limited data. I kept thresholds explainable and reported limits plainly.

## 5. Limitations
Tested on small simulated data. Accuracy on real hiring data is unmeasured.
Screening and interviews are simulated text. No deployed database, queue or
authentication. ATS keyword inflation is not fixed.

## 6. Next steps
See AI_ROADMAP.md: validate on real data, harden PDF and skill handling,
deploy, then extend to more languages and real calls.

## 7. Learning
During this internship, I gained hands-on experience designing modular Python pipelines, integrating pretrained NLP models (sentence-transformers, Whisper, VADER), building FastAPI endpoints, and writing comprehensive pytest suites. More importantly, I learned that responsible AI in hiring requires explainable scoring, strict handling of missing or unreadable inputs, fairness checks, and keeping final decisions with human reviewers. If I were to repeat the project, I would prioritise gathering anonymised, recruiter-labelled evaluation data earlier to benchmark rule-based thresholds against real hiring outcomes.

## 8. Acknowledgements
I sincerely thank my mentor and the entire team at Zecser Business LLP for their guidance, structured feedback, and support throughout this 70-day internship.