import sys
sys.path.append(".")
from ats_engine.polished_decision_service import safe_decide
from ats_engine.polished_reports import reasons_for, render
from ats_engine import consistency_checks as cc

RESULT = {
    "candidate_id": "c1", "job_id": "j1", "category": "Moderate Fit",
    "hiring_fit_percentage": 66.0, "flags": ["Weak round(s): hr_interview scored below 40"],
    "screening_score_simulated": 60.0,
    "ats": {"ats_score": 70.0, "sections_found": ["EDUCATION"], "years": None, "missing": ["experience_relevance"]},
    "hr": {"hr_score": 50.0, "band": "Adequate", "weak_components": ["confidence"]},
}


def test_valid_request_returns_decision():
    r = safe_decide({"round_scores": {"ats": 80, "screening": 70, "hr_interview": 65}, "role_category": "technical"})
    assert r["category"] in ("Strong Fit", "Moderate Fit", "Weak Fit")
    assert r["model_version"]


def test_out_of_range_score_rejected_with_field():
    r = safe_decide({"round_scores": {"ats": 250}})
    assert r["error"]["code"] == "SCORE_OUT_OF_RANGE" and r["error"]["field"] == "ats"


def test_text_score_rejected():
    assert safe_decide({"round_scores": {"ats": "high"}})["error"]["code"] == "INVALID_SCORE"


def test_unknown_round_rejected():
    assert safe_decide({"round_scores": {"ats": 50, "video": 50}})["error"]["code"] == "UNKNOWN_ROUND"


def test_no_scores_goes_to_manual_review_not_rejection():
    r = safe_decide({"round_scores": {}})
    assert r["error"]["code"] == "NO_ROUND_SCORES"
    assert r["decision"] == "Needs Manual Review"


def test_missing_round_still_scores():
    assert "error" not in safe_decide({"round_scores": {"ats": 80, "screening": 70, "hr_interview": None}})


def test_reasons_explain_missing_sections_and_weak_areas():
    text = " ".join(reasons_for(RESULT))
    assert "No clear Skills section" in text and "confidence" in text


def test_report_always_says_human_decides():
    assert "A person makes the final decision" in render(RESULT)


def test_scoring_consistency():
    assert cc.check_deterministic()
    assert cc.check_monotonic() == []
    assert cc.check_range() == []
    assert cc.check_boundaries() == {}