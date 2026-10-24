from ats_engine.cross_round_config import (
    ROUND_NAMES, ROLE_WEIGHTS, RELIABILITY_FACTOR, CATEGORY_ORDER,
)
from utils.logger import logger

ROUND_LABELS = {
    "ats": "ATS", "screening": "Screening", "hr_interview": "HR interview",
    "technical_interview": "Technical interview", "machine_test": "Machine test",
}


def _is_valid_score(value):
    """A usable score is a number from 0 to 100 (True/False are not scores)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 100


def get_role_weights(role_category=None):
    """Return (weights, role_used). Unknown roles fall back to the default profile."""
    if role_category in ROLE_WEIGHTS:
        return ROLE_WEIGHTS[role_category], role_category
    return ROLE_WEIGHTS["default"], "default"


def aggregate_rounds(round_scores, role_category=None, low_reliability_rounds=None):
    """
    Combine up to five round scores (each 0-100, or None) into one weighted score.
    - Missing or invalid rounds are left out and their weight is shared by the rest.
    - Low-reliability rounds count for half of their weight.
    - Every contribution is returned, so the result can be checked by hand.
    """
    base_weights, role_used = get_role_weights(role_category)
    low_reliability = [r for r in (low_reliability_rounds or []) if r in ROUND_NAMES]

    scores, invalid = {}, []
    for name in ROUND_NAMES:
        value = round_scores.get(name)
        if value is None:
            continue
        if _is_valid_score(value):
            scores[name] = float(value)
        else:
            invalid.append(name)

    missing = [n for n in ROUND_NAMES if n not in scores]
    low_used = [n for n in low_reliability if n in scores]

    if not scores:
        return {
            "hiring_fit_percentage": 0.0, "role_used": role_used, "round_scores": {},
            "weights_used": {}, "contributions": {}, "rounds_completed": 0,
            "missing_rounds": missing, "invalid_rounds": invalid,
            "low_reliability_rounds": [], "explanation": "No usable round scores.",
        }

    adjusted = {n: base_weights[n] * (RELIABILITY_FACTOR if n in low_used else 1.0) for n in scores}
    total = sum(adjusted.values())
    shares = {n: adjusted[n] / total for n in scores}

    hiring_fit = round(sum(scores[n] * shares[n] for n in scores), 1)
    contributions = {n: round(scores[n] * shares[n], 2) for n in scores}
    weights_used = {n: round(shares[n], 3) for n in scores}

    parts = [f"{ROUND_LABELS[n]} {scores[n]} x {weights_used[n]}" for n in scores]
    explanation = " | ".join(parts)
    if missing:
        explanation += " | Not scored: " + ", ".join(ROUND_LABELS[n] for n in missing) + " (weight shared)"
    if low_used:
        explanation += " | Half weight (low reliability): " + ", ".join(ROUND_LABELS[n] for n in low_used)
    if invalid:
        explanation += " | Ignored invalid score: " + ", ".join(ROUND_LABELS[n] for n in invalid)

    logger.info(f"Aggregated {len(scores)} rounds for role {role_used}: {hiring_fit}")
    return {
        "hiring_fit_percentage": hiring_fit, "role_used": role_used, "round_scores": scores,
        "weights_used": weights_used, "contributions": contributions,
        "rounds_completed": len(scores), "missing_rounds": missing, "invalid_rounds": invalid,
        "low_reliability_rounds": low_used, "explanation": explanation,
    }


def rank_in_pool(category, hiring_fit, pool):
    """
    Position of one candidate among comparable candidates for the same job (1 = best).
    pool = list of (category, hiring_fit_percentage) for all comparable candidates, including this one.
    Category comes first, then percentage, so a capped Moderate Fit never outranks a Strong Fit.
    """
    if not pool:
        return None
    own = (CATEGORY_ORDER.get(category, 0), hiring_fit)
    better = sum(1 for cat, pct in pool if (CATEGORY_ORDER.get(cat, 0), pct) > own)
    return {"rank": 1 + better, "pool_size": len(pool)}