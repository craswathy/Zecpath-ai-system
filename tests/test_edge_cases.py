import sys
sys.path.append(".")
from ats_engine.audio_edge_cases import detect_poor_audio_quality, handle_missing_answer
from ats_engine.safety_fallback_framework import diagnose_turn, get_safety_response

def test_detect_poor_audio_low_confidence():
    flagged, reason = detect_poor_audio_quality({"text": "some text", "confidence": 0.2})
    assert flagged is True
    assert reason == "very_low_confidence"

def test_detect_poor_audio_clear():
    flagged, reason = detect_poor_audio_quality({"text": "I have three years of experience", "confidence": 0.9})
    assert flagged is False

def test_handle_missing_answer_retries():
    result = handle_missing_answer("q1", retry_count=0, max_retries=2)
    assert result["action"] == "retry"

def test_handle_missing_answer_gives_up():
    result = handle_missing_answer("q1", retry_count=2, max_retries=2)
    assert result["action"] == "mark_unanswered"

def test_diagnose_turn_call_dropped():
    issue = diagnose_turn({}, {}, 0, call_status="dropped")
    assert issue == "call_technical_failure"

def test_diagnose_turn_clean_answer():
    issue = diagnose_turn(
        {"text": "I have three years of experience", "confidence": 0.9},
        {"is_off_topic": False, "structured_answer": {"is_vague_or_missing": False}},
        0,
    )
    assert issue is None

def test_get_safety_response_escalates_after_max_retries():
    response = get_safety_response("missing_answer", retry_count=2, max_retries=2)
    assert response["action"] == "escalate_to_human_review"