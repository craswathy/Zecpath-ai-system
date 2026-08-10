import re
from parsers.skill_dictionary import SKILL_SYNONYMS, normalize_skill
from utils.logger import logger


def extract_title(text):
    """First non-empty line is usually the job title."""
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line
    return "Unknown"


def extract_required_skills(text):
    """Scan JD text for known skills/synonyms, return normalized list."""
    text_lower = text.lower()
    found = set()
    for canonical, synonyms in SKILL_SYNONYMS.items():
        for syn in synonyms:
            if syn in text_lower:
                found.add(canonical)
                break
    return sorted(found)


def extract_experience_years(text):
    """Find patterns like '2+ years', '0-4 Yrs', '3 of years of experience'."""
    patterns = [
        r"(\d+)\s*\+?\s*[-to]{0,4}\s*(\d+)?\s*\+?\s*years?",
        r"(\d+)\s*-\s*(\d+)\s*yrs?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = [g for g in match.groups() if g]
            nums = [int(g) for g in groups]
            return {"min_experience_years": min(nums), "max_experience_years": max(nums)}
    return {"min_experience_years": None, "max_experience_years": None}


def extract_education(text):
    """Look for common degree keywords."""
    degree_keywords = {
        "phd": "PhD",
        "master": "Master's",
        "postgraduate": "Postgraduate",
        "bachelor": "Bachelor's",
        "b.tech": "Bachelor's",
        "undergraduate": "Undergraduate",
    }
    text_lower = text.lower()
    for keyword, label in degree_keywords.items():
        if keyword in text_lower:
            return label
    return "Not specified"


def parse_jd(text, job_id="unknown"):
    """Convert raw JD text into a structured job requirement object."""
    title = extract_title(text)
    skills = extract_required_skills(text)
    experience = extract_experience_years(text)
    education = extract_education(text)

    jd_profile = {
        "job_id": job_id,
        "title": title,
        "required_skills": [{"name": s, "mandatory": True} for s in skills],
        "min_experience_years": experience["min_experience_years"],
        "max_experience_years": experience["max_experience_years"],
        "education_requirement": {"degree": education, "field_of_study": None},
    }

    logger.info(f"Parsed JD '{job_id}': {len(skills)} skills found, title='{title}'")
    return jd_profile