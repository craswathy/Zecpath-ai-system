import sys
sys.path.append(".")
from ats_engine.speech_quality_checker import detect_silence_or_empty, detect_partial_answer, assess_response_quality

def test_detect_silence():
    assert detect_silence_or_empty({"text": ""}) is True
    assert detect_silence_or_empty({"text": "hello there"}) is False

def test_detect_partial_answer():
    assert detect_partial_answer({"text": "yes I"}) is True
    assert detect_partial_answer({"text": "I have three years of experience in this field"}) is False

def test_assess_quality_low_confidence():
    result = assess_response_quality({"text": "some answer here", "confidence": 0.3})
    assert result == "low_confidence"

def test_assess_quality_ok():
    result = assess_response_quality({"text": "I have three years of experience", "confidence": 0.9})
    assert result == "ok"