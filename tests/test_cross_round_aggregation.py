import sys
sys.path.append(".")
from ats_engine.cross_round_config import ROLE_WEIGHTS
from ats_engine.cross_round_aggregation_engine import aggregate_rounds, rank_in_pool
from ats_engine.hiring_fit_calculator_v2 import classify_hiring_fit
from ats_engine.unified_candidate_score_object import build_unified_score_object

ALL_80 = {"ats": 80, "screening": 80, "hr_interview": 80, "technical_interview": 80, "machine_test": 80}


def test_every_role_weights_add_up_to_one():
    for weights in ROLE_WEIGHTS.values():
        assert round(sum(weights.values()), 5) == 1.0


def test_all_rounds_equal_scores_give_same_percentage():
    assert aggregate_rounds(ALL_80)["hiring_fit_percentage"] == 80.0


def test_missing_rounds_share_their_weight():
    result = aggregate_rounds({"ats": 80, "screening": 80})
    assert result["rounds_completed"] == 2
    assert result["hiring_fit_percentage"] == 80.0
    assert "hr_interview" in result["missing_rounds"]


def test_role_weights_change_the_result():
    scores = {"ats": 50, "screening": 50, "hr_interview": 50, "technical_interview": 90, "machine_test": 90}
    technical = aggregate_rounds(scores, "technical")["hiring_fit_percentage"]
    client_facing = aggregate_rounds(scores, "client_facing")["hiring_fit_percentage"]
    assert technical > client_facing


def test_unknown_role_uses_default_weights():
    assert aggregate_rounds(ALL_80, "no_such_role")["role_used"] == "default"


def test_low_reliability_round_counts_half():
    full = aggregate_rounds({"ats": 100, "screening": 0})
    low = aggregate_rounds({"ats": 100, "screening": 0}, low_reliability_rounds=["screening"])
    assert low["hiring_fit_percentage"] > full["hiring_fit_percentage"]
    assert low["weights_used"]["screening"] < full["weights_used"]["screening"]


def test_invalid_score_is_ignored_not_used():
    result = aggregate_rounds({"ats": 150, "screening": 80, "hr_interview": True})
    assert result["rounds_completed"] == 1
    assert "ats" in result["invalid_rounds"] and "hr_interview" in result["invalid_rounds"]
    assert result["hiring_fit_percentage"] == 80.0


def test_no_rounds_returns_zero_and_pending():
    obj = build_unified_score_object("c0", "j1", {})
    assert obj["hiring_fit"]["percentage"] == 0.0
    assert obj["hiring_fit"]["category"] == "No data"
    assert obj["metadata"]["status"] == "pending"


def test_contributions_add_up_to_the_percentage():
    result = aggregate_rounds({"ats": 70, "screening": 66, "hr_interview": 78, "technical_interview": 61.2}, "technical")
    assert abs(sum(result["contributions"].values()) - result["hiring_fit_percentage"]) < 0.1


def test_round_floor_caps_strong_fit():
    scores = {"ats": 38, "screening": 90, "hr_interview": 90, "technical_interview": 90, "machine_test": 90}
    aggregate = aggregate_rounds(scores, "technical")
    assert aggregate["hiring_fit_percentage"] >= 75
    fit = classify_hiring_fit(aggregate)
    assert fit["fit_category"] == "Moderate Fit"
    assert any("capped" in f for f in fit["flags"])


def test_fewer_than_three_rounds_is_preliminary_and_capped():
    fit = classify_hiring_fit(aggregate_rounds({"ats": 95, "screening": 95}, "technical"))
    assert fit["status"] == "preliminary"
    assert fit["fit_category"] == "Moderate Fit"


def test_strong_fit_with_enough_rounds_and_no_weak_round():
    fit = classify_hiring_fit(aggregate_rounds(ALL_80, "technical"))
    assert fit["fit_category"] == "Strong Fit"
    assert fit["status"] == "final"


def test_context_is_shown_but_not_scored():
    context = {"integrity_review_priority": "High"}
    with_context = build_unified_score_object("c1", "j1", ALL_80, "technical", context=context)
    without = build_unified_score_object("c1", "j1", ALL_80, "technical")
    assert with_context["hiring_fit"]["percentage"] == without["hiring_fit"]["percentage"]
    assert with_context["context_not_scored"] == context


def test_object_follows_metadata_standard():
    obj = build_unified_score_object("c1", "j1", ALL_80, "technical")
    for key in ("model_version", "timestamp", "stage", "status"):
        assert key in obj["metadata"]
    assert obj["metadata"]["status"] == "complete"
    assert obj["candidate_id"] == "c1" and obj["job_id"] == "j1"


def test_partial_object_lists_missing_rounds():
    obj = build_unified_score_object("c2", "j1", {"ats": 80, "screening": 70, "hr_interview": 75})
    assert obj["metadata"]["status"] == "partial"
    assert "machine_test" in obj["missing_rounds"]


def test_rank_puts_category_before_percentage():
    pool = [("Strong Fit", 84.1), ("Moderate Fit", 84.8), ("Weak Fit", 37.0)]
    assert rank_in_pool("Strong Fit", 84.1, pool)["rank"] == 1
    assert rank_in_pool("Moderate Fit", 84.8, pool)["rank"] == 2


def test_preliminary_candidate_is_not_ranked():
    pool = [("Strong Fit", 84.1)]
    obj = build_unified_score_object("c3", "j1", {"ats": 90, "screening": 90}, "technical", pool=pool)
    assert obj["rank_in_pool"] is None