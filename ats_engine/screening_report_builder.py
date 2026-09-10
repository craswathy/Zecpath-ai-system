from utils.logger import logger


def summarize_key_answers(answers_data):
    """Extract the most informative answer per category for a quick-read summary."""
    key_answers = {}
    for answer in answers_data:
        category = answer["question_category"]
        extracted = answer["structured_answer"]["extracted_value"]
        if extracted and not answer["structured_answer"]["is_vague_or_missing"]:
            key_answers[category] = extracted
    return key_answers


def identify_strengths(screening_scores, behavioral_report):
    """Pull out what went well, based on Day 26 scores and Day 27 behavioral signals."""
    strengths = []

    for q in screening_scores["per_question_scores"]:
        if q["weighted_score"] >= 0.8:
            strengths.append(f"Strong, clear response on {q['question_category']}")

    if behavioral_report["call_level_report"]["overall_strength"] == "Strong":
        strengths.append("Confident, clear communication throughout the call")

    if behavioral_report["call_level_report"]["negative_sentiment_turns"] == 0:
        strengths.append("Consistently positive/neutral tone")

    return strengths if strengths else ["No standout strengths identified"]


def identify_risks(screening_scores, behavioral_report, answers_data):
    """Flag risk signals: off-topic answers, low scores, negative sentiment, high hesitation."""
    risks = []

    off_topic_categories = [a["question_category"] for a in answers_data if a["is_off_topic"]]
    if off_topic_categories:
        risks.append(f"Off-topic responses detected for: {', '.join(off_topic_categories)}")

    low_score_categories = [
        q["question_category"] for q in screening_scores["per_question_scores"] if q["weighted_score"] < 0.5
    ]
    if low_score_categories:
        risks.append(f"Weak responses on: {', '.join(low_score_categories)}")

    flag_summary = behavioral_report["call_level_report"].get("flag_summary", {})
    if flag_summary.get("high_hesitation", 0) > 0:
        risks.append(f"High hesitation detected in {flag_summary['high_hesitation']} response(s)")
    if flag_summary.get("expressed_uncertainty", 0) > 0:
        risks.append(f"Uncertainty expressed in {flag_summary['expressed_uncertainty']} response(s)")
    if behavioral_report["call_level_report"]["negative_sentiment_turns"] > 0:
        risks.append(f"Negative tone detected in {behavioral_report['call_level_report']['negative_sentiment_turns']} response(s)")

    return risks if risks else ["No significant risks identified"]


def identify_missing_data(answers_data, expected_categories):
    """Flag any expected question categories that were vague, missing, or never answered."""
    answered_categories = {
        a["question_category"] for a in answers_data
        if not a["structured_answer"]["is_vague_or_missing"]
    }
    missing = [cat for cat in expected_categories if cat not in answered_categories]
    return missing


def extract_highlight_fields(answers_data):
    """Pull out the three fields recruiters care about most, front and center."""
    highlights = {"salary_expectation": None, "availability": None, "skills_confirmed": []}

    for answer in answers_data:
        category = answer["question_category"]
        value = answer["structured_answer"]["extracted_value"]
        if category == "Salary" and value:
            highlights["salary_expectation"] = f"{value} LPA"
        elif category in ("Location", "Notice Period") and value:
            highlights["availability"] = value
        elif category == "Skills" and value:
            highlights["skills_confirmed"] = value

    return highlights


def build_screening_report(candidate_id, job_id, answers_data, screening_scores, behavioral_report):
    """
    Assemble the full recruiter-facing screening report, combining
    Day 25 (answers), Day 26 (scores), and Day 27 (behavioral) outputs.
    """
    expected_categories = ["Introduction", "Education", "Experience", "Skills", "Location", "Salary", "Notice Period"]

    report = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "final_screening_score": screening_scores["final_screening_score"]["final_screening_score"],
        "overall_communication_strength": behavioral_report["call_level_report"]["overall_strength"],
        "key_answers": summarize_key_answers(answers_data),
        "highlights": extract_highlight_fields(answers_data),
        "strengths": identify_strengths(screening_scores, behavioral_report),
        "risks": identify_risks(screening_scores, behavioral_report, answers_data),
        "missing_data": identify_missing_data(answers_data, expected_categories),
    }

    logger.info(f"Built screening report for {candidate_id}: score={report['final_screening_score']}")
    return report