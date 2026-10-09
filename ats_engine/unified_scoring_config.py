# Cross-round weight configuration -- Zecpath
# Same pattern as Day 13's scoring_config.py and Day 37's hr_scoring_config.py,
# but the "components" here are whole hiring rounds, not individual signals.

DEFAULT_ROUND_WEIGHTS = {
    "ats": 0.30,
    "screening": 0.30,
    "hr_interview": 0.40,
}

ROLE_ROUND_WEIGHT_PROFILES = {
    "technical": {"ats": 0.40, "screening": 0.25, "hr_interview": 0.35},
    "client_facing": {"ats": 0.20, "screening": 0.30, "hr_interview": 0.50},
    "entry_level": {"ats": 0.35, "screening": 0.30, "hr_interview": 0.35},
}

# Hiring-fit category thresholds (0-100)
FIT_THRESHOLDS = {
    "strong_fit": 75,
    "moderate_fit": 55,
}

# Day 40 lesson: if any single round scores below this floor, the overall
# category is capped at "Moderate Fit" no matter how high the average is.
ROUND_FLOOR = 40


def get_round_weights(role_category=None):
    """Return the cross-round weight profile for a role category, or the default."""
    if role_category and role_category in ROLE_ROUND_WEIGHT_PROFILES:
        return ROLE_ROUND_WEIGHT_PROFILES[role_category]
    return DEFAULT_ROUND_WEIGHTS