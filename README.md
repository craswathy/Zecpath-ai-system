\# Zecpath AI System



AI-powered job portal \& automated hiring assistant — ATS, screening, interview intelligence, and decision engine microservices.



\## Project Layout



\- \*\*data/\*\* — sample resumes, datasets used for testing/training

\- \*\*parsers/\*\* — resume/document parsing logic (extract text, skills, experience)

\- \*\*ats\_engine/\*\* — resume scoring \& ranking logic (ATS)

\- \*\*screening\_ai/\*\* — voice call screening logic, call scoring

\- \*\*interview\_ai/\*\* — interview intelligence: adaptive Q\&A, communication/aptitude scoring

\- \*\*scoring/\*\* — decision \& scoring engine, combines all scores into final recommendation

\- \*\*utils/\*\* — shared helpers (e.g. logger.py)

\- \*\*tests/\*\* — pytest test files

\- \*\*notebooks/\*\* — Jupyter notebooks for experimentation/prototyping



\## Setup

conda create -n zecpath-ai python=3.11 -y

conda activate zecpath-ai

pip install -r requirements.txt



\## Run Tests

pytest tests/



\## Logging

All AI activity logs write to ai\_activity.log via utils/logger.py.

