# Developer Guide -- Zecpath ATS

## Getting Started
1. Clone the repo, create the conda environment:

```
conda create -n zecpath-ai python=3.11 -y
conda activate zecpath-ai
pip install -r requirements.txt
```

2. Verify setup:


`pytest tests/`


   All tests should pass before making changes.

## Project Structure

​```
data/                 -- sample resumes, JDs, and all pipeline output
parsers/              -- extraction, parsing, matching modules (Days 5-12)
ats_engine/           -- scoring, ranking, fairness, API modules (Days 13-18)
utils/                -- shared logger
tests/                -- one test file per module
notebooks/            -- experimentation/prototyping only, not production code
​```



## Adding a New Feature
1. Check ATS_TECHNICAL_DOCUMENTATION.md to see which pipeline stage your
   feature belongs to.
2. Follow CODING_STANDARDS.md (PEP8, docstrings, one module = one responsibility).
3. Add a test in `tests/` before considering the feature done.
4. Use the shared logger (`from utils.logger import logger`) instead of print().
5. Update ATS_TECHNICAL_DOCUMENTATION.md if you add a new module.

## Running the Full Pipeline
See "Full Pipeline Execution Order" in ATS_TECHNICAL_DOCUMENTATION.md.

## Where to Look When Something Breaks
See TROUBLESHOOTING_NOTES.md for known issues and their root causes.

## Key Design Decisions to Understand Before Modifying
- Scoring weights are configurable per role category (scoring_config.py) --
  don't hardcode weights elsewhere.
- Missing data is handled by weight redistribution, not by defaulting to
  zero (see ats_scorer.py) -- preserve this pattern in any scoring changes.
- Personal attributes are masked before scoring (fairness_normalizer.py) --
  never bypass this when adding new scoring inputs.