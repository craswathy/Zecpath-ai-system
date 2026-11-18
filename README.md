# Zecpath AI Hiring Platform: AI Engine

Python AI engine for an AI-powered hiring platform. It turns resumes and job
descriptions into structured data, scores and ranks candidates with an
explainable method, scores AI screening and interview answers, and combines
all rounds into one hiring-fit recommendation with flags for human review.

Built during a remote internship at Zecser Business LLP. All demo candidates
are fictional.

## What it does

1. Parses resumes and job descriptions (PDF, DOCX, text) into a fixed schema.
2. Scores resume-to-job match with weighted skills, experience, education and
   semantic similarity (sentence-transformers), then ranks and checks fairness.
3. Runs AI screening and HR interview scoring (speech-to-text with Whisper,
   intent and sentiment analysis, communication and confidence scoring).
4. Scores technical interviews and combines all rounds into one decision with
   safeguards: a failed stage always goes to a human.
5. Provides APIs, structured logging, monitoring rules and governance controls.

## Design principles

- Explainable: every score shows its components and weights.
- Missing data is never invented. Weight is redistributed.
- Personal attributes are masked before scoring.
- AI recommends, people decide.
- Each module documents its limits.

## Tech stack

Python 3.11, sentence-transformers, OpenAI Whisper, VADER, FastAPI, pytest, Git.

## Repository structure

    parsers/       extraction, parsing and semantic matching
    ats_engine/    scoring, ranking, screening, interview, decision, API, observability
    utils/         shared logger
    tests/         one test file per module
    data/          sample inputs and stage outputs
    demo_dataset_day63/   fictional demo candidates and jobs
    notebooks/     experiments (not production code)
    *.md           documentation (see DOCUMENTATION_INDEX.md)

## Setup

    conda create -n zecpath-ai python=3.11 -y
    conda activate zecpath-ai
    pip install -r requirements.txt

Speech-to-text also needs ffmpeg installed and added to PATH.

## Run the pipeline

Run from the project folder, in this order:

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

## Run the demo

    python -m ats_engine.create_demo_dataset
    python -m ats_engine.run_demo_simulation
    python -m ats_engine.polished_reports

## Run the API

    uvicorn ats_engine.polished_api:app --reload

Open http://127.0.0.1:8000/docs and try POST /api/v1/decisions.

## Run the tests

    pytest tests/

## Documentation

Start with ZECPATH_AI_TECHNICAL_HANDBOOK.md, then DOCUMENTATION_INDEX.md for
the full list. New developers: DEVELOPER_ONBOARDING_GUIDE.md.

## Known limitations

- Tested on a small set of resumes and fictional candidates. Accuracy on real
  hiring data has not been measured.
- Thresholds and weights were tuned on small data and need recalibration.
- Skill detection is dictionary based. Multi-column and scanned PDFs are not handled.
- English only. No real telephony or video analysis.
- No deployed database, queue or authentication. Performance numbers come
  from one laptop.

## Roadmap

See AI_ROADMAP.md.

## Author

C R Aswathy, Data Science Engineer intern, Zecser Business LLP. GitHub: craswathy.