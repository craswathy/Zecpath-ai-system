from utils.logger import logger


def identify_hr_strengths(hr_score_result, aptitude_results, communication_data):
    """Pull out what went well across HR score components, aptitude, and communication."""
    strengths = []

    for component, score in hr_score_result.get("component_scores", {}).items():
        if score >= 0.75:
            strengths.append(f"Strong {component} throughout the interview")

    correct_aptitude = [r for r in aptitude_results if r.get("correct") is True]
    if len(correct_aptitude) >= 2:
        strengths.append(f"Solid logical reasoning -- {len(correct_aptitude)} reasoning question(s) answered correctly")

    high_coverage = [r for r in aptitude_results if r.get("coverage_score", 0) >= 0.7]
    if high_coverage:
        strengths.append("Situational judgment responses covered key reasoning points well")

    avg_comm = sum(c["communication_score"] for c in communication_data) / len(communication_data) if communication_data else 0
    if avg_comm >= 75:
        strengths.append("Clear, well-structured communication throughout")

    return strengths if strengths else ["No standout strengths identified in this interview"]


def identify_hr_weaknesses(hr_score_result, aptitude_results, communication_data):
    """Identify weak spots -- low component scores, missed reasoning, poor communication."""
    weaknesses = []

    for component, score in hr_score_result.get("component_scores", {}).items():
        if score < 0.5:
            weaknesses.append(f"Weak {component} observed during the interview")

    incorrect_aptitude = [r for r in aptitude_results if r.get("correct") is False]
    if incorrect_aptitude:
        weaknesses.append(f"{len(incorrect_aptitude)} logical reasoning question(s) answered incorrectly")

    low_coverage = [r for r in aptitude_results if "coverage_score" in r and r["coverage_score"] < 0.4]
    if low_coverage:
        weaknesses.append("Situational judgment responses missed key reasoning elements")

    avg_comm = sum(c["communication_score"] for c in communication_data) / len(communication_data) if communication_data else 0
    if avg_comm < 50:
        weaknesses.append("Communication clarity below expected standard")

    return weaknesses if weaknesses else ["No significant weaknesses identified"]


def identify_cultural_fit_indicators(aptitude_results, confidence_stress_data):
    """
    Extract signals relevant to teamwork/culture fit -- situational
    judgment responses (Day 38) that touch on collaboration, plus
    overall behavioral stability (Day 36) as a rough proxy.
    """
    indicators = []

    sjt_results = [r for r in aptitude_results if r.get("type") == "situational_judgment"]
    collaborative_responses = [
        r for r in sjt_results
        if any("communication" in e for e in r.get("elements_covered", []))
    ]
    if collaborative_responses:
        indicators.append("Demonstrated collaborative problem-solving approach in scenario questions")

    avg_stress = (
        sum(c["stress_score"] for c in confidence_stress_data) / len(confidence_stress_data)
        if confidence_stress_data else 0
    )
    if avg_stress < 0.3:
        indicators.append("Calm, composed demeanor under interview conditions")
    elif avg_stress > 0.6:
        indicators.append("Elevated stress signals observed -- may warrant a follow-up conversation in a lower-pressure setting")

    return indicators if indicators else ["Insufficient data to assess cultural fit indicators"]


def identify_risk_flags(hr_score_result, confidence_stress_data, contradiction_count):
    """Surface risk signals a recruiter should specifically know about."""
    risks = []

    if contradiction_count > 0:
        risks.append(f"{contradiction_count} contradiction(s) detected across interview responses -- review for consistency")

    if hr_score_result.get("score_reliability") == "low_reliability":
        risks.append(f"Score based on limited data ({hr_score_result.get('turns_scored', 0)} turns) -- interpret with caution")

    negative_sentiment_turns = sum(1 for c in confidence_stress_data if c.get("sentiment", {}).get("label") == "negative")
    if negative_sentiment_turns > 0:
        risks.append(f"Negative tone detected in {negative_sentiment_turns} response(s)")

    return risks if risks else ["No significant risk flags identified"]


def summarize_overall_hr_performance(hr_score_result):
    """One-line overall performance summary based on the final HR score."""
    score = hr_score_result.get("hr_interview_score", 0)
    if score >= 75:
        return "Strong overall HR interview performance."
    elif score >= 50:
        return "Adequate HR interview performance with some areas for improvement."
    else:
        return "Below-expectation HR interview performance -- recommend detailed manual review."