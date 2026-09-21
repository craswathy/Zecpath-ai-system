from ats_engine.hr_scoring_config import get_hr_weights
from utils.logger import logger


def score_relevance_for_turn(is_off_topic, is_vague_or_missing):
    """
    Relevance score for one HR interview answer -- reuses the same
    logic pattern as Day 26's screening relevance scoring.
    """
    if is_off_topic:
        return 0.1
    if is_vague_or_missing:
        return 0.3
    return 1.0


def score_consistency_for_candidate(contradiction_count, total_turns):
    """
    Consistency across the whole interview -- inverse of contradiction
    density (Day 36's contradiction detector), not per-turn since
    contradictions only make sense across multiple answers.
    """
    if total_turns == 0:
        return 1.0
    contradiction_rate = contradiction_count / total_turns
    return round(max(0.0, 1.0 - contradiction_rate * 2), 2)


def compute_hr_interview_score(per_turn_data, contradiction_count, role_category=None):
    """
    Combine relevance, communication, confidence, and consistency into
    one explainable HR interview score (0-100).

    per_turn_data: list of dicts, each with keys:
      is_off_topic, is_vague_or_missing (from Day 25 pattern),
      communication_score (Day 35, 0-100 scale),
      behavioral_confidence_score (Day 36, 0-100 scale)
    """
    weights = get_hr_weights(role_category)
    total_turns = len(per_turn_data)

    if total_turns == 0:
        return {
            "hr_interview_score": 0.0,
            "component_scores": {},
            "explanation": "No interview responses to score.",
        }

    relevance_scores = [
        score_relevance_for_turn(t["is_off_topic"], t["is_vague_or_missing"])
        for t in per_turn_data
    ]
    avg_relevance = round(sum(relevance_scores) / total_turns, 2)

    avg_communication = round(
        sum(t["communication_score"] for t in per_turn_data) / total_turns / 100, 2
    )
    avg_confidence = round(
        sum(t["behavioral_confidence_score"] for t in per_turn_data) / total_turns / 100, 2
    )
    consistency = score_consistency_for_candidate(contradiction_count, total_turns)

    component_scores = {
        "relevance": avg_relevance,
        "communication": avg_communication,
        "confidence": avg_confidence,
        "consistency": consistency,
    }

    final_score = sum(component_scores[k] * weights[k] for k in weights)
    final_score = round(final_score * 100, 1)

    explanation = " | ".join(
        f"{k.title()}: {v} (weight {weights[k]})" for k, v in component_scores.items()
    )

    logger.info(f"HR interview score: {final_score}/100 across {total_turns} turns")

    return {
        "hr_interview_score": final_score,
        "component_scores": component_scores,
        "weights_used": weights,
        "turns_scored": total_turns,
        "explanation": explanation,
    }