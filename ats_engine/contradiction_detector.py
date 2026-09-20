from utils.logger import logger


def detect_numeric_contradiction(value_a, value_b, tolerance=1.0):
    """
    Compare two numeric values stated at different points in a conversation
    (e.g. years of experience mentioned twice). Generalizes the logic
    used in Day 26's score_consistency, reusable across any numeric field.
    """
    if value_a is None or value_b is None:
        return {"contradiction": False, "difference": None}

    difference = abs(value_a - value_b)
    contradiction = difference > tolerance

    return {"contradiction": contradiction, "difference": round(difference, 1)}


def detect_categorical_contradiction(value_a, value_b):
    """
    Compare two categorical/text answers on the same topic (e.g. said
    'yes' to relocating, then later implied unwillingness).
    """
    if value_a is None or value_b is None:
        return {"contradiction": False}
    return {"contradiction": str(value_a).strip().lower() != str(value_b).strip().lower()}


def scan_for_contradictions(answer_history, field_key):
    """
    Scan a candidate's full answer history for a given extracted field
    (e.g. 'experience_years') and flag any pairwise contradictions found
    across the whole conversation, not just adjacent turns.
    """
    values = [
        (a["turn_id"], a["structured_answer"]["extracted_value"])
        for a in answer_history
        if a["structured_answer"].get("extracted_value") is not None
    ]

    contradictions = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            turn_a, val_a = values[i]
            turn_b, val_b = values[j]
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                result = detect_numeric_contradiction(val_a, val_b)
            else:
                result = detect_categorical_contradiction(val_a, val_b)

            if result["contradiction"]:
                contradictions.append({"turn_a": turn_a, "turn_b": turn_b, "field": field_key, **result})

    if contradictions:
        logger.info(f"Found {len(contradictions)} contradiction(s) in field '{field_key}'")
    return contradictions