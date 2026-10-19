# Day 47: all numbers live here. Starting values, not tuned on real data.

# Weights per question type. Each row adds up to 1.0.
PARAMETER_WEIGHTS = {
    "conceptual": {"accuracy": 0.45, "depth": 0.25, "reasoning": 0.20, "applicability": 0.10},
    "scenario": {"accuracy": 0.25, "depth": 0.20, "reasoning": 0.30, "applicability": 0.25},
    "experience": {"accuracy": 0.20, "depth": 0.30, "reasoning": 0.15, "applicability": 0.35},
}

# Harder questions count more when answers are combined
LEVEL_WEIGHTS = {"L1": 1.0, "L2": 1.5, "L3": 2.0}

# Words a good answer is expected to have, by level
TARGET_WORDS = {"L1": 20, "L2": 35, "L3": 50}

PASS_SCORE = 0.6          # answer counts as "passed" at or above this
SKILL_FLOOR = 0.4         # a skill below this lowers the overall band one level
MIN_RELIABLE_ANSWERS = 5  # fewer scored answers = low reliability

BAND_STRONG = 75
BAND_ADEQUATE = 50