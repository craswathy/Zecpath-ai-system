import sys
sys.path.append(".")
from ats_engine.pause_repetition_detector import detect_long_pause, detect_repeated_words
from ats_engine.contradiction_detector import detect_numeric_contradiction
from ats_engine.stress_indicator import compute_stress_score

def test_detect_long_pause():
    result = detect_long_pause(word_count=5, duration_seconds=15)
    assert result["long_pause_detected"] is True

def test_detect_no_long_pause():
    result = detect_long_pause(word_count=10, duration_seconds=5)
    assert result["long_pause_detected"] is False

def test_detect_repeated_words():
    result = detect_repeated_words("I I I have three years of experience")
    assert result["repetition_count"] >= 1

def test_numeric_contradiction_detected():
    result = detect_numeric_contradiction(3, 7)
    assert result["contradiction"] is True

def test_numeric_contradiction_within_tolerance():
    result = detect_numeric_contradiction(3, 3.5)
    assert result["contradiction"] is False

def test_stress_score_range():
    score = compute_stress_score(2, True, 1, "negative", True)
    assert 0 <= score <= 1