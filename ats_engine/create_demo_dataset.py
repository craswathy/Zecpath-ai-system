import json
import os

OUT = "demo_dataset_day63"

JDS = {
    "jd_data_analyst": """Data Analyst
Required skills: Python, SQL, Excel, Power BI, Statistics
Experience: 1 - 4 years
Education: Master's or Bachelor's in Statistics, Mathematics or related field
Responsibilities: clean and analyse sales data, build dashboards, present insights to stakeholders.
""",
    "jd_business_analyst": """Business Analyst
Required skills: Excel, SQL, Communication, Power BI
Experience: 2 - 6 years
Education: Bachelor's degree in any discipline
Responsibilities: gather requirements, analyse business processes, report to stakeholders.
""",
}

RESUMES = {
    "cand_priya": """SUMMARY
Data analyst with two years of experience building dashboards and statistical reports.
SKILLS
Python, SQL, Excel, Power BI, Statistics
EXPERIENCE
BrightMart Retail 06/2022 - 05/2024 // Data Analyst
- Built Power BI dashboards tracking weekly sales across 40 stores.
- Wrote SQL queries to clean and join transaction data.
DataWorks 06/2024 - present // Senior Data Analyst
- Applied hypothesis testing to measure campaign impact.
EDUCATION
Master of Science in Statistics, Christ College, 2022
""",
    "cand_arun": """SKILLS
Excel, SQL, Communication
EXPERIENCE
Metro Finance 01/2021 - 12/2023 // Business Analyst
- Prepared monthly reports and gathered requirements from managers.
EDUCATION
Bachelor of Science in Mathematics, 2020
""",
    "cand_meera": """SUMMARY
Recent graduate looking for a first role in analytics.
SKILLS
Python, Excel, Statistics
PROJECTS
Retail sales analysis using Excel and Python for a college project.
EDUCATION
Master of Science in Statistics, 2026
""",
    "cand_ravi": """SKILLS
Python, SQL, Excel, Power BI, Machine Learning, Statistics, Java, Spring Boot, AWS, Communication, Leadership, CRM
EXPERIENCE
Local Traders 03/2024 - 06/2024 // Intern
- Helped with data entry.
EDUCATION
Bachelor of Science in Computer Science, 2024
""",
    "cand_sana": """SKILLS
Python, SQL, Excel, Statistics
EXPERIENCE
Alpha Insights 01/2017 - 12/2018 // Data Analyst
- Produced weekly KPI reports.
Beta Analytics 06/2023 - 05/2024 // Data Analyst
- Built SQL reports and Excel models.
EDUCATION
Master of Science in Statistics, 2016
""",
    "cand_john": """SUMMARY
Principal data scientist with ten years of experience leading machine learning teams.
SKILLS
Python, SQL, Machine Learning, Statistics, Power BI, Leadership
EXPERIENCE
GlobalTech 01/2014 - 12/2019 // Lead Data Scientist
- Led a team of eight on forecasting models.
InnoSoft 01/2020 - present // Principal Data Scientist
- Owns the machine learning platform strategy.
EDUCATION
PhD in Statistics, 2013
""",
    "cand_divya": """Divya
Worked in reporting for three years at a small firm. Used Excel and SQL daily and
made weekly dashboards in Power BI. Completed a degree in Statistics in 2021.
""",
    "cand_kiran": """SKILLS
AutoCAD, Communication
EXPERIENCE
BuildRight 05/2019 - 08/2024 // Civil Engineer
- Site supervision and structural drawings.
EDUCATION
Bachelor of Engineering in Civil Engineering, 2019
""",
}

S = "Experience"
K = "Skills"
E = "Education"

PROFILES = [
    {"candidate_id": "cand_priya", "job_id": "jd_data_analyst", "quality": "strong, well structured",
     "simulated_screening_score": 82.0, "expected": "Strong Fit",
     "responses": [
         {"category": S, "answer": "I have two years of experience. I built dashboards for forty stores, for example weekly sales tracking, and I cut report time by half.", "duration": 14, "stt_confidence": 0.93},
         {"category": K, "answer": "I use Python and SQL every day and Power BI for reporting. I also applied hypothesis testing on campaign data.", "duration": 11, "stt_confidence": 0.95}]},
    {"candidate_id": "cand_arun", "job_id": "jd_business_analyst", "quality": "average, thin detail",
     "simulated_screening_score": 68.0, "expected": "Moderate Fit",
     "responses": [
         {"category": S, "answer": "I worked as a business analyst for three years preparing reports and talking to managers about what they needed.", "duration": 12, "stt_confidence": 0.88},
         {"category": K, "answer": "Mostly Excel and some SQL. I communicate with stakeholders regularly.", "duration": 8, "stt_confidence": 0.9}]},
    {"candidate_id": "cand_meera", "job_id": "jd_data_analyst", "quality": "fresher, no experience section",
     "simulated_screening_score": 60.0, "expected": "Moderate Fit",
     "responses": [
         {"category": S, "answer": "I am a fresher. I did a retail sales analysis project in my final year using Python and Excel.", "duration": 10, "stt_confidence": 0.9},
         {"category": K, "answer": "Python, Excel and statistics from my course work.", "duration": 6, "stt_confidence": 0.9}]},
    {"candidate_id": "cand_ravi", "job_id": "jd_data_analyst", "quality": "keyword stuffed, little substance",
     "simulated_screening_score": 40.0, "expected": "Weak Fit",
     "responses": [
         {"category": S, "answer": "um uh yeah I think maybe two years", "duration": 12, "stt_confidence": 0.7},
         {"category": K, "answer": "I love hiking and travelling on weekends", "duration": 6, "stt_confidence": 0.9}]},
    {"candidate_id": "cand_sana", "job_id": "jd_data_analyst", "quality": "good skills, long career gap",
     "simulated_screening_score": 72.0, "expected": "Moderate Fit",
     "responses": [
         {"category": S, "answer": "I worked as a data analyst for about three years in total. I took a break between 2019 and 2023 for family reasons.", "duration": 13, "stt_confidence": 0.9},
         {"category": K, "answer": "I use SQL for reports and Excel for models, and Python for cleaning data.", "duration": 9, "stt_confidence": 0.92}]},
    {"candidate_id": "cand_john", "job_id": "jd_data_analyst", "quality": "overqualified senior profile",
     "simulated_screening_score": 78.0, "expected": "Moderate Fit",
     "responses": [
         {"category": S, "answer": "I have ten years of experience. I led a team of eight and I built forecasting models, for example demand planning for retail.", "duration": 14, "stt_confidence": 0.94},
         {"category": K, "answer": "Python, SQL and machine learning, plus Power BI for reporting.", "duration": 7, "stt_confidence": 0.95}]},
    {"candidate_id": "cand_divya", "job_id": "jd_data_analyst", "quality": "unstructured resume, no headings",
     "simulated_screening_score": 70.0, "expected": "Moderate Fit",
     "responses": [
         {"category": S, "answer": "I have three years of experience in reporting, building weekly dashboards for my team.", "duration": 11, "stt_confidence": 0.9},
         {"category": K, "answer": "Excel, SQL and Power BI every day.", "duration": 6, "stt_confidence": 0.9}]},
    {"candidate_id": "cand_kiran", "job_id": "jd_data_analyst", "quality": "wrong domain",
     "simulated_screening_score": 45.0, "expected": "Weak Fit",
     "responses": [
         {"category": S, "answer": "I have five years of experience as a civil engineer supervising construction sites.", "duration": 11, "stt_confidence": 0.92},
         {"category": K, "answer": "AutoCAD and site planning.", "duration": 5, "stt_confidence": 0.92}]},
]


def run():
    for sub in ("resumes", "job_descriptions"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for name, text in RESUMES.items():
        with open(os.path.join(OUT, "resumes", f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    for name, text in JDS.items():
        with open(os.path.join(OUT, "job_descriptions", f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    with open(os.path.join(OUT, "test_candidate_profiles.json"), "w", encoding="utf-8") as f:
        json.dump(PROFILES, f, indent=2)
    print(f"Created {len(RESUMES)} resumes, {len(JDS)} job descriptions, {len(PROFILES)} profiles in {OUT}/")


if __name__ == "__main__":
    run()