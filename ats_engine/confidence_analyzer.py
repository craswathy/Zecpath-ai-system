import re
from utils.logger import logger

HESITATION_MARKERS = [
    r"\bum+\b", r"\buh+\b", r"\ber+\b", r"\bhmm+\b",
    r"\bi think\b", r"\bmaybe\b", r"\bprobably\b", r"\bi guess\b",
    r"\bnot sure\b", r"\bkind of\b", r"\bsort of\b",
]

UNCERTAINTY_PHRASES = [
    r"\bi don'?t know\b", r"\bnot certain\b", r"\bcould be wrong\b",
    r"\bi'?m not sure\b", r"\bpossibly\b",
]


def count_hesitation_markers(raw_answer_text):
    """
    Count hesitation markers in the RAW (pre-cleaned) transcript text --
    this must run before Day 23's filler-word removal, since that
    normalization strips exactly these signals.
    """
    text_lower = raw_answer_text.lower()
    count = 0
    for pattern in HESITATION_MARKERS:
        count += len(re.findall(pattern, text_lower))
    return count


def measure_response_pace(word_count, duration_seconds):
    """
    Words per second -- a rough pace indicator. Very slow pace can signal
    hesitation/uncertainty; very fast pace can signal rehearsed or
    nervous rushed speech. Returns pace value and a qualitative label.
    """
    if not duration_seconds or duration_seconds == 0:
        return {"words_per_second": None, "pace_label": "unknown"}

    wps = round(word_count / duration_seconds, 2)

    if wps < 1.0:
        label = "slow (may indicate hesitation)"
    elif wps > 3.0:
        label = "fast (may indicate rushing or rehearsal)"
    else:
        label = "normal"

    return {"words_per_second": wps, "pace_label": label}


def detect_uncertainty(raw_answer_text):
    """Flag explicit uncertainty language in the response."""
    text_lower = raw_answer_text.lower()
    for pattern in UNCERTAINTY_PHRASES:
        if re.search(pattern, text_lower):
            return True
    return False


def compute_confidence_indicator(raw_answer_text, word_count, duration_seconds, stt_confidence):
    """
    Combine hesitation markers, pace, uncertainty language, and STT
    confidence (Day 24) into one 0-1 communication confidence score.
    """
    hesitation_count = count_hesitation_markers(raw_answer_text)
    pace_info = measure_response_pace(word_count, duration_seconds)
    uncertain = detect_uncertainty(raw_answer_text)

    # Start from STT confidence (how clearly they spoke), then penalize
    # for hesitation markers and explicit uncertainty language
    score = stt_confidence
    score -= min(0.3, hesitation_count * 0.1)  # each hesitation marker costs up to 0.3 total
    if uncertain:
        score -= 0.15
    if pace_info["pace_label"] != "normal":
        score -= 0.05

    score = round(max(0.0, min(1.0, score)), 2)

    logger.info(f"Confidence indicator: {score} (hesitations={hesitation_count}, uncertain={uncertain})")

    return {
        "confidence_score": score,
        "hesitation_count": hesitation_count,
        "uncertainty_detected": uncertain,
        "pace": pace_info,
    }