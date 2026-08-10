# JD Parsing Documentation — Zecpath

## Overview

`parsers/jd_parser.py` converts raw job description text into a structured
job requirement object matching the JD schema defined in Day 4
(`data/jd_schema.json`).

## Extraction Logic

- **Title** — first non-empty line of the JD text.
- **Required Skills** — keyword/synonym matching against `skill_dictionary.py`,
  which maps common variations (e.g. "ML", "Machine Learning", "Applied
  Machine Learning") to one canonical skill name, so downstream ATS scoring
  doesn't need to know every possible phrasing.
- **Experience Requirement** — regex pattern matching on common phrasings
  ("2+ years", "0 - 4 Yrs", etc.), returning a min/max range.
- **Education Requirement** — keyword match against common degree terms
  (PhD, Master's, Bachelor's, Postgraduate).

## Known Limitations

- Skill detection is dictionary-based, not NLP-based — skills not in
  `SKILL_SYNONYMS` will not be detected. Dictionary needs to grow as more
  JDs are processed.
- Experience regex may miss unusual phrasings not yet seen in the sample set.
- Education detection returns the first match only, not a full requirement list.

## Sample Output

See `data/jd_parsed/` for structured JSON output per job description,
one file per JD processed.