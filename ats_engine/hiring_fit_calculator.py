from ats_engine.unified_scoring_config import FIT_THRESHOLDS, ROUND_FLOOR
from utils.logger import logger


def classify_hiring_fit(unified_result):
    """
    Turn the numeric hiring-fit percentage into a category (Strong /
    Moderate / Weak), with two safeguards:
    1. Round floor: any single round below ROUND_FLOOR caps the category
       at Moderate Fit (the Day 40 fix for strong rounds masking a weak one).
    2. Data sufficiency: fewer than 2 completed rounds is flagged.
    """
    score = unified_result["hiring_fit_percentage"]
    rounds_used = unified_result["round_scores_used"]
    flags = []

    if score >= FIT_THRESHOLDS["strong_fit"]:
        category = "Strong Fit"
    elif score >= FIT_THRESHOLDS["moderate_fit"]:
        category = "Moderate Fit"
    else:
        category = "Weak Fit"

    weak_rounds = [k for k, v in rounds_used.items() if v < ROUND_FLOOR]
    if weak_rounds:
        flags.append(
            f"Weak round(s): {', '.join(weak_rounds)} scored below {ROUND_FLOOR} -- review before deciding"
        )
        if category == "Strong Fit":
            category = "Moderate Fit"
            flags.append("Category capped at Moderate Fit due to round floor")

    if unified_result["rounds_completed"] < 2:
        flags.append("Based on fewer than 2 completed rounds -- low confidence")

    logger.info(f"Hiring fit category: {category}")

    return {
        "hiring_fit_percentage": score,
        "fit_category": category,
        "flags": flags,
    }