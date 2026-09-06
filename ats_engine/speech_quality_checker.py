from utils.logger import logger

MIN_WORD_COUNT_FOR_COMPLETE_ANSWER = 3


def detect_silence_or_empty(transcription_result):
    """Flag if a transcription came back empty or near-empty -- likely silence."""
    text = transcription_result.get("text", "")
    if not text or len(text.strip()) == 0:
        return True
    return False


def detect_partial_answer(transcription_result):
    """
    Heuristic: very short responses to a free_text question likely indicate
    an interrupted or partial answer rather than a genuine complete response.
    """
    text = transcription_result.get("text", "")
    word_count = len(text.split())
    return word_count < MIN_WORD_COUNT_FOR_COMPLETE_ANSWER and word_count > 0


def assess_response_quality(transcription_result):
    """Combine checks into one quality flag for downstream handling."""
    if detect_silence_or_empty(transcription_result):
        flag = "silence_detected"
    elif detect_partial_answer(transcription_result):
        flag = "partial_answer"
    elif transcription_result.get("confidence", 0) < 0.5:
        flag = "low_confidence"
    else:
        flag = "ok"

    logger.info(f"Response quality assessment: {flag}")
    return flag