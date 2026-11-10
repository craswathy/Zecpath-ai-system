# Module Index -- Zecpath AI System

Generated automatically by ats_engine/generate_module_index.py.
Re-run it after adding modules.

## parsers/

| File | Classes | Public functions |
|---|---|---|
| education_dictionary.py | - | - |
| education_parser.py | - | normalize_degree, normalize_field_of_study, extract_graduation_year, extract_education_entries, extract_certifications |
| education_relevance.py | - | score_degree_match, score_field_match, score_education_relevance |
| experience_parser.py | - | parse_date, extract_experience_entries, compute_experience_summary |
| experience_relevance.py | - | score_role_relevance, score_experience_relevance |
| jd_parser.py | - | extract_title, extract_required_skills, extract_experience_years, extract_education, parse_jd |
| resume_reader.py | - | read_pdf, read_docx, extract_resume |
| run_education_parsing.py | - | run |
| run_experience_parsing.py | - | run |
| run_extraction.py | - | run |
| run_jd_parsing.py | - | run |
| run_section_classification.py | - | run |
| run_semantic_matching.py | - | run |
| run_skill_extraction.py | - | run |
| section_classifier.py | - | match_heading, guess_section_by_content, classify_sections |
| semantic_matcher.py | - | get_model, embed_text, embed_batch, semantic_similarity, compare_resume_to_jd |
| skill_dictionary.py | - | normalize_skill |
| skill_extractor.py | - | extract_skills |
| skill_master_dictionary.py | - | - |
| summarize_matches.py | - | - |
| text_cleaner.py | - | clean_text |

## ats_engine/

| File | Classes | Public functions |
|---|---|---|
| adaptive_questioning_framework.py | - | select_follow_up_question, decide_next_action |
| answer_extractor.py | - | extract_skills_mentioned, extract_experience_years, extract_availability, extract_salary_expectation, is_vague_or_missing, build_structured_answer |
| api_schemas.py | - | - |
| api_server.py | ScoreRequest | upload_resume, get_resume_status, score_candidate, get_shortlist |
| aptitude_question_bank.py | - | get_aptitude_questions |
| ats_scorer.py | - | compute_ats_score |
| audio_edge_cases.py | - | detect_poor_audio_quality, detect_language_mixing, handle_missing_answer |
| behavioral_indicators.py | - | build_communication_strength_indicator, build_call_level_report |
| bias_checker.py | - | check_keyword_overdependence, check_score_distribution_bias |
| call_error_handler.py | - | classify_answer_event, should_end_call |
| candidate_ranker.py | - | classify_candidate, rank_candidates, get_shortlist, get_review_zone, get_auto_rejected |
| communication_score_normalizer.py | - | normalize_communication_scores, apply_grammar_leniency_flag |
| communication_scorer.py | - | score_clarity, score_communication |
| confidence_analyzer.py | - | count_hesitation_markers, measure_response_pace, detect_uncertainty, compute_confidence_indicator |
| contradiction_detector.py | - | detect_numeric_contradiction, detect_categorical_contradiction, scan_for_contradictions |
| conversation_question_builder.py | - | build_conversation_questions, validate_mandatory_coverage |
| conversation_state_machine.py | CallState, ConversationStateMachine | - |
| cross_round_aggregation_engine.py | - | get_role_weights, aggregate_rounds, rank_in_pool |
| cross_round_config.py | - | - |
| decision_config.py | - | - |
| decision_engine.py | - | compute_confidence, decide, format_decision_summary |
| e2e_stages.py | - | parse_resume, run_ats, run_screening, estimate_communication, estimate_confidence, run_hr, run_technical |
| eligibility_config.py | - | get_rules |
| eligibility_engine.py | - | check_mandatory_skills, check_experience_range, check_location, evaluate_eligibility |
| fairness_normalizer.py | - | mask_personal_attributes, normalize_resume_text, normalize_score_distribution |
| fallback_questions.py | - | get_fallback_question, get_polite_closing_message |
| fluency_analyzer.py | - | count_filler_words, measure_sentence_continuity, measure_answer_structure |
| follow_up_state_tracker.py | FollowUpStateTracker | - |
| follow_up_trigger_detector.py | - | needs_clarification, needs_deepening, is_confident_response, classify_follow_up_need |
| generate_module_index.py | - | first_line, describe, run |
| governance_controls.py | AuditLog | log_score, log_decision, log_human_decision, is_allowed, has_consent, check_access, find_expired, find_withdrawal_deletions |
| grammar_vocabulary_analyzer.py | - | check_grammar_quality, measure_vocabulary_range |
| hiring_fit_calculator.py | - | classify_hiring_fit |
| hiring_fit_calculator_v2.py | - | classify_hiring_fit |
| hiring_report_generator.py | - | build_sections, collect_strengths, collect_weaknesses, collect_risks, build_report |
| hr_api_server.py | StartInterviewRequest, AnswerRequest, TurnData, ScoreRequest | start_interview, get_interview, submit_answer, score_interview |
| hr_interview_question_bank.py | - | get_questions_for_candidate, get_questions_by_category |
| hr_interview_report_generator.py | - | build_hr_interview_summary, generate_natural_language_narrative, format_hr_summary_as_text |
| hr_interview_scorer.py | - | score_relevance_for_turn, score_consistency_for_candidate, classify_performance_band, compute_hr_interview_score |
| hr_interview_state.py | InterviewPhase, HRInterviewState | - |
| hr_interview_summary_builder.py | - | identify_hr_strengths, identify_hr_weaknesses, identify_cultural_fit_indicators, identify_risk_flags, summarize_overall_hr_performance |
| hr_pipeline_benchmark.py | - | per_call_microseconds, run |
| hr_question_bank.py | - | get_questions_by_category, get_questions_for_role, get_mandatory_questions |
| hr_score_normalizer.py | - | normalize_for_interview_length, normalize_scores_across_candidates |
| hr_score_report_formatter.py | - | format_hr_score_report, export_hr_score_report |
| hr_scoring_config.py | - | get_hr_weights |
| intent_classifier.py | - | classify_intent, is_off_topic |
| logical_reasoning_scorer.py | - | extract_numeric_answer, score_numeric_reasoning, score_verbal_reasoning, score_logical_reasoning |
| memory_utils.py | - | release_memory, process_in_chunks |
| monitoring_metrics.py | - | read_jsonl, compute_metrics, evaluate_alerts |
| observability.py | - | new_request_id, log_api_call, log_model_output, log_error, log_decision, timed_call |
| pause_repetition_detector.py | - | detect_long_pause, detect_repeated_words |
| perf_optimizations.py | - | clear_cache, cache_size, embed_texts_cached, similarity_matrix, extract_many |
| performance_benchmark.py | - | time_it, benchmark_extraction, benchmark_semantic_model, run |
| performance_day60.py | - | timed, load_texts, run |
| recruiter_report.py | - | format_candidate_row, generate_recruiter_report |
| refined_decision_logic.py | - | decide_refined, batch_mode |
| refined_intent.py | - | count_hedges, is_concrete, classify_follow_up_refined |
| report_config.py | - | - |
| report_exporter.py | - | render_text, render_html, export_report |
| report_formatter.py | - | format_report_as_text, export_report |
| run_answer_understanding.py | - | build_hr_interview_summary, generate_natural_language_narrative, format_hr_summary_as_text |
| run_aptitude_evaluation.py | - | run |
| run_ats_scoring.py | - | load_json, run |
| run_behavioral_analysis.py | - | run |
| run_bug_repro.py | - | show, run |
| run_communication_scoring.py | - | run |
| run_confidence_stress_analysis.py | - | run |
| run_conversation_simulation.py | - | run |
| run_cross_round_demo.py | - | run |
| run_decision_demo.py | - | run |
| run_e2e_simulation.py | - | load_questions, run_pipeline, check_invariants, find_inconsistencies, load_reviews, compare_with_humans, measure_performance, write_review_packet, write_reports, run |
| run_edge_case_test.py | - | run |
| run_eligibility.py | - | load_json, run |
| run_fairness_check.py | - | run |
| run_final_demo.py | - | load_dataset, is_vague, make_recommendation, run_candidate, run |
| run_follow_up_demo.py | - | run |
| run_governance_demo.py | - | run |
| run_hr_interview_demo.py | - | run |
| run_hr_interview_simulation.py | - | run |
| run_hr_interview_summary.py | - | run |
| run_hr_scoring.py | - | run |
| run_load_test.py | - | cpu_request, io_request, run_level, run |
| run_observability_demo.py | - | run |
| run_optimization_analysis.py | - | reference_decision, engine_decision, score_set, show, intent_metrics, run |
| run_question_generation.py | - | run |
| run_ranking.py | - | run |
| run_report_demo.py | - | run |
| run_screening_report.py | - | run |
| run_screening_scoring.py | - | run |
| run_screening_test_suite.py | - | simulate_call, run |
| run_speed_benchmark.py | - | score_one, microseconds_per_candidate, run |
| run_stability_check.py | - | preflight, validate_e2e_data, edge_cases, fuzz, run |
| run_stt_pipeline.py | - | run |
| run_technical_scoring.py | - | load_json, build_question_index, run |
| run_transcript_demo.py | - | build_demo_transcript, run |
| run_unified_candidate_object.py | - | load_json, run |
| run_unified_scoring.py | - | load_json, run |
| safety_fallback_framework.py | - | diagnose_turn, get_safety_response |
| scenario_evaluator.py | - | evaluate_scenario_response, assess_problem_solving_clarity |
| scoring_config.py | - | get_weights |
| screening_aggregator.py | - | normalize_scores, aggregate_screening_score, apply_false_rejection_safeguard |
| screening_report_builder.py | - | summarize_key_answers, identify_strengths, identify_risks, identify_missing_data, extract_highlight_fields, build_screening_report |
| screening_scorer.py | - | score_clarity, score_relevance, score_completeness, score_consistency, score_answer |
| sentiment_scorer.py | - | get_analyzer, score_sentiment |
| speech_quality_checker.py | - | detect_silence_or_empty, detect_partial_answer, assess_response_quality |
| speech_to_text.py | - | get_whisper_model, transcribe_audio |
| stress_indicator.py | - | compute_stress_score, compute_behavioral_confidence_score |
| technical_scoring_config.py | - | - |
| technical_scoring_engine.py | - | score_accuracy, score_experience_evidence, score_depth, score_reasoning, score_applicability, classify_depth, score_answer, score_technical_interview, build_text_report |
| testing_metrics.py | - | compute_precision_recall |
| transcript_normalizer.py | - | normalize_transcript_text, extract_numeric_answer, extract_yes_no_answer |
| transcript_schema.py | - | build_empty_transcript |
| unified_candidate_object.py | - | build_unified_candidate_object |
| unified_candidate_score_object.py | - | build_unified_score_object |
| unified_scorer.py | - | compute_unified_score |
| unified_scoring_config.py | - | get_round_weights |

## utils/

| File | Classes | Public functions |
|---|---|---|
| logger.py | - | - |

Total modules indexed: 139