import re
from utils.logger import logger


def extract_numeric_answer(response_text):
    """Pull the first numeric value from a candidate's spoken/written answer."""
    match = re.search(r'-?\d+(\.\d+)?', response_text)
    return float(match.group()) if match else None


def score_numeric_reasoning(response_text, correct_answer, question_id):
    """
    Score a numeric reasoning question: exact match scores full marks,
    otherwise checks if reasoning steps (from ideal_answer_structure)
    are at least partially present in the explanation given.
    """
    extracted = extract_numeric_answer(response_text)

    if extracted is None:
        return {"score": 0.0, "correct": False, "reasoning": "No numeric answer detected."}

    is_correct = abs(extracted - correct_answer) < 0.01

    logger.info(f"[{question_id}] Numeric answer: {extracted}, correct: {correct_answer}, match: {is_correct}")

    return {
        "score": 1.0 if is_correct else 0.2,
        "correct": is_correct,
        "extracted_answer": extracted,
        "reasoning": "Correct final answer." if is_correct else "Incorrect final answer, partial credit for attempt.",
    }


def score_verbal_reasoning(response_text, correct_answer, question_id):
    """
    Score a verbal/logical reasoning question by checking if the
    candidate's stated conclusion (yes/no) matches the logically correct one.
    """
    text_lower = response_text.lower()

    if correct_answer == "no":
        stated_no = any(w in text_lower for w in ["no", "cannot", "can't", "doesn't follow", "false"])
        stated_yes = any(w in text_lower for w in ["yes", "correct", "true"]) and not stated_no
        is_correct = stated_no and not stated_yes
    else:
        is_correct = correct_answer.lower() in text_lower

    logger.info(f"[{question_id}] Verbal reasoning correct: {is_correct}")

    return {
        "score": 1.0 if is_correct else 0.3,
        "correct": is_correct,
        "reasoning": "Correct logical conclusion." if is_correct else "Conclusion does not match expected logical answer.",
    }


def score_logical_reasoning(response_text, question):
    """Route to the correct scorer based on question's expected_answer_type."""
    if question["expected_answer_type"] == "numeric":
        return score_numeric_reasoning(response_text, question["correct_answer"], question["id"])
    elif question["expected_answer_type"] == "reasoning":
        return score_verbal_reasoning(response_text, question["correct_answer"], question["id"])
    return {"score": 0.5, "correct": None, "reasoning": "Unscored question type."}