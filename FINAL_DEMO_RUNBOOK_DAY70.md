# Final Demo Runbook -- Day 70

Total: about 15 minutes. Rehearse once with a stopwatch. Run every command once
beforehand so the AI model is already loaded.

## Say this first
"Everything today uses fictional candidates. ATS, interview scoring and the
decision are computed by the real code. The screening score is simulated and
the interview answers are typed text, because no real calls are connected."

## Timeline
| Minutes | Part | What to do |
|---|---|---|
| 0-1 | Opening | Problem, and the principle: AI recommends, people decide |
| 1-5 | Explain | Architecture, AI models, scoring logic (notes below) |
| 5-11 | Live demo | The five stages below |
| 11-13 | Handover | What is delivered, what is open |
| 13-15 | Questions | Use the backup slide |

## Live demo: Resume to Decision
| Stage | Run | Show and say |
|---|---|---|
| Resume | `type demo_dataset_day63\resumes\cand_priya.txt` | A plain text resume. The system will parse it into skills, experience, education |
| ATS, Screening, Interview, Decision | `python -m ats_engine.run_demo_simulation` | One row per candidate: ATS score, screening score (simulated), HR interview score, hiring fit and category. Point out one match and one mismatch, and explain the mismatch honestly |
| Recruiter report | `type data\polished_reports\cand_ravi.txt` | Reasons in plain words, a suggested next step, "a person makes the final decision" |
| Decision API | `uvicorn ats_engine.polished_api:app` then open `/docs` | A valid request, then a 422 error, then an empty request that returns Needs Manual Review |
| Monitoring | `python -m ats_engine.monitoring_metrics` | Metrics and a fired alert |

Optional, if time allows (technical round and cross-round decision):
`python -m ats_engine.run_cross_round_demo` and `python -m ats_engine.run_decision_demo`.
Say: the end-to-end test used simplified stand-ins for some stages.

## Explain: architecture
Backend and gateway, five AI services (resume parsing, ATS scoring, screening,
interview, decision), and storage. Slow work is asynchronous with a queue and
webhooks. Fast work is synchronous. The queue, database and authentication are
designed in AI_INTEGRATION_DOCUMENT.md and not deployed.

## Explain: AI models (be exact)
| Part | Technique | Honest note |
|---|---|---|
| Semantic matching | Pretrained sentence-transformer, cosine similarity | Pretrained, not trained by me. Model name is in parsers/semantic_matcher.py |
| Speech-to-text | OpenAI Whisper | Pretrained. Demo uses text, not audio |
| Sentiment | VADER | Lexicon based, not a trained model |
| Everything else | Rules and weighted formulas | Chosen for explainability, no labelled data existed |

## Explain: scoring logic
- ATS score: weighted skills, experience, education and semantic match. Weights depend on role type. A missing part has its weight shared among the others.
- Interview score: relevance, communication, confidence and consistency. A weak part downgrades the band.
- Hiring fit (demo): weighted blend of ATS, screening and interview. Strong Fit from 75, Moderate from 55. A round below 40 caps the category at Moderate.
- Decision engine (later version, decision_v1.2): Selected, Hold or Rejected with confidence, and extra rules that send disagreeing rounds, a weak key round, a failed resume or a failed stage to Hold for a person.
- Know which one you are showing. The demo prints Strong, Moderate and Weak. The decision engine prints Selected, Hold and Rejected.

## If something fails
Switch to your saved screenshot and say "let me show the saved result". Never
edit code live. A mismatch between a candidate and the intended outcome is a
finding to explain, not a bug to hide.

## Close
"The system is a tested, documented prototype. Next steps are real-data
validation, then deployment. The roadmap is in AI_ROADMAP.md."