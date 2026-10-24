# Day 51: all numbers live here. Starting values, not tuned on real data.

MODEL_VERSION = "unified_v2.0"

ROUND_NAMES = ["ats", "screening", "hr_interview", "technical_interview", "machine_test"]

# Weights per role. Each row adds up to 1.0.
ROLE_WEIGHTS = {
    "default": {"ats": 0.15, "screening": 0.20, "hr_interview": 0.25, "technical_interview": 0.25, "machine_test": 0.15},
    "technical": {"ats": 0.10, "screening": 0.15, "hr_interview": 0.15, "technical_interview": 0.30, "machine_test": 0.30},
    "client_facing": {"ats": 0.15, "screening": 0.20, "hr_interview": 0.40, "technical_interview": 0.15, "machine_test": 0.10},
    "entry_level": {"ats": 0.15, "screening": 0.25, "hr_interview": 0.20, "technical_interview": 0.20, "machine_test": 0.20},
    "senior": {"ats": 0.10, "screening": 0.10, "hr_interview": 0.20, "technical_interview": 0.35, "machine_test": 0.25},
}

# A round marked low reliability counts for half of its normal weight
RELIABILITY_FACTOR = 0.5

STRONG_FIT = 75
MODERATE_FIT = 55
ROUND_FLOOR = 40           # any round below this caps the category at Moderate Fit
MIN_ROUNDS_FOR_FINAL = 3   # fewer rounds = preliminary result

# Used only to rank candidates: a higher category always ranks above a lower one
CATEGORY_ORDER = {"Strong Fit": 3, "Moderate Fit": 2, "Weak Fit": 1}