from ats_engine.cross_round_config import (
    STRONG_FIT, MODERATE_FIT, ROUND_FLOOR, MIN_ROUNDS_FOR_FINAL, ROUND_NAMES,
)
from ats_engine.cross_round_aggregation_engine import ROUND_LABELS
from utils.logger import logger


def classify_hiring_fit(aggregate):
    """
    Turn the aggregated percentage into a fit category with flags.
    Two safeguards stop a Strong Fit label from being misleading:
    - round floor: any round below ROUND_FLOOR caps the category at Moderate Fit
    - not enough rounds: fewer than MIN_ROUNDS_FOR_FINAL makes the result preliminary
      and caps the category at Moderate Fit
    """
    pct = aggregate["hiring_fit_percentage"]
    rounds_completed = aggregate["rounds_completed"]

    if rounds_completed == 0:
        return {"hiring_fit_percentage": 0.0, "fit_category": "No data", "status": "pending",
                "flags": ["No round has been scored yet"]}

    if pct >= STRONG_FIT:
        category = "Strong Fit"
    elif pct >= MODERATE_FIT:
        category = "Moderate Fit"
    else:
        category = "Weak Fit"

    flags = []
    weak_rounds = [n for n in ROUND_NAMES if n in aggregate["round_scores"] and aggregate["round_scores"][n] < ROUND_FLOOR]
    if weak_rounds:
        flags.append(f"Weak round below {ROUND_FLOOR}: " + ", ".join(ROUND_LABELS[n] for n in weak_rounds))
        if category == "Strong Fit":
            category = "Moderate Fit"
            flags.append("Category capped at Moderate Fit due to round floor")

    status = "final" if rounds_completed >= MIN_ROUNDS_FOR_FINAL else "preliminary"
    if status == "preliminary":
        flags.append(f"Preliminary: only {rounds_completed} round(s) scored, fewer than {MIN_ROUNDS_FOR_FINAL}")
        if category == "Strong Fit":
            category = "Moderate Fit"
            flags.append("Category capped at Moderate Fit because the result is preliminary")

    if aggregate["low_reliability_rounds"]:
        flags.append("Low-reliability round(s) counted at half weight: "
                     + ", ".join(ROUND_LABELS[n] for n in aggregate["low_reliability_rounds"]))
    if aggregate["invalid_rounds"]:
        flags.append("Invalid score ignored: " + ", ".join(ROUND_LABELS[n] for n in aggregate["invalid_rounds"]))

    logger.info(f"Hiring fit: {pct}% -> {category} ({status})")
    return {"hiring_fit_percentage": pct, "fit_category": category, "status": status, "flags": flags}