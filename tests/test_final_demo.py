import sys
sys.path.append(".")
from ats_engine.run_final_demo import load_dataset, run_candidate


def _results():
    return {c["candidate_id"]: run_candidate(c) for c in load_dataset()}


def test_dataset_has_three_candidates():
    assert len(load_dataset()) == 3


def test_confident_candidate_is_strong():
    r = _results()["demo_confident"]
    assert r["hr"]["performance_band"] == "Strong"
    assert r["fit"]["fit_category"] == "Strong Fit"


def test_hesitant_candidate_is_adjusted_down():
    r = _results()["demo_hesitant"]
    assert r["hr"]["performance_band"] == "Adequate"
    assert r["hr"]["band_adjusted_from"] == "Strong"
    assert "confidence" in r["hr"]["weak_components"]


def test_inexperienced_candidate_is_below_expectation():
    r = _results()["demo_inexperienced"]
    assert r["hr"]["performance_band"] == "Below-expectation"
    assert r["fit"]["fit_category"] == "Weak Fit"


def test_every_result_has_recommendation_and_valid_score():
    for r in _results().values():
        assert r["recommendation"]
        assert 0 <= r["hr"]["hr_interview_score"] <= 100


def test_follow_up_cap_respected():
    for r in _results().values():
        assert r["follow_ups_asked"] <= 6