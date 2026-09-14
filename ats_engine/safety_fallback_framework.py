from ats_engine.audio_edge_cases import detect_poor_audio_quality, detect_language_mixing, handle_missing_answer
from utils.logger import logger

FALLBACK_PRIORITY = [
    "call_technical_failure",
    "poor_audio_quality",
    "language_mixing",
    "missing_answer",
    "off_topic",
    "vague_answer",
]


def diagnose_turn(stt_result, intent_result, retry_count, call_status="active"):
    """
    Central diagnosis point: given everything known about one turn,
    determine the single highest-priority issue (if any) so the
    conversation state machine (Day 29) has one clear signal to act on,
    rather than juggling multiple overlapping checks itself.
    """
    if call_status == "dropped":
        return "call_technical_failure"

    poor_audio, audio_reason = detect_poor_audio_quality(stt_result)
    if poor_audio:
        logger.warning(f"Poor audio quality: {audio_reason}")
        return "poor_audio_quality"

    if not stt_result.get("text", "").strip():
        return "missing_answer"

    if detect_language_mixing(stt_result.get("text", "")):
        return "language_mixing"

    if intent_result and intent_result.get("is_off_topic"):
        return "off_topic"

    if intent_result and intent_result.get("structured_answer", {}).get("is_vague_or_missing"):
        return "vague_answer"

    return None  # no issue -- answer is usable as-is


def get_safety_response(issue_type, retry_count, max_retries=2):
    """
    Return the appropriate safe, polite fallback action + message for
    a diagnosed issue, respecting retry limits so the system never
    loops indefinitely on a struggling candidate.
    """
    if retry_count >= max_retries:
        return {
            "action": "escalate_to_human_review",
            "message": "Thank you for your patience. We'll have a member of our team follow up with you directly.",
        }

    responses = {
        "call_technical_failure": {
            "action": "end_call_reschedule",
            "message": "It looks like we lost connection. We'll reach out to reschedule this call.",
        },
        "poor_audio_quality": {
            "action": "retry",
            "message": "I'm having trouble hearing you clearly -- could you move to a quieter space and repeat that?",
        },
        "language_mixing": {
            "action": "retry",
            "message": "Could you please answer in English so I can understand you clearly?",
        },
        "missing_answer": {
            "action": "retry",
            "message": "We didn't receive your response -- could you please answer again?",
        },
        "off_topic": {
            "action": "clarify",
            "message": "Let me rephrase the question to make sure I understand what you're asking.",
        },
        "vague_answer": {
            "action": "clarify",
            "message": "Could you give me a bit more detail on that, please?",
        },
    }

    return responses.get(issue_type, {"action": "retry", "message": "Could you please repeat that?"})