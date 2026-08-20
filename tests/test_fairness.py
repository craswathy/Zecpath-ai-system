import sys
sys.path.append(".")
from ats_engine.fairness_normalizer import mask_personal_attributes, normalize_score_distribution
from ats_engine.bias_checker import check_keyword_overdependence

def test_mask_personal_attributes():
    profile = {"personal_info": {"name": "Test Person", "email": "test@test.com"}}
    masked = mask_personal_attributes(profile)
    assert masked["personal_info"]["name"] == "[MASKED]"
    assert masked["personal_info"]["email"] == "[MASKED]"

def test_normalize_score_distribution():
    result = normalize_score_distribution([50, 60, 70])
    assert result[0] == 0.0
    assert result[-1] == 100.0

def test_keyword_overdependence_flagged():
    scores = {"skill_match": 0.95, "experience_relevance": 0.1, "education_alignment": 0.1}
    assert check_keyword_overdependence(scores) is True

def test_keyword_overdependence_not_flagged():
    scores = {"skill_match": 0.8, "experience_relevance": 0.7, "education_alignment": 0.75}
    assert check_keyword_overdependence(scores) is False