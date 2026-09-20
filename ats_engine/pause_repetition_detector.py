import re
from utils.logger import logger

# Expected speaking rate for typical conversational English (words per second).
# Used to estimate whether a turn's duration implies pauses beyond normal speech.
EXPECTED_WORDS_PER_SECOND = 2.0


def detect_long_pause(word_count, duration_seconds):
    """
    Estimate whether a turn's duration implies unusually long pauses,
    by comparing actual duration to the expected time for that many
    words at a normal speaking rate. This is a turn-level proxy --
    true pause detection would need word-level timestamps, which
    aren't available from Whisper's basic output (Day 24).
    """
    if not duration_seconds or word_count == 0:
        return {"long_pause_detected": False, "estimated_pause_seconds": 0.0}

    expected_duration = word_count / EXPECTED_WORDS_PER_SECOND
    excess_duration = duration_seconds - expected_duration

    long_pause = excess_duration > 3.0  # more than 3s beyond expected speaking time
    return {
        "long_pause_detected": long_pause,
        "estimated_pause_seconds": round(max(0.0, excess_duration), 1),
    }


def detect_repeated_words(text):
    """
    Detect literal word-repetition patterns (e.g. 'I I I have', 'the the
    project') -- a distinct stress/hesitation signal from filler words
    (Day 27), often indicating the speaker restarting a thought mid-sentence.
    """
    if not text:
        return {"repetition_count": 0, "repeated_phrases": []}

    pattern = re.compile(r'\b(\w+)(\s+\1\b)+', re.IGNORECASE)
    matches = pattern.findall(text)
    repeated_phrases = [m[0] for m in matches]

    return {
        "repetition_count": len(repeated_phrases),
        "repeated_phrases": repeated_phrases,
    }