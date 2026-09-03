

# HR Screening Question Category Mapping -- Zecpath

## Categories and Purpose

| Category | Purpose | Typical Scoring Importance |
|---|---|---|
| Introduction | Warm-up, communication style baseline | Low |
| Education | Verify qualification meets job requirement | Medium |
| Experience | Core fit assessment -- years and role relevance | High |
| Skills | Technical/role-specific competency check | High |
| Location | Logistics -- relocation/remote feasibility | Medium |
| Salary | Budget alignment check | Medium |
| Notice Period | Joining timeline feasibility | Medium |

## Answer Type Reference

| Answer Type | Description | Example |
|---|---|---|
| free_text | Open-ended spoken/written response | "Tell me about yourself" |
| numeric | A number value | "How many years of experience?" |
| numeric_scale | Self-rated scale (e.g. 1-5) | "Rate your Python proficiency" |
| multiple_choice | Selection from a fixed list | "Which tools have you used?" |
| yes_no | Binary response | "Are you open to relocating?" |

## Role Applicability
- **all**: asked regardless of role type (Introduction, Education baseline, Location, Salary, Notice Period)
- **technical**: only asked for technical roles (Software Engineer, Data Analyst, Java Developer) -- skill-specific questions
- **business**: reserved for non-technical role-specific questions (not yet populated -- see backlog)

## Template Placeholders
Questions may contain placeholders filled in per job posting:
- `{role_specific_skill_list}` -- populated from the JD's required_skills (Day 6)
- `{primary_skill}` -- the JD's top-priority mandatory skill
- `{job_location}` -- from the JD's location field