# Per-job eligibility rule configuration.
# Each job_id maps to a set of hard requirements checked BEFORE/ALONGSIDE
# the ATS score (Day 13), not replacing it.

ELIGIBILITY_RULES = {
    "jd_data_analyst": {
        "min_ats_score": 60,
        "mandatory_skills": ["sql", "excel"],
        "min_experience_years": 0,
        "max_experience_years": 6,
        "allowed_locations": None,  # None = no restriction
    },
    "jd_business_analyst": {
        "min_ats_score": 55,
        "mandatory_skills": ["communication", "excel"],
        "min_experience_years": 2,
        "max_experience_years": 8,
        "allowed_locations": None,
    },
    "jd_software_engineer": {
        "min_ats_score": 65,
        "mandatory_skills": ["java"],
        "min_experience_years": 0,
        "max_experience_years": 10,
        "allowed_locations": None,
    },
}

DEFAULT_RULES = {
    "min_ats_score": 50,
    "mandatory_skills": [],
    "min_experience_years": 0,
    "max_experience_years": 40,
    "allowed_locations": None,
}


def get_rules(job_id):
    """Return the eligibility rule set for a job, or defaults if not configured."""
    return ELIGIBILITY_RULES.get(job_id, DEFAULT_RULES)