import sys
sys.path.append(".")
from ats_engine.hr_interview_scorer import score_relevance_for_turn, score_consistency_for_candidate, compute_hr_interview_score
from ats_engine.hr_score_normalizer import normalize_for_interview_length

def test_score_relevance_off_topic():
    assert score_relevance_for_turn(True, False) == 0.1

def test_score_relevance_on_topic():
    assert score_relevance_for_turn(False, False) == 1.0

def test_score_consistency_no_contradictions():
    assert score_consistency_for_candidate(0, 5) == 1.0

def test_score_consistency_with_contradictions():
    assert score_consistency_for_candidate(2, 5) < 1.0

def test_compute_hr_score_empty_input():
    result = compute_hr_interview_score([], 0)
    assert result["hr_interview_score"] == 0.0

def test_normalize_flags_low_reliability():
    result = {"turns_scored": 2}
    normalized = normalize_for_interview_length(result)
    assert normalized["score_reliability"] == "low_reliability"

def test_normalize_flags_reliable():
    result = {"turns_scored": 6}
    normalized = normalize_for_interview_length(result)
    assert normalized["score_reliability"] == "reliable"