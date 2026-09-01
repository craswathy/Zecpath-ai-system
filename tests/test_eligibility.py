import sys
sys.path.append(".")
from ats_engine.eligibility_engine import check_mandatory_skills, check_experience_range, evaluate_eligibility

def test_mandatory_skills_all_present():
    skills = [{"skill": "python", "confidence": 1.0}, {"skill": "sql", "confidence": 0.9}]
    passed, missing = check_mandatory_skills(skills, ["python", "sql"])
    assert passed is True
    assert missing == []

def test_mandatory_skills_missing_one():
    skills = [{"skill": "python", "confidence": 1.0}]
    passed, missing = check_mandatory_skills(skills, ["python", "sql"])
    assert passed is False
    assert "sql" in missing

def test_experience_range_within_bounds():
    assert check_experience_range(3, 0, 6) is True

def test_experience_range_out_of_bounds():
    assert check_experience_range(15, 0, 6) is False

def test_evaluate_eligibility_all_pass():
    result = evaluate_eligibility(
        candidate_id="test_candidate",
        job_id="jd_data_analyst",
        ats_score=75,
        candidate_skills=[{"skill": "sql", "confidence": 1.0}, {"skill": "excel", "confidence": 1.0}],
        total_experience_years=3,
    )
    assert result["eligibility_tag"] == "Eligible"