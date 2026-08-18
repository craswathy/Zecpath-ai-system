import sys
sys.path.append(".")
from ats_engine.ats_scorer import compute_ats_score

def test_missing_data_handled_gracefully():
    candidate_data = {"skills": None, "experience_summary": None, "education_relevance": None, "semantic_match": None}
    jd_data = {"required_skills": []}
    result = compute_ats_score(candidate_data, jd_data)
    assert result["final_score"] == 0.0

def test_full_data_produces_score_between_0_and_100():
    candidate_data = {
        "skills": [{"skill": "python", "confidence": 1.0}],
        "experience_summary": {"experience_entries": [{"relevance_score": 0.8}]},
        "education_relevance": {"relevance_score": 0.9},
        "semantic_match": {"overall_similarity": 0.7},
    }
    jd_data = {"required_skills": [{"name": "python", "mandatory": True}]}
    result = compute_ats_score(candidate_data, jd_data)
    assert 0 <= result["final_score"] <= 100