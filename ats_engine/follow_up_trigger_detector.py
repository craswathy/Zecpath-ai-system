import re
from utils.logger import logger

SHALLOW_ANSWER_PATTERNS = [
    re.compile(r"^\s*(good|fine|okay|nice)\s*\.?\s*$", re.IGNORECASE),
    re.compile(r"^\s*i (like|enjoy) (it|that|working)\s*\.?\s*$", re.IGNORECASE),
]

CONFIDENCE_PATTERN = re.compile(
    r"\bfor example\b|\bspecifically\b|\bin my experience\b|\bi led\b|\bi built\b|\bi designed\b|\bi solved\b",
    re.IGNORECASE,
)

DIGIT_PATTERN = re.compile(r"\d")
MIN_WORDS_FOR_DEPTH = 12


def needs_clarification(answer_text, is_vague_or_missing):
    """Clarify when Day 25 flagged the answer, or when nothing was said at all."""
    return bool(is_vague_or_missing) or not (answer_text or "").strip()


def needs_deepening(answer_text):
    """
    Deepen when the answer is short and generic. A number counts as specific
    detail (e.g. "3 years"), so concrete short answers are not over-probed.
    """
    text = (answer_text or "").strip()
    if not text:
        return False

    for pattern in SHALLOW_ANSWER_PATTERNS:
        if pattern.match(text):
            return True

    word_count = len(text.split())
    has_confidence_markers = bool(CONFIDENCE_PATTERN.search(text))
    has_specific_detail = bool(DIGIT_PATTERN.search(text))
    return word_count < MIN_WORDS_FOR_DEPTH and not has_confidence_markers and not has_specific_detail


def is_confident_response(answer_text):
    """Detailed, example-backed answers get a scenario-based follow-up."""
    text = answer_text or ""
    word_count = len(text.split())
    return word_count >= MIN_WORDS_FOR_DEPTH and bool(CONFIDENCE_PATTERN.search(text))


def classify_follow_up_need(answer_text, is_vague_or_missing):
    """Returns 'clarification', 'scenario_based', 'deepening', or None."""
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