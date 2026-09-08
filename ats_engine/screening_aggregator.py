from utils.logger import logger

# Some question categories matter more for the overall screening decision
CATEGORY_IMPORTANCE_WEIGHTS = {
    "Experience": 1.5,
    "Skills": 1.5,
    "Introduction": 0.5,
    "Education": 1.0,
    "Location": 0.75,
    "Salary": 0.75,
    "Notice Period": 0.5,
}
DEFAULT_IMPORTANCE = 1.0


def normalize_scores(per_question_scores):
    """
    Min-max normalize weighted scores across all questions in a call,
    so the final aggregate isn't skewed by one unusually easy/hard question.
    """
    scores = [q["weighted_score"] for q in per_question_scores]
    if not scores:
        return per_question_scores

    min_s, max_s = min(scores), max(scores)
    spread = max_s - min_s

    for q in per_question_scores:
        if spread == 0:
            q["normalized_score"] = q["weighted_score"]  # all identical, keep as-is
        else:
            q["normalized_score"] = round((q["weighted_score"] - min_s) / spread, 2)

    return per_question_scores


def aggregate_screening_score(per_question_scores):
    """
    Combine all per-question scores into one final screening score (0-100),
    weighting each question's category by importance.
    """
    if not per_question_scores:
        return {"final_screening_score": 0.0, "explanation": "No answers to score."}

    total_weighted = 0.0
    total_importance = 0.0

    for q in per_question_scores:
        importance = CATEGORY_IMPORTANCE_WEIGHTS.get(q["question_category"], DEFAULT_IMPORTANCE)
        total_weighted += q["weighted_score"] * importance
        total_importance += importance

    final_score = round((total_weighted / total_importance) * 100, 1) if total_importance else 0.0

    breakdown = [
        f"{q['question_category']}: {q['weighted_score']} (importance {CATEGORY_IMPORTANCE_WEIGHTS.get(q['question_category'], DEFAULT_IMPORTANCE)}x)"
        for q in per_question_scores
    ]

    logger.info(f"Final aggregated screening score: {final_score}/100")

    return {
        "final_screening_score": final_score,
        "questions_scored": len(per_question_scores),
        "explanation": " | ".join(breakdown),
    }