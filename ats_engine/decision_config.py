# Day 52: all numbers and labels live here. Starting values, not tuned on real data.

MODEL_VERSION = "decision_v1.0"

SELECTED = "Selected"
HOLD = "Hold / Review"
REJECTED = "Rejected"

# Score-based starting point: the Day 51 fit category decides it
CATEGORY_TO_DECISION = {"Strong Fit": SELECTED, "Moderate Fit": HOLD, "Weak Fit": REJECTED}

# Hiring-fit percentages that separate the three decisions
SELECT_LINE = 75
REJECT_LINE = 55
BORDER_MARGIN = 3   # within this many points of a line, the decision goes to Hold / Review

# Confidence score (0 to 1) = weighted sum of four parts, minus risk penalties
CONFIDENCE_WEIGHTS = {"completeness": 0.35, "reliability": 0.20, "agreement": 0.25, "margin": 0.20}
AGREEMENT_RANGE = 60       # gap between best and worst round that gives agreement 0
MARGIN_FULL = 15           # distance from a decision line that gives margin 1.0
PRELIMINARY_CONFIDENCE_CAP = 0.4

# Integrity risk (Day 49 tags): confidence penalty
INTEGRITY_PENALTY = {"Medium": 0.10, "High": 0.20}

# A decision other than Hold / Review needs at least this much confidence
MIN_CONFIDENCE = {SELECTED: 0.6, REJECTED: 0.7}

HIGH_CONFIDENCE = 0.75
MEDIUM_CONFIDENCE = 0.5

# Rounds that must be scored before Selected or Rejected can be recommended
REQUIRED_ROUNDS = {
    "default": ["hr_interview"],
    "technical": ["technical_interview"],
    "senior": ["technical_interview"],
    "client_facing": ["hr_interview"],
    "entry_level": ["hr_interview"],
}

ROUND_FLOOR = 40   # same floor as the Day 51 aggregation