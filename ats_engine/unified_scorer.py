from ats_engine.unified_scoring_config import get_round_weights
from utils.logger import logger


def compute_unified_score(round_scores, role_category=None):
    """
    Combine ATS, screening, and HR interview scores (each 0-100) into one
    hiring-fit percentage.

    round_scores: dict like {"ats": 82.0, "screening": 76.1, "hr_interview": None}
    A round with None is treated as missing, and its weight is redistributed
    across the available rounds (same graceful approach as Day 13).
    """
    weights = get_round_weights(role_category)
    available = {k: v for k, v in round_scores.items() if v is not None}
    missing = [k for k, v in round_scores.items() if v is None]

    if not available:
        return {
            "hiring_fit_percentage": 0.0,
            "round_scores_used": {},
            "weights_used": {},
            "missing_rounds": missing,
            "rounds_completed": 0,
            "explanation": "No round scores available.",
        }

    available_weight_sum = sum(weights[k] for k in available)
    adjusted_weights = {k: round(weights[k] / available_weight_sum, 3) for k in available}

    hiring_fit = round(sum(available[k] * adjusted_weights[k] for k in available), 1)

    explanation_parts = [
        f"{k.replace('_', ' ').title()}: {available[k]} (weight {adjusted_weights[k]})"
        for k in available
    ]
    if missing:
        explanation_parts.append(
            f"Missing: {', '.join(m.replace('_', ' ') for m in missing)} -- weight redistributed."
        )

    logger.info(f"Unified hiring-fit score: {hiring_fit}% ({len(available)} rounds)")

    return {
        "hiring_fit_percentage": hiring_fit,
        "round_scores_used": available,
        "weights_used": adjusted_weights,
        "missing_rounds": missing,
        "rounds_completed": len(available),
        "explanation": " | ".join(explanation_parts),
    }