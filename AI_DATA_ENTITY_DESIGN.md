\# AI Data Entity Design — Zecpath



\## Candidate Profile



Represents one candidate's full resume data, structured for AI parsing and scoring.



Contact fields (`email`/`phone`/`location`) are optional since public resume datasets often redact this information for privacy. The production system captures these details directly from the candidate registration form instead.



\## Job Profile



Represents one job posting, structured so the ATS AI Service can match candidate skills and experience against exact requirement fields rather than free text.



\## Skill Object



A nested entity inside `candidate.skills\[]` and `job.required\_skills\[]`.



Kept as its own object (not just a string list) so each skill can carry metadata such as category, proficiency, and mandatory flag, which are needed for weighted scoring.



\## Experience Object



A nested entity inside `candidate.experience\[]`.



Structured with explicit `start\_date`, `end\_date`, and `duration\_years` so the ATS AI Service can calculate total relevant experience programmatically rather than parsing free text.



\## Pattern Observations



Based on 10 sample resumes and 6 JDs:



\- Technical resumes (Data Science, Software, Java) list skills as a flat keyword list; non-technical resumes (HR, Civil) describe skills inside prose/responsibility bullets.

\- Experience is written inconsistently — some resumes give exact months, while others just state "X years at Company". The schema normalizes this into `start\_date`, `end\_date`, and `duration\_years`.

\- JDs consistently separate "requirements" from "responsibilities", mirrored in the schema as `required\_skills` and `responsibilities`.

\- Education requirements in JDs are usually just a degree name, occasionally with a specific field of study. The schema keeps `field\_of\_study` optional.

