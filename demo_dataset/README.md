# Zecpath ATS Demo Dataset

A small, representative subset of the full test set (10 resumes, 6 JDs)
used for live demonstration purposes.

## Contents
- ba_resume_1.pdf (Business Analyst, non-technical)
- da_resume_1.pdf (Data Analyst, technical)
- java_resume_1.pdf (Java Developer, technical)
- jd_business_analyst.txt
- jd_data_analyst.txt
- jd_software_engineer.txt

## How to Demo
Run the full pipeline (see DEVELOPER_GUIDE.md "Running the Full Pipeline"),
then show:
1. `data/labeled_sections/da_resume_1_labeled.json` -- structured sections
2. `data/skills_extracted/da_resume_1_skills.json` -- confidence-scored skills
3. `data/ats_scores/da_resume_1_ats_score.json` -- explainable final score
4. `data/rankings/recruiter_report.txt` -- ranked shortlist output