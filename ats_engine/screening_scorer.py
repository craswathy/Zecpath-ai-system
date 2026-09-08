from utils.logger import logger

# Each parameter scored 0-1, then combined with weights below.
SCORING_WEIGHTS = {
    "clarity": 0.25,
    "relevance": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
}


def score_clarity(answer_text, response_confidence):
    """
    Clarity reflects how well-formed and understandable the answer was.
    Combines STT confidence (Day 24) with basic sentence structure signals.
    """
    if not answer_text or not answer_text.strip():
        return 0.0

    word_count = len(answer_text.split())
    structure_score = min(1.0, word_count / 15)  # very short answers score lower on clarity

    # response_confidence comes from Whisper (Day 24) -- low confidence
    # transcription often correlates with unclear/mumbled speech
    combined = (structure_score * 0.5) + (response_confidence * 0.5)
    return round(min(1.0, combined), 2)


def score_relevance(is_off_topic, detected_intents):
    """
    Relevance reflects whether the answer actually addressed the question
    asked, using Day 25's intent classification and off-topic detection.
    """
    if is_off_topic:
        return 0.1
    if "refusal_or_unclear" in detected_intents:
        return 0.3
    if "unclassified" in detected_intents:
        return 0.5
    return 1.0


def score_completeness(is_vague_or_missing, extracted_value):
    """
    Completeness reflects whether the answer actually provided the
    specific information the question needed (Day 25's extraction result).
    """
    if is_vague_or_missing:
        return 0.0
    if extracted_value is None or extracted_value == []:
        return 0.4  # answered, but couldn't extract the specific fact needed
    return 1.0


def score_consistency(current_answer_value, previously_stated_value):
    """
    Consistency checks whether this answer contradicts something the
    candidate said earlier in the same call (e.g. stated 3 years experience
    in one answer, then implied 6 years in another).
    Returns 1.0 if no conflict or nothing to compare against, lower if conflicting.
    """
    if previously_stated_value is None or current_answer_value is None:
        return 1.0  # nothing to compare, assume consistent

    if isinstance(current_answer_value, (int, float)) and isinstance(previously_stated_value, (int, float)):
        difference = abs(current_answer_value - previously_stated_value)
        if difference == 0:
            return 1.0
        elif difference <= 1:
            return 0.7  # minor discrepancy, could be rounding
        else:
            return 0.2  # significant contradiction

    return 1.0 if current_answer_value == previously_stated_value else 0.4


def score_answer(answer_data, response_confidence, previously_stated_value=None):
    """
    Combine all four scoring parameters for one answer into a single
    explainable per-question score.

    answer_data: one entry from Day 25's answer_understanding_result.json
    """
    clarity = score_clarity(answer_data["structured_answer"]["raw_answer"], response_confidence)
    relevance = score_relevance(answer_data["is_off_topic"], answer_data["detected_intents"])
    completeness = score_completeness(
        answer_data["structured_answer"]["is_vague_or_missing"],
        answer_data["structured_answer"]["extracted_value"],
    )
    consistency = score_consistency(
        answer_data["structured_answer"]["extracted_value"], previously_stated_value
    )

    weighted_score = (
        clarity * SCORING_WEIGHTS["clarity"]
        + relevance * SCORING_WEIGHTS["relevance"]
        + completeness * SCORING_WEIGHTS["completeness"]
        + consistency * SCORING_WEIGHTS["consistency"]
    )

    logger.info(f"Scored answer for {answer_data['question_category']}: {round(weighted_score, 2)}")

    return {
        "turn_id": answer_data["turn_id"],
        "question_category": answer_data["question_category"],
        "component_scores": {
            "clarity": clarity,
            "relevance": relevance,
            "completeness": completeness,
            "consistency": consistency,
        },
        "weighted_score": round(weighted_score, 2),
        "explanation": (
            f"Clarity: {clarity} (25%) | Relevance: {relevance} (30%) | "
            f"Completeness: {completeness} (25%) | Consistency: {consistency} (20%)"
        ),
    }