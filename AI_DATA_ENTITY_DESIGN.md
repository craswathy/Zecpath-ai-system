# AI Data Entity Design — Zecpath

## Candidate Profile

Represents one candidate's full resume data, structured for AI parsing and scoring.

Contact fields (`email`/`phone`/`location`) are optional since public resume datasets often redact this information for privacy. The production system captures these details directly from the candidate registration form instead.

## Job Profile

Represents one job posting, structured so the ATS AI Service can match candidate skills and experience against exact requirement fields rather than free text.

## Skill Object

A nested entity inside `candidate.skills[]` and `job.required_skills[]`.

Kept as its own object (not just a string list) so each skill can carry metadata — category, proficiency, mandatory flag — needed for weighted scoring.

## Experience Object

A nested entity inside `candidate.experience[]`.

Structured with explicit `start_date`, `end_date`, and `duration_years` so the ATS AI Service can calculate total relevant experience programmatically, rather than parsing free text.

## Pattern Observations (from 10 sample resumes + 6 JDs)

- Technical resumes (Data Science, Software, Java) list skills as a flat keyword list; non-technical resumes (HR, Civil) describe skills inside prose/responsibility bullets.
- Experience is written inconsistently — some resumes give exact months, others just "X years at Company" — schema normalizes this into `start_date`/`end_date`/`duration_years`.
- JDs consistently separate "requirements" from "responsibilities" — mirrored in the schema as `required_skills` vs `responsibilities`.
- Education requirement in JDs is usually just a degree name, occasionally a specific field of study — schema keeps `field_of_study` optional.