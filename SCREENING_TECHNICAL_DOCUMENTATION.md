# Screening System Technical Documentation -- Zecpath

## Purpose
Master reference for the AI screening pipeline (Days 22-31), covering
question generation through final screening report, with edge-case
handling built in throughout.

## Pipeline Stages

### 1. HR Question Bank (Day 22)
- **Module**: `ats_engine/hr_question_bank.py`, `ats_engine/conversation_question_builder.py`
- **Output**: Job-specific question sets in `data/screening_questions/`
- **Key logic**: Category-tagged question templates with placeholder
  filling from JD data (Day 6).

### 2. Transcript Data Architecture (Day 23)
- **Module**: `ats_engine/transcript_schema.py`, `ats_engine/transcript_normalizer.py`
- **Key logic**: Structured transcript schema with call/turn-level metadata,
  disfluency removal, spoken-number normalization.

### 3. Speech-to-Text Integration (Day 24)
- **Module**: `ats_engine/speech_to_text.py`, `ats_engine/speech_quality_checker.py`
- **Key logic**: Whisper-based transcription with confidence estimation,
  silence/partial-answer detection.
- **See also**: STT_ACCURACY_TEST_REPORT.md

### 4. Answer Understanding (Day 25)
- **Module**: `ats_engine/intent_classifier.py`, `ats_engine/answer_extractor.py`
- **Key logic**: Pattern-based intent classification, off-topic detection,
  type-specific value extraction (numeric, availability, salary).

### 5. Screening Scoring (Day 26)
- **Module**: `ats_engine/screening_scorer.py`, `ats_engine/screening_aggregator.py`
- **Key logic**: 4-component weighted scoring (clarity, relevance,
  completeness, consistency), category-importance-weighted aggregation,
  false-rejection safeguard (Day 30).

### 6. Confidence & Sentiment Analysis (Day 27)
- **Module**: `ats_engine/confidence_analyzer.py`, `ats_engine/sentiment_scorer.py`, `ats_engine/behavioral_indicators.py`
- **Key logic**: Hesitation marker detection, VADER sentiment scoring,
  pace analysis, combined communication-strength indicator.

### 7. Screening Report Generator (Day 28)
- **Module**: `ats_engine/screening_report_builder.py`, `ats_engine/report_formatter.py`
- **Output**: Recruiter-ready reports in `data/screening_reports/`
- **Key logic**: Strengths/risks/missing-data summarization, JSON + plain-text export.

### 8. Conversation Flow (Day 29)
- **Module**: `ats_engine/conversation_state_machine.py`, `ats_engine/fallback_questions.py`
- **Key logic**: State machine managing greeting -> question -> answer ->
  retry/clarify -> next -> close, with configurable retry limits.

### 9. Testing & Optimization (Day 30)
- **Module**: `ats_engine/run_screening_test_suite.py`
- **Key finding**: Fixed a state-machine bug where retry-loop control
  signals were misinterpreted as candidate answers, silently discarding
  real responses during retry states.

### 10. Edge Case Handling (Day 31)
- **Module**: `ats_engine/audio_edge_cases.py`, `ats_engine/safety_fallback_framework.py`
- **Key logic**: Prioritized diagnosis (technical failure > audio quality
  > language mixing > missing answer > off-topic > vague), unified
  safety-response system with retry-limit escalation to human review.

## Full Pipeline Execution Order
```
python -m ats_engine.run_question_generation
python -m ats_engine.run_transcript_demo
python -m ats_engine.run_answer_understanding
python -m ats_engine.run_screening_scoring
python -m ats_engine.run_behavioral_analysis
python -m ats_engine.run_screening_report
python -m ats_engine.run_conversation_simulation
python -m ats_engine.run_screening_test_suite
python -m ats_engine.run_edge_case_test
```