# Canonical skill name -> list of known synonyms/variations
SKILL_SYNONYMS = {
    "python": ["python", "python3"],
    "sql": ["sql", "mysql", "postgresql", "t-sql", "snowflake", "bigquery"],
    "excel": ["excel", "microsoft excel", "advanced excel", "google sheets"],
    "power bi": ["power bi", "powerbi", "bi tools"],
    "machine learning": ["machine learning", "ml", "applied machine learning"],
    "javascript": ["javascript", "js"],
    "java": ["java", "core java", "java 11", "java 17"],
    "react": ["react", "reactjs", "react.js"],
    "spring boot": ["spring boot", "spring"],
    "aws": ["aws", "amazon web services"],
    "communication": ["communication skills", "written and verbal communication", "communication"],
    "leadership": ["leadership", "team leadership"],
    "autocad": ["autocad", "civil 3d"],
    "crm": ["crm", "salesforce", "hubspot", "zoho crm"],
    "statistics": ["statistics", "statistical background"],
}

def normalize_skill(raw_skill):
    """Map a raw skill mention to its canonical form using the synonym dictionary."""
    raw_lower = raw_skill.strip().lower()
    for canonical, synonyms in SKILL_SYNONYMS.items():
        if raw_lower in synonyms:
            return canonical
    return raw_lower