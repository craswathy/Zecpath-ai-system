from utils.logger import logger


def build_communication_strength_indicator(confidence_result, sentiment_result):
    """
    Combine confidence and sentiment into one qualitative communication
    strength label for a single answer.
    """
    confidence_score = confidence_result["confidence_score"]
    sentiment_label = sentiment_result["label"]

    if confidence_score >= 0.75 and sentiment_label != "negative":
        strength = "Strong"
    elif confidence_score >= 0.5:
        strength = "Moderate"
    else:
        strength = "Weak"

    flags = []
    if confidence_result["hesitation_count"] > 2:
        flags.append("high_hesitation")
    if confidence_result["uncertainty_detected"]:
        flags.append("expressed_uncertainty")
    if sentiment_label == "negative":
        flags.append("negative_tone")
    if confidence_result["pace"]["pace_label"] != "normal":
        flags.append("unusual_pace")

    return {
        "communication_strength": strength,
        "flags": flags,
    }


def build_call_level_report(per_turn_indicators):
    """
    Aggregate per-turn behavioral indicators into one overall call-level
    behavioral summary.
    """
    if not per_turn_indicators:
        return {"overall_strength": "Unknown", "summary": "No data available."}

    avg_confidence = sum(t["confidence"]["confidence_score"] for t in per_turn_indicators) / len(per_turn_indicators)
    negative_count = sum(1 for t in per_turn_indicators if t["sentiment"]["label"] == "negative")
    total_flags = [f for t in per_turn_indicators for f in t["indicator"]["flags"]]

    if avg_confidence >= 0.75:
        overall = "Strong"
    elif avg_confidence >= 0.5:
        overall = "Moderate"
    else:
        overall = "Weak"

    logger.info(f"Call-level behavioral report: overall={overall}, avg_confidence={round(avg_confidence, 2)}")

    return {
        "overall_strength": overall,
        "average_confidence_score": round(avg_confidence, 2),
        "negative_sentiment_turns": negative_count,
        "total_turns_analyzed": len(per_turn_indicators),
        "flag_summary": {flag: total_flags.count(flag) for flag in set(total_flags)},
    }