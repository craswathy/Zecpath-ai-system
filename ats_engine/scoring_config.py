# Default scoring weights per component. Must sum to 1.0.
DEFAULT_WEIGHTS = {
    "skill_match": 0.35,
    "experience_relevance": 0.25,
    "education_alignment": 0.15,
    "semantic_similarity": 0.25,
}

# Role-specific weight overrides -- e.g. technical roles weight skills higher,
# leadership/business roles weight experience higher.
ROLE_WEIGHT_PROFILES = {
    "technical": {
        "skill_match": 0.45,
        "experience_relevance": 0.20,
        "education_alignment": 0.10,
        "semantic_similarity": 0.25,
    },
    "business": {
        "skill_match": 0.25,
        "experience_relevance": 0.35,
        "education_alignment": 0.15,
        "semantic_similarity": 0.25,
    },
    "entry_level": {
        "skill_match": 0.30,
        "experience_relevance": 0.10,
        "education_alignment": 0.30,
        "semantic_similarity": 0.30,
    },
}


def get_weights(role_category=None):
    """Return the weight profile for a role category, or the default profile."""
    if role_category and role_category in ROLE_WEIGHT_PROFILES:
        return ROLE_WEIGHT_PROFILES[role_category]
    return DEFAULT_WEIGHTS