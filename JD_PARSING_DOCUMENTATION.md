\# JD Parsing Documentation — Zecpath



\## Overview

`parsers/jd\_parser.py` converts raw job description text into a structured

job requirement object matching the JD schema defined in Day 4

(`data/jd\_schema.json`).



\## Extraction Logic

\- \*\*Title\*\* — first non-empty line of the JD text.

\- \*\*Required Skills\*\* — keyword/synonym matching against `skill\_dictionary.py`,

&#x20; which maps common variations (e.g. "ML", "Machine Learning", "Applied

&#x20; Machine Learning") to one canonical skill name, so downstream ATS scoring

&#x20; doesn't need to know every possible phrasing.

\- \*\*Experience Requirement\*\* — regex pattern matching on common phrasings

&#x20; ("2+ years", "0 - 4 Yrs", etc.), returning a min/max range.

\- \*\*Education Requirement\*\* — keyword match against common degree terms

&#x20; (PhD, Master's, Bachelor's, Postgraduate).



\## Known Limitations

\- Skill detection is dictionary-based, not NLP-based — skills not in

&#x20; `SKILL\_SYNONYMS` will not be detected. Dictionary needs to grow as more

&#x20; JDs are processed.

\- Experience regex may miss unusual phrasings not yet seen in the sample set.

\- Education detection returns the first match only, not a full requirement list.



\## Sample Output

See `data/jd\_parsed/` for structured JSON output per job description,

one file per JD processed.

