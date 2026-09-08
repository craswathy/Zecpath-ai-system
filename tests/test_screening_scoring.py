import sys
sys.path.append(".")
from ats_engine.screening_scorer import score_clarity, score_relevance, score_completeness, score_consistency
from ats_engine.screening_aggregator import aggregate_screening_score

def test_score_clarity_high_confidence_full_answer():
    score = score_clarity("I have three years of experience in data analysis and Python", 0.95)
    assert score > 0.7

def test_score_relevance_off_topic():
    assert score_relevance(True, ["skills_mention"]) == 0.1

def test_score_relevance_on_topic():
    assert score_relevance(False, ["skills_mention"]) == 1.0

def test_score_completeness_vague():
    assert score_completeness(True, None) == 0.0

def test_score_consistency_matching_values():
    assert score_consistency(3, 3) == 1.0

def test_score_consistency_conflicting_values():
    assert score_consistency(3, 7) == 0.2

def test_aggregate_screening_score():
    scores = [
        {"question_category": "Skills", "weighted_score": 0.9},
        {"question_category": "Experience", "weighted_score": 0.8},
    ]
    result = aggregate_screening_score(scores)
    assert 0 <= result["final_screening_score"] <= 100