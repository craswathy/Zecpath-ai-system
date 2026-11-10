# Zecpath AI Technical Handbook

## How to use this handbook
This is the master document. Each section summarises one area and points
to the detailed document. For the list of every module and function, see
MODULE_INDEX.md (auto-generated). New developers should start with
DEVELOPER_ONBOARDING_GUIDE.md.

## Contents
1. System overview
2. Architecture
3. Pipeline modules
4. Scoring logic
5. Data models
6. APIs
7. Setup and deployment
8. Testing
9. Monitoring and security
10. Troubleshooting
11. Known limitations
12. Document index

## 1. System overview
Zecpath is an AI-powered hiring platform. This repository holds the AI
side: it turns resumes and job descriptions into structured data, scores
and ranks candidates, runs AI screening and HR interviews, and combines
all rounds into one explainable hiring-fit result.

Design principles used throughout:
- Explainable: every score comes with its components and weights.
- Missing data is handled by redistributing weight, never by inventing a value.
- Fairness: personal attributes are masked before scoring.
- Humans decide: AI output is a recommendation with flags for review.
- Honest limits: each module documents what it cannot do.

## 2. Architecture
Five logical AI services sit between the backend and storage:
ATS, Screening, Interview Intelligence, Behavior Analysis, and Decision
and Scoring. Slow work (resume processing, calls) is asynchronous through
a queue with webhooks. Fast work (scoring, decisions) is synchronous REST.
Full detail and diagrams: SYSTEM_ARCHITECTURE_DOCUMENTATION.md.

## 3. Pipeline modules

| Stage | Folder | Purpose | Detail document |
|---|---|---|---|
| Resume extraction | parsers/ | PDF and DOCX to clean text | ATS_TECHNICAL_DOCUMENTATION.md |
| JD parsing | parsers/ | JD text to requirement object | JD_PARSING_DOCUMENTATION.md |
| Section, skill, experience, education parsing | parsers/ | Structured candidate profile | ATS_TECHNICAL_DOCUMENTATION.md |
| Semantic matching | parsers/ | Sentence-transformer embeddings and cosine similarity | MATCHING_ACCURACY_REPORT.md |
| ATS scoring, ranking, fairness | ats_engine/ | Weighted score, zones, bias checks | ATS_TECHNICAL_DOCUMENTATION.md |
| Eligibility | ats_engine/ | Rule and score based eligibility | ATS_TECHNICAL_DOCUMENTATION.md |
| Screening | ats_engine/ | Question bank, speech-to-text, intent, scoring, state machine | SCREENING_TECHNICAL_DOCUMENTATION.md |
| HR interview | ats_engine/ | Questions, follow-ups, communication and confidence scoring, summaries | HR documents from Days 33-45 |
| Unified scoring | ats_engine/ | Cross-round hiring fit | UNIFIED_SCORING_DOCUMENTATION.md |
| Observability | ats_engine/ | Structured logs, metrics, alerts | AI_OBSERVABILITY_PLAN.md |

## 4. Scoring logic

| Score | Formula in short | Key safeguard |
|---|---|---|
| ATS score | Weighted skill match, experience relevance, education, semantic similarity (weights per role) | Missing component weight is redistributed |
| Screening score | Clarity, relevance, completeness, consistency, weighted by question category | False-rejection safeguard |
| Communication score | Fluency, grammar, vocabulary, clarity | Short-answer leniency flag |
| HR interview score | Relevance, communication, confidence, consistency | Component floor of 0.5 downgrades the band one level |
| Hiring fit | Weighted ATS, screening, HR interview (and later rounds) | Any round below 40 caps the category at Moderate Fit |

Thresholds (shortlist 70, review 40, strong fit 75, moderate fit 55) were
tuned on a small simulated set and must be recalibrated on real data.

## 5. Data models
- Resume (candidate profile) and job description schemas: data/resume_schema.json, data/jd_schema.json.
- Request and response schemas for all AI APIs: api_schemas_day59.json.
- Metadata carried by every record: candidate_id, job_id, model_version, timestamp, stage, status (METADATA_STANDARDS.md).
- Transcript schema: ats_engine/transcript_schema.py.
- Unified candidate score object: ats_engine/unified_candidate_object.py.

## 6. APIs
Five API groups: Resume Parsing, ATS Scoring, Screening, Interview, Decision.
Request and response contracts, async and sync rules, retries and
authentication: AI_INTEGRATION_DOCUMENT.md and ATS_API_SPECIFICATION.md.
Working code exists for the ATS and HR API stubs only
(ats_engine/api_server.py and the HR API from Day 44).

## 7. Setup and deployment

### Local setup
    conda create -n zecpath-ai python=3.11 -y
    conda activate zecpath-ai
    pip install -r requirements.txt
    pytest tests/

Whisper also needs ffmpeg installed and added to PATH.

### Run the ATS pipeline in order
    python -m parsers.run_extraction
    python -m parsers.run_jd_parsing
    python -m parsers.run_section_classification
    python -m parsers.run_skill_extraction
    python -m parsers.run_experience_parsing
    python -m parsers.run_education_parsing
    python -m parsers.run_semantic_matching
    python -m ats_engine.run_ats_scoring
    python -m ats_engine.run_ranking
    python -m ats_engine.run_fairness_check

### Run the API stub
    uvicorn ats_engine.api_server:app --reload

### Deployment (plan, not yet done)
1. Package each service as its own container image.
2. Load models at service start, not per request.
3. Put a load balancer in front of each service.
4. Run resume and call jobs through a queue with workers.
5. Store secrets in a secrets manager, never in the repository.
6. Follow SCALABILITY_STRATEGY.md for scaling and AI_OBSERVABILITY_PLAN.md for monitoring.

## 8. Testing
Run pytest tests/ before and after every change. One test file per
module. Tests cover logic with simulated data. They do not cover real
calls, real audio at scale or real traffic.

## 9. Monitoring and security
- Structured logs, metrics and alert rules: AI_OBSERVABILITY_PLAN.md, LOGGING_STRUCTURE.md.
- Ethics, consent and retention: the Day 43 ethics documentation.
- Logs must never contain names, emails, phones, resume text or transcripts.

## 10. Troubleshooting
See TROUBLESHOOTING_NOTES.md. Most common problems:
- ModuleNotFoundError for parsers: run with python -m, or add sys.path.append(".") in tests.
- Empty or wrong section split: check for a multi-column or scanned PDF.
- Zero shortlisted: check the real score spread before changing thresholds.
- Empty file after saving: Notepad saved nothing. Check with type before running.

## 11. Known limitations
- Mostly rule-based logic. Real ML models: sentence-transformers and Whisper (pretrained, not trained here). VADER is lexicon-based.
- Tested on about 10 resumes and 6 job descriptions, plus simulated candidates.
- No real telephony, video, queue, database or authentication is connected.
- Multilingual support is not built. Question text is English only.
- Multi-column and scanned PDFs are not handled.
- Performance and load numbers come from one laptop.

## 12. Document index
See Section 3 and Section 9 above, plus:
- SYSTEM_ARCHITECTURE_DOCUMENTATION.md
- DEVELOPER_ONBOARDING_GUIDE.md
- DEVELOPER_GUIDE.md
- CODING_STANDARDS.md
- IMPROVEMENT_BACKLOG.md
- PERFORMANCE_BENCHMARK_REPORT_DAY60.md
- MODULE_INDEX.md