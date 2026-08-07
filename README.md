# Zecpath AI System

AI-powered job portal & automated hiring assistant — ATS, screening, interview intelligence, and decision engine microservices.

## Project Layout

- **data/** — sample resumes, datasets used for testing/training
- **parsers/** — resume/document parsing logic (extract text, skills, experience)
- **ats_engine/** — resume scoring & ranking logic (ATS)
- **screening_ai/** — voice call screening logic, call scoring
- **interview_ai/** — interview intelligence: adaptive Q&A, communication/aptitude scoring
- **scoring/** — decision & scoring engine, combines all scores into final recommendation
- **utils/** — shared helpers (e.g. `logger.py`)
- **tests/** — pytest test files
- **notebooks/** — Jupyter notebooks for experimentation/prototyping

## Setup

```bash
conda create -n zecpath-ai python=3.11 -y
conda activate zecpath-ai
pip install -r requirements.txt
```

## Run Tests

```bash
pytest tests/
```

## Logging

All AI activity logs write to `ai_activity.log` via `utils/logger.py`.