from utils.logger import logger

STRESS_WEIGHTS = {
    "hesitation": 0.25,
    "pause": 0.20,
    "repetition": 0.20,
    "negative_sentiment": 0.15,
    "contradiction": 0.20,
}


def compute_stress_score(hesitation_count, long_pause_detected, repetition_count,
                          sentiment_label, has_contradiction):
    """
    Combine multiple stress-adjacent signals into one 0-1 stress indicator.
    Higher score = more stress signals present. This is a signal for
    human review, not a pass/fail judgment -- stress during an interview
    doesn't necessarily reflect poor candidate quality.
    """
    hesitation_component = min(1.0, hesitation_count * 0.2)
    pause_component = 1.0 if long_pause_detected else 0.0
    repetition_component = min(1.0, repetition_count * 0.3)
    sentiment_component = 1.0 if sentiment_label == "negative" else 0.0
    contradiction_component = 1.0 if has_contradiction else 0.0

    stress_score = (
        hesitation_component * STRESS_WEIGHTS["hesitation"]
        + pause_component * STRESS_WEIGHTS["pause"]
        + repetition_component * STRESS_WEIGHTS["repetition"]
        + sentiment_component * STRESS_WEIGHTS["negative_sentiment"]
        + contradiction_component * STRESS_WEIGHTS["contradiction"]
    )

    logger.info(f"Stress score computed: {round(stress_score, 2)}")
    return round(stress_score, 2)


def compute_behavioral_confidence_score(confidence_result, stress_score):
    """
    Final behavioral confidence score (0-100): Day 27's base confidence
    indicator, reduced by the Day 36 stress score. High stress pulls
    confidence down even if the raw content of the answer was fine.
    """
    base_confidence = confidence_result["confidence_score"]
    adjusted = max(0.0, base_confidence - (stress_score * 0.4))
    final_score = round(adjusted * 100, 1)

    return {
        "behavioral_confidence_score": final_score,
        "base_confidence": base_confidence,
        "stress_score": stress_score,
    }