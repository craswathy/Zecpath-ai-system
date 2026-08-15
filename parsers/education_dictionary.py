DEGREE_PATTERNS = {
    "PhD": ["phd", "ph.d", "doctorate"],
    "Master's": ["master", "masters", "msc", "m.sc", "mba", "m.tech", "mtech", "ma", "m.a"],
    "Bachelor's": ["bachelor", "bachelors", "bsc", "b.sc", "b.tech", "btech", "ba", "b.a", "be", "b.e"],
    "Diploma": ["diploma"],
    "Higher Secondary": ["higher secondary", "12th", "+2", "hsc"],
}

# Common field-of-study keywords -> canonical name
FIELD_OF_STUDY = {
    "statistics": ["statistics", "stats"],
    "computer science": ["computer science", "cs", "computer applications"],
    "mathematics": ["mathematics", "maths", "math"],
    "civil engineering": ["civil engineering"],
    "business administration": ["business administration", "mba", "management"],
    "data science": ["data science"],
    "economics": ["economics"],
}

# Certification issuer keywords -> relevance category
CERTIFICATION_CATEGORIES = {
    "aws": "cloud",
    "amazon web services": "cloud",
    "microsoft azure": "cloud",
    "google cloud": "cloud",
    "google analytics": "analytics",
    "power bi": "analytics",
    "tableau": "analytics",
    "pmp": "project management",
    "scrum": "project management",
    "six sigma": "process improvement",
    "coursera": "general",
    "udemy": "general",
    "nptel": "general",
}