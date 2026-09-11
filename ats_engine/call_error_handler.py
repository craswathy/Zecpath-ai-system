from utils.logger import logger


def classify_answer_event(stt_result, intent_result):
    """
    Given Day 24's STT result and Day 25's intent/off-topic detection,
    classify what event the state machine (Day 29) should react to.
    """
    if not stt_result.get("text", "").strip():
        return "silence_detected"

    if stt_result.get("confidence", 1.0) < 0.4:
        return "low_confidence_transcription"

    if intent_result.get("is_off_topic"):
        return "off_topic_detected"

    if intent_result.get("structured_answer", {}).get("is_vague_or_missing"):
        return "vague_answer"

    return "answer_received_ok"


def should_end_call(state_machine, consecutive_failures_threshold=3):
    """
    Decide whether the call should be ended early due to repeated failures
    (e.g. candidate consistently silent or giving off-topic answers across
    multiple questions, not just one).
    """
    recent_events = [h["event"] for h in state_machine.history[-consecutive_failures_threshold:]]
    failure_events = {"silence_detected", "off_topic_detected", "vague_answer", "low_confidence_transcription"}

    if len(recent_events) >= consecutive_failures_threshold and all(e in failure_events for e in recent_events):
        logger.warning(f"[{state_machine.call_id}] Ending call early -- {consecutive_failures_threshold} consecutive failures")
        return True
    return False