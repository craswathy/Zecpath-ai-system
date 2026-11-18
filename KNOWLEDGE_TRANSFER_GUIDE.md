# Knowledge Transfer Guide -- Zecpath AI Engine

For the person taking over this code. Read in this order, about 90 minutes.

## 1. Orientation (15 minutes)
README.md, then ZECPATH_AI_TECHNICAL_HANDBOOK.md, then
SYSTEM_ARCHITECTURE_DOCUMENTATION.md. MODULE_INDEX.md lists every module.

## 2. Code walkthrough order
| Step | Files | What to understand |
|---|---|---|
| 1. Reading resumes | parsers/resume_reader.py, text_cleaner.py | PDF and DOCX to clean text |
| 2. Structuring | parsers/section_classifier.py, skill_extractor.py, experience_parser.py, education_parser.py, jd_parser.py | Text to structured profile and job requirement |
| 3. Matching | parsers/semantic_matcher.py, ats_engine/perf_optimizations.py | Embeddings, cosine similarity, caching and batching |
| 4. ATS score | ats_engine/ats_scorer.py, scoring_config.py, candidate_ranker.py | Weighted score, zones, ranking |
| 5. Fairness | ats_engine/fairness_normalizer.py, bias_checker.py | Masking and bias checks |
| 6. Screening | ats_engine/screening_scorer.py, screening_aggregator.py, conversation_state_machine.py, call_error_handler.py | Answer scoring, call flow, safeguards |
| 7. HR interview | ats_engine/hr_interview_scorer.py, communication_scorer.py, confidence_analyzer.py, follow_up_trigger_detector.py | Interview scoring and follow-ups |
| 8. Technical | ats_engine/technical_scoring_engine.py | Technical answer scoring |
| 9. Combining rounds | ats_engine/unified_scorer.py, hiring_fit_calculator.py, cross_round_aggregation_engine.py | Cross-round fit |
| 10. Decision | ats_engine/decision_engine.py, refined_decision_logic.py, polished_decision_service.py | Selected, Hold or Rejected, safety rules, validated API logic |
| 11. Governance | ats_engine/governance_controls.py | Consent, access, audit log, retention |
| 12. Operations | ats_engine/observability.py, monitoring_metrics.py, polished_api.py | Logs, metrics, alerts, API |

## 3. Things that will surprise you
- Two decision styles exist: Strong, Moderate, Weak (hiring_fit_calculator) and Selected, Hold, Rejected (decision_engine). The second is the later design.
- Some duplicate-looking modules exist (hiring_fit_calculator_v2, unified_candidate_object and unified_candidate_score_object). Check which one the code imports before editing.
- The end-to-end test in run_e2e_simulation uses simplified stand-ins for some stages (see ats_engine/e2e_stages.py). The demo in run_demo_simulation uses the real modules.
- "No data" is None, never 0. A failed stage or unreadable resume always goes to a person.
- Run modules with python -m. Test files start with sys.path.append(".").

## 4. How to run and verify
    pytest tests/
    python -m ats_engine.release_validator
    python -m ats_engine.run_stability_check
    python -m ats_engine.run_demo_simulation

## 5. How to make a safe change
1. Run pytest first. Everything should pass.
2. Change one thing. Add a test for it.
3. Run pytest, release_validator and run_stability_check again.
4. Do not change a threshold before checking the real score spread.

## 6. Handover status
| Item | Status |
|---|---|
| Code, tests, documentation | Delivered |
| Demo dataset and demo scripts | Delivered |
| Release validation and bug fix report | Delivered |
| AI roadmap | Delivered, see AI_ROADMAP.md |
| Validation on real recruiter data | Not done |
| Database, queue, authentication, deployment | Not done |
| ATS keyword inflation | Known, not fixed |
| Real telephony, video analysis, multilingual | Not built |

## 7. Where to get help
TROUBLESHOOTING_NOTES.md, then IMPROVEMENT_BACKLOG.md, then the author:
C R Aswathy, GitHub craswathy.