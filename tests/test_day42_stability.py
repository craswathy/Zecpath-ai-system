import sys
sys.path.append(".")
from ats_engine.hr_interview_scorer import compute_hr_interview_score, classify_performance_band
from ats_engine.hr_interview_summary_builder import summarize_overall_hr_performance
from ats_engine.transcript_normalizer import normalize_transcript_text, extract_yes_no_answer
from ats_engine.follow_up_trigger_detector import classify_follow_up_need
from ats_engine.follow_up_state_tracker import FollowUpStateTracker


def test_weak_component_downgrades_strong_to_adequate():
    band, weak, adjusted_from = classify_performance_band(
        75.8, {"relevance": 0.82, "communication": 0.53, "confidence": 0.49, "consistency": 1.0})
    assert band == "Adequate"
    assert weak == ["confidence"]
    assert adjusted_from == "Strong"


def test_no_weak_component_keeps_band():
    band, weak, adjusted_from = classify_performance_band(
        95.5, {"relevance": 1.0, "communication": 0.86, "confidence": 0.89, "consistency": 1.0})
    assert band == "Strong" and weak == [] and adjusted_from is None


def test_weak_relevance_downgrades_adequate_to_below():
    band, _, _ = classify_performance_band(
        64.9, {"relevance": 0.47, "communication": 0.55, "confidence": 0.67, "consistency": 1.0})
    assert band == "Below-expectation"


def test_missing_component_is_excluded_not_faked():
    turns = [{"is_off_topic": False, "is_vague_or_missing": False,
              "communication_score": None, "behavioral_confidence_score": 80}]
    result = compute_hr_interview_score(turns, 0)
    assert "communication" in result["missing_components"]
    assert "communication" not in result["component_scores"]
    assert result["hr_interview_score"] > 0


def test_summary_mentions_adjustment():
    text = summarize_overall_hr_performance({
        "hr_interview_score": 75.8, "performance_band": "Adequate",
        "weak_components": ["confidence"], "band_adjusted_from": "Strong"})
    assert "Adequate" in text and "confidence" in text


def test_yes_no_no_false_positive_on_know():
    assert extract_yes_no_answer("I know the process") == "unclear"


def test_yes_no_not_sure_is_unclear():
    assert extract_yes_no_answer("I am not sure about that") == "unclear"


def test_stutter_collapsed():
    assert "I I" not in normalize_transcript_text("I I I have three years of experience")


def test_pronoun_one_not_converted():
    assert "one of the projects" in normalize_transcript_text("one of the projects was difficult").lower()


def test_stray_comma_removed_after_filler():
    assert not normalize_transcript_text("um, I think so").startswith(",")


def test_empty_answer_triggers_clarification():
    assert classify_follow_up_need("   ", False) == "clarification"


def test_specific_number_skips_deepening():
    assert classify_follow_up_need("I have 3 years of experience", False) is None


def test_total_follow_up_cap():
    tracker = FollowUpStateTracker(max_total_follow_ups=1)
    first = tracker.process_answer("q1", "good", False, True)
    second = tracker.process_answer("q2", "fine", False, True)
    assert first["action"] == "ask_follow_up"
    assert second["action"] == "move_to_next"