import sys
sys.path.append(".")
from ats_engine.confidence_analyzer import count_hesitation_markers, measure_response_pace, detect_uncertainty
from ats_engine.sentiment_scorer import score_sentiment
from ats_engine.behavioral_indicators import build_communication_strength_indicator

def test_count_hesitation_markers():
    assert count_hesitation_markers("um I think maybe I have three years") >= 2

def test_measure_pace_normal():
    result = measure_response_pace(10, 5)
    assert result["pace_label"] == "normal"

def test_detect_uncertainty():
    assert detect_uncertainty("I'm not sure about that") is True
    assert detect_uncertainty("I have three years of experience") is False

def test_sentiment_positive():
    result = score_sentiment("I really enjoy working with data and love solving problems")
    assert result["label"] == "positive"

def test_communication_strength_strong():
    confidence = {"confidence_score": 0.9, "hesitation_count": 0, "uncertainty_detected": False, "pace": {"pace_label": "normal"}}
    sentiment = {"label": "positive"}
    result = build_communication_strength_indicator(confidence, sentiment)
    assert result["communication_strength"] == "Strong"