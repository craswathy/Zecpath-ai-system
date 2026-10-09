import sys
sys.path.append(".")
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit


def test_unified_score_all_rounds():
    result = compute_unified_score({"ats": 80, "screening": 80, "hr_interview": 80})
    assert result["hiring_fit_percentage"] == 80.0


def test_missing_round_redistributes_weight():
    result = compute_unified_score({"ats": 80, "screening": 80, "hr_interview": None})
    assert result["rounds_completed"] == 2
    assert result["hiring_fit_percentage"] == 80.0


def test_no_rounds_returns_zero():
    result = compute_unified_score({"ats": None, "screening": None, "hr_interview": None})
    assert result["hiring_fit_percentage"] == 0.0


def test_role_weights_change_result():
    scores = {"ats": 90, "screening": 50, "hr_interview": 50}
    technical = compute_unified_score(scores, role_category="technical")
    client_facing = compute_unified_score(scores, role_category="client_facing")
    assert technical["hiring_fit_percentage"] > client_facing["hiring_fit_percentage"]


def test_round_floor_caps_strong_fit():
    # Weighted score is 75.6 (Strong Fit), but HR is below the floor of 40
    unified = compute_unified_score({"ats": 100, "screening": 100, "hr_interview": 39})
    assert unified["hiring_fit_percentage"] >= 75
    fit = classify_hiring_fit(unified)
    assert fit["fit_category"] == "Moderate Fit"
    assert any("capped" in f for f in fit["flags"])


def test_strong_fit_without_weak_round():
    unified = compute_unified_score({"ats": 85, "screening": 80, "hr_interview": 82})
    fit = classify_hiring_fit(unified)
    assert fit["fit_category"] == "Strong Fit"