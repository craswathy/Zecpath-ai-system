# Master skill dictionary, organized by category
# Each canonical skill maps to known synonyms/spelling variations

TECH_SKILLS = {
    "python": ["python", "python3", "pyhton", "phyton"],
    "sql": ["sql", "mysql", "postgresql", "t-sql", "snowflake", "bigquery"],
    "excel": ["excel", "microsoft excel", "advanced excel", "google sheets"],
    "power bi": ["power bi", "powerbi", "power-bi"],
    "machine learning": ["machine learning", "ml", "applied machine learning"],
    "javascript": ["javascript", "js", "java script"],
    "java": ["java", "core java", "java 11", "java 17"],
    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node.js", "nodejs", "node js"],
    "express.js": ["express.js", "expressjs", "express"],
    "mongodb": ["mongodb", "mongo db", "mongo"],
    "angular": ["angular", "angularjs"],
    "spring boot": ["spring boot", "springboot", "spring"],
    "aws": ["aws", "amazon web services"],
    "autocad": ["autocad", "auto cad"],
    "civil 3d": ["civil 3d", "civil3d"],
    "tensorflow": ["tensorflow", "tensor flow"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy", "num py"],
    "statistics": ["statistics", "statistical background", "stats"],
}

BUSINESS_SKILLS = {
    "communication": ["communication skills", "written and verbal communication", "communication"],
    "leadership": ["leadership", "team leadership"],
    "stakeholder management": ["stakeholder management", "stakeholder engagement"],
    "crm": ["crm", "salesforce", "hubspot", "zoho crm"],
    "business analysis": ["business analysis", "ba", "requirements gathering"],
    "project management": ["project management", "pm"],
    "reporting": ["reporting", "report automation", "dashboard reporting"],
    "negotiation": ["negotiation", "negotiation skills"],

}

CREATIVE_SKILLS = {
    "graphic design": ["graphic design", "graphics design"],
    "ui/ux design": ["ui/ux design", "ui ux", "ux design", "ui design"],
    "figma": ["figma"],
    "adobe photoshop": ["photoshop", "adobe photoshop"],
    "content writing": ["content writing", "copywriting"],
}

# Skill stacks: one mention expands into multiple component skills
SKILL_STACKS = {
    "mern": ["mongodb", "express.js", "react", "node.js"],
    "mean": ["mongodb", "angular", "express.js", "node.js"],
    "lamp": ["linux", "apache", "mysql", "php"],
}

# Merge all categories into one lookup, tagged by category
ALL_SKILLS = {}
for skill, syns in TECH_SKILLS.items():
    ALL_SKILLS[skill] = {"synonyms": syns, "category": "technical"}
for skill, syns in BUSINESS_SKILLS.items():
    ALL_SKILLS[skill] = {"synonyms": syns, "category": "business"}
for skill, syns in CREATIVE_SKILLS.items():
    ALL_SKILLS[skill] = {"synonyms": syns, "category": "creative"}