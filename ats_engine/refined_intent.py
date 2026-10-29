import re
from ats_engine.follow_up_trigger_detector import classify_follow_up_need, CONFIDENCE_PATTERN, DIGIT_PATTERN

STRONG_HEDGE = re.compile(
    r"\bnot (?:very |really |too )?(?:sure|certain)\b|\bi guess\b|\bmaybe\b|\bperhaps\b|\bno idea\b"
    r"|\bi (?:do not|don'?t) know\b|\bkind of\b|\bsort of\b",
    re.IGNORECASE,
)
WEAK_HEDGE = re.compile(r"\bi think\b|\bprobably\b", re.IGNORECASE)


def count_hedges(text):
    """Return (strong, weak) hedge counts."""
    return len(STRONG_HEDGE.findall(text or "")), len(WEAK_HEDGE.findall(text or ""))


def is_concrete(text):
    """A number or an evidence phrase ('for example', 'I built') makes an answer concrete."""
    return bool(DIGIT_PATTERN.search(text or "")) or bool(CONFIDENCE_PATTERN.search(text or ""))


def classify_follow_up_refined(answer_text, is_vague_or_missing, is_off_topic=False):
    """
    Day 42 classifier plus two fixes found in the Day 45 demo:
    - an off-topic answer gets a clarification follow-up
    - a hedged answer without concrete detail gets a clarification follow-up
    Hedged = one strong hedge, or two hedges of any kind. 'I think' alone is not enough.
    """
    if is_off_topic:
        return "clarification"
    result = classify_follow_up_need(answer_text, is_vague_or_missing)
    if result in (None, "deepening") and not is_concrete(answer_text):
        strong, weak = count_hedges(answer_text)
        if strong >= 1 or strong + weak >= 2:
            return "clarification"
    return result