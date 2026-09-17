import re
from utils.logger import logger

# Signals that a response, while not fully vague (Day 25's is_vague_or_missing
# already catches those), still lacks depth or specificity worth probing.
SHALLOW_ANSWER_INDICATORS = [
    r"^\s*(good|fine|okay|nice)\s*\.?\s*$",
    r"^\s*i (like|enjoy) (it|that|working)\s*\.?\s*$",
]

CONFIDENCE_INDICATORS = [
    r"\bfor example\b", r"\bspecifically\b", r"\bin my experience\b",
    r"\bi led\b", r"\bi built\b", r"\bi designed\b", r"\bi solved\b",
]

MIN_WORDS_FOR_DEPTH = 12


def needs_clarification(answer_text, is_vague_or_missing):
    """
    Trigger a clarification follow-up when Day 25 already flagged the
    answer as vague/missing, or STT confidence made the meaning unclear.
    """
    return bool(is_vague_or_missing)


def needs_deepening(answer_text):
    """
    Trigger a deepening follow-up when the answer is coherent and on-topic
    but shallow -- short, generic, no specific detail -- distinct from a
    genuinely vague/missing answer.
    """
    text = answer_text.strip()
    if not text:
        return False

    for pattern in SHALLOW_ANSWER_INDICATORS:
        if re.match(pattern, text, re.IGNORECASE):
            return True

    word_count = len(text.split())
    has_confidence_markers = any(re.search(p, text.lower()) for p in CONFIDENCE_INDICATORS)

    return word_count < MIN_WORDS_FOR_DEPTH and not has_confidence_markers


def is_confident_response(answer_text):
    """
    Detect a strong, detailed, example-backed answer -- these are
    candidates for a scenario-based follow-up rather than a basic probe,
    since the candidate has already shown depth.
    """
    text_lower = answer_text.lower()
    word_count = len(answer_text.split())
    has_confidence_markers = any(re.search(p, text_lower) for p in CONFIDENCE_INDICATORS)
    return word_count >= MIN_WORDS_FOR_DEPTH and has_confidence_markers


def classify_follow_up_need(answer_text, is_vague_or_missing):
    """
    Single entry point: classify what kind of follow-up (if any) this
    answer warrants. Returns one of: 'clarification', 'deepening',
    'scenario_based', or None (no follow-up needed).
    """
    if needs_clarification(answer_text, is_vague_or_missing):
        result = "clarification"
    elif is_confident_response(answer_text):
        result = "scenario_based"
    elif needs_deepening(answer_text):
        result = "deepening"
    else:
        result = None

    logger.info(f"Follow-up classification: {result}")
    return result