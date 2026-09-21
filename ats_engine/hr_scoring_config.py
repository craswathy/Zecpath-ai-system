# HR Interview Scoring Weight Configuration -- Zecpath
# Mirrors Day 13's scoring_config.py pattern, but for the HR interview
# round (Day 33-36 outputs) rather than resume/ATS scoring.

DEFAULT_HR_WEIGHTS = {
    "relevance": 0.35,
    "communication": 0.25,
    "confidence": 0.20,
    "consistency": 0.20,
}

# Role-specific overrides, same pattern as Day 13
HR_ROLE_WEIGHT_PROFILES = {
    "technical": {
        "relevance": 0.40,
        "communication": 0.20,
        "confidence": 0.15,
        "consistency": 0.25,
    },
    "client_facing": {
        "relevance": 0.25,
        "communication": 0.40,
        "confidence": 0.20,
        "consistency": 0.15,
    },
    "senior": {
        "relevance": 0.30,
        "communication": 0.25,
        "confidence": 0.15,
        "consistency": 0.30,
    },
}


def get_hr_weights(role_category=None):
    """Return the HR scoring weight profile for a role category, or the default."""
    if role_category and role_category in HR_ROLE_WEIGHT_PROFILES:
        return HR_ROLE_WEIGHT_PROFILES[role_category]
    return DEFAULT_HR_WEIGHTS