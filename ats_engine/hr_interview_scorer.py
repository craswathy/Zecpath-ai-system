from ats_engine.hr_scoring_config import get_hr_weights
from utils.logger import logger

# Day 42: a component below this floor downgrades the overall band one level
COMPONENT_FLOOR = 0.5
BAND_ORDER = ["Below-expectation", "Adequate", "Strong"]


def score_relevance_for_turn(is_off_topic, is_vague_or_missing):
    """Relevance score for one HR interview answer."""
    if is_off_topic:
        return 0.1
    if is_vague_or_missing:
        return 0.3
    return 1.0


def score_consistency_for_candidate(contradiction_count, total_turns):
    """Consistency across the whole interview (inverse of contradiction density)."""
    if total_turns == 0:
        return 1.0
    contradiction_rate = contradiction_count / total_turns
    return round(max(0.0, 1.0 - contradiction_rate * 2), 2)


def classify_performance_band(score, component_scores):
    """
    Band from the weighted score, then downgraded one level if any single
    component is below COMPONENT_FLOOR, so strong components cannot hide a
    weak one. Returns (band, weak_components, adjusted_from).
    """
    if score >= 75:
        base = "Strong"
    elif score >= 50:
        base = "Adequate"
    else:
        base = "Below-expectation"

    weak = [name for name, value in component_scores.items() if value < COMPONENT_FLOOR]
    if weak and base != "Below-expectation":
        return BAND_ORDER[BAND_ORDER.index(base) - 1], weak, base
    return base, weak, None


def _average_scaled(per_turn_data, key):
    """Average a 0-100 per-turn field to 0-1. Returns None if no turn has it."""
    values = [t[key] for t in per_turn_data if t.get(key) is not None]
    if not values:
        return None
    return round(sum(values) / len(values) / 100, 2)


def compute_hr_interview_score(per_turn_data, contradiction_count, role_category=None):
    """
    Combine relevance, communication, confidence, and consistency into one
    explainable HR interview score (0-100). A component with no data is
    excluded and its weight redistributed, never filled with a fake value.
    """
    weights = get_hr_weights(role_category)
    total_turns = len(per_turn_data)

    if total_turns == 0:
        return {
            "hr_interview_score": 0.0,
            "component_scores": {},
            "weights_used": {},
            "turns_scored": 0,
            "missing_components": [],
            "weak_components": [],
            "performance_band": "No data",
            "band_adjusted_from": None,
            "explanation": "No interview responses to score.",
        }

    relevance_scores = [
        score_relevance_for_turn(t["is_off_topic"], t["is_vague_or_missing"])
        for t in per_turn_data
    ]
    all_components = {
        "relevance": round(sum(relevance_scores) / total_turns, 2),
        "communication": _average_scaled(per_turn_data, "communication_score"),
        "confidence": _average_scaled(per_turn_data, "behavioral_confidence_score"),
        "consistency": score_consistency_for_candidate(contradiction_count, total_turns),
    }

    component_scores = {k: v for k, v in all_components.items() if v is not None}
    missing = [k for k, v in all_components.items() if v is None]

    if missing:
        weight_total = sum(weights[k] for k in component_scores)
        effective = {k: weights[k] / weight_total for k in component_scores}
    else:
        effective = {k: weights[k] for k in component_scores}

    final_score = round(sum(component_scores[k] * effective[k] for k in component_scores) * 100, 1)
    weights_used = {k: round(effective[k], 3) for k in effective}

    band, weak, adjusted_from = classify_performance_band(final_score, component_scores)

    explanation = " | ".join(
        f"{k.title()}: {v} (weight {weights_used[k]})" for k, v in component_scores.items()
    )
    if missing:
        explanation += f" | Missing: {', '.join(missing)} (weight redistributed)"
    if adjusted_from:
        explanation += f" | Band adjusted down from {adjusted_from} due to weak: {', '.join(weak)}"

    logger.info(f"HR interview score: {final_score}/100, band={band}, turns={total_turns}")

    return {
        "hr_interview_score": final_score,
        "component_scores": component_scores,
        "weights_used": weights_used,
        "turns_scored": total_turns,
        "missing_components": missing,
        "weak_components": weak,
        "performance_band": band,
        "band_adjusted_from": adjusted_from,
        "explanation": explanation,
    }