from utils.logger import logger

# Keywords associated with each ideal-answer-structure element --
# a lightweight proxy for checking whether a response touches on the
# expected reasoning points, without needing a full NLP model.
STRUCTURE_KEYWORD_HINTS = {
    "acknowledges the mistake promptly": ["mistake", "error", "wrong", "acknowledge", "admit"],
    "proposes informing relevant stakeholders": ["inform", "tell", "notify", "communicate", "client", "team"],
    "focuses on correction, not blame": ["fix", "correct", "resolve", "solution"],
    "mentions direct communication first": ["talk", "speak", "discuss", "conversation", "ask"],
    "avoids immediately escalating to management": ["before escalating", "first", "directly", "one-on-one"],
    "focuses on understanding root cause": ["why", "reason", "understand", "cause"],
    "communicates the risk clearly": ["risk", "concern", "explain", "flag"],
    "proposes alternatives (reduced scope, phased delivery)": ["alternative", "phase", "reduce scope", "compromise", "instead"],
    "doesn't simply agree or simply refuse": ["however", "but", "while", "although"],
}


def evaluate_scenario_response(response_text, ideal_answer_structure):
    """
    Check how many of the ideal-answer-structure elements are reflected
    in the candidate's response, using keyword-hint proxies for each element.
    Returns a coverage score and which elements were/weren't detected.
    """
    if not response_text or not response_text.strip():
        return {"coverage_score": 0.0, "elements_covered": [], "elements_missing": ideal_answer_structure}

    text_lower = response_text.lower()
    covered = []
    missing = []

    for element in ideal_answer_structure:
        hints = STRUCTURE_KEYWORD_HINTS.get(element, [])
        if any(hint in text_lower for hint in hints):
            covered.append(element)
        else:
            missing.append(element)

    coverage_score = round(len(covered) / len(ideal_answer_structure), 2) if ideal_answer_structure else 0.0

    logger.info(f"Scenario coverage: {len(covered)}/{len(ideal_answer_structure)} elements detected")

    return {
        "coverage_score": coverage_score,
        "elements_covered": covered,
        "elements_missing": missing,
    }


def assess_problem_solving_clarity(response_text):
    """
    Rough proxy for problem-solving clarity: does the response show a
    structured approach (sequencing words like 'first', 'then', 'because')
    rather than a single unstructured statement.
    """
    if not response_text:
        return {"clarity_score": 0.0, "has_structured_reasoning": False}

    text_lower = response_text.lower()
    structure_markers = ["first", "then", "next", "because", "therefore", "so that", "as a result"]
    marker_count = sum(1 for m in structure_markers if m in text_lower)

    has_structure = marker_count >= 1
    clarity_score = round(min(1.0, 0.5 + marker_count * 0.25), 2)

    return {"clarity_score": clarity_score, "has_structured_reasoning": has_structure}