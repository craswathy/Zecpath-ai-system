import re
from utils.logger import logger

# Common patterns that suggest language mixing (code-switching) --
# e.g. an answer that's mostly English but has Malayalam/Hindi words
# transliterated, which Whisper sometimes partially transcribes or garbles
CODE_SWITCH_INDICATORS = [
    r"\bank\b.*\bank\b",  # repeated fragments often signal STT confusion
    r"[a-z]{1,2}\s[a-z]{1,2}\s[a-z]{1,2}\b",  # unusually short choppy words in sequence
]


def detect_poor_audio_quality(stt_result):
    """
    Flag likely poor audio quality based on STT confidence AND
    text characteristics (very short output relative to expected
    speech duration suggests audio was too degraded to transcribe fully).
    """
    confidence = stt_result.get("confidence", 1.0)
    text = stt_result.get("text", "")

    if confidence < 0.4:
        return True, "very_low_confidence"

    if not text.strip() and confidence > 0:
        return True, "empty_despite_signal"

    # heavy repetition of the same short word/fragment often signals
    # the model struggling with noisy/garbled audio
    words = text.lower().split()
    if len(words) > 5:
        most_common_count = max(words.count(w) for w in set(words))
        if most_common_count > len(words) * 0.4:
            return True, "excessive_repetition"

    return False, None


def detect_language_mixing(text, primary_language="en"):
    """
    Heuristic detection of code-switching (mixing languages mid-answer).
    A full solution needs language-ID per word; this flags likely cases
    for human review rather than claiming certainty.
    """
    if not text:
        return False

    for pattern in CODE_SWITCH_INDICATORS:
        if re.search(pattern, text.lower()):
            logger.info("Possible language mixing detected -- flagged for review")
            return True
    return False


def handle_missing_answer(question_id, retry_count, max_retries=2):
    """
    Decide what to do when no usable answer was captured at all
    (distinct from Day 29's vague/off-topic handling -- this is
    total absence of any signal, e.g. dead air or call issue).
    """
    if retry_count < max_retries:
        return {"action": "retry", "message": "We didn't receive your response -- could you please answer again?"}
    else:
        return {"action": "mark_unanswered", "message": None}