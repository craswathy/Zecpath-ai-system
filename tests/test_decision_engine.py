import sys
sys.path.append(".")
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide, compute_confidence, format_decision_summary

STRONG = {"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84}
WEAK = {"ats": 45, "screening": 40, "hr_interview": 44, "technical_interview": 42, "machine_test": 41}
MID = {"ats": 65, "screening": 62, "hr_interview": 66, "technical_interview": 64, "machine_test": 63}


def _decide(scores, context=None, role="technical", low=None):
    unified = build_unified_score_object("c1", "j1", scores, role, low, context)
    return decide(unified)


def test_strong_complete_candidate_is_selected():
    d = _decide(STRONG)
    assert d["decision"] == "Selected"
    assert d["confidence"]["band"] == "high"


def test_weak_complete_candidate_is_rejected_with_human_review():
    d = _decide(WEAK)
    assert d["decision"] == "Rejected"
    assert d["human_review"]["required"] is True
    assert d["human_review"]["final_decision"] is None


def test_middle_candidate_goes_to_hold_review():
    assert _decide(MID)["decision"] == "Hold / Review"


def test_borderline_score_goes_to_hold_review():
    d = _decide({k: 76 for k in STRONG})
    assert d["score_based_decision"] == "Selected"
    assert d["decision"] == "Hold / Review"
    assert any(r["id"] == "BORDERLINE" for r in d["rules_triggered"])


def test_integrity_high_moves_selected_to_hold():
    d = _decide(STRONG, {"integrity_review_priority": "High"})
    assert d["decision"] == "Hold / Review"
    assert any(r["id"] == "INTEGRITY_HIGH" for r in d["rules_triggered"])


def test_integrity_never_causes_rejection():
    d = _decide(STRONG, {"integrity_review_priority": "High"})
    assert d["decision"] != "Rejected"
    d2 = _decide(MID, {"integrity_review_priority": "High"})
    assert d2["decision"] == "Hold / Review"


def test_integrity_medium_lowers_confidence_only():
    plain = _decide(STRONG)
    medium = _decide(STRONG, {"integrity_review_priority": "Medium"})
    assert medium["confidence"]["score"] < plain["confidence"]["score"]
    assert medium["score_based_decision"] == plain["score_based_decision"]


def test_behavioral_label_never_changes_decision_or_confidence():
    plain = _decide(STRONG)
    low_engagement = _decide(STRONG, {"behavioral_label": "Low observed engagement"})
    assert plain["decision"] == low_engagement["decision"]
    assert plain["confidence"]["score"] == low_engagement["confidence"]["score"]
    assert "never changes a decision" in low_engagement["risk_factors"]["behavioral"]["effect"]


def test_preliminary_result_is_hold_with_capped_confidence():
    d = _decide({"ats": 95, "screening": 95})
    assert d["decision"] == "Hold / Review"
    assert d["confidence"]["score"] <= 0.4


def test_missing_required_round_blocks_selection():
    scores = dict(STRONG)
    scores["technical_interview"] = None
    d = _decide(scores)
    assert d["decision"] == "Hold / Review"
    assert any(r["id"] == "REQUIRED_ROUND_MISSING" for r in d["rules_triggered"])


def test_required_round_depends_on_role():
    scores = dict(STRONG)
    scores["technical_interview"] = None
    d = _decide(scores, role="client_facing")
    assert d["decision"] == "Selected"


def test_weak_round_cannot_give_selected():
    scores = dict(STRONG)
    scores["ats"] = 35
    d = _decide(scores)
    assert d["decision"] != "Selected"


def test_low_confidence_blocks_rejection():
    d = _decide({"ats": 40, "screening": 40, "hr_interview": None, "technical_interview": 40, "machine_test": None},
                low=["ats", "screening", "technical_interview"])
    assert d["decision"] != "Rejected"


def test_no_rules_can_move_toward_selected_or_rejected():
    d = _decide(MID, {"integrity_review_priority": "No concern"})
    assert d["decision"] == "Hold / Review"
    assert all(r["moves_to_hold"] in (True, False) for r in d["rules_triggered"])


def test_confidence_is_between_zero_and_one():
    for scores in (STRONG, WEAK, MID):
        c = _decide(scores)["confidence"]["score"]
        assert 0.0 <= c <= 1.0


def test_no_scores_gives_hold_and_zero_confidence():
    d = _decide({})
    assert d["decision"] == "Hold / Review"
    assert d["confidence"]["score"] == 0.0


def test_output_has_required_fields_and_metadata():
    d = _decide(STRONG)
    for key in ("decision", "recommendation", "score_based_decision", "hiring_fit", "rules_triggered",
                "confidence", "risk_factors", "next_steps", "human_review", "explanation"):
        assert key in d
    for key in ("model_version", "timestamp", "stage", "status"):
        assert key in d["metadata"]
    assert "Final recommendation" in d["explanation"]


def test_plain_hold_still_has_a_next_step():
    assert _decide(MID)["next_steps"]


def test_summary_text_contains_decision_and_confidence():
    text = format_decision_summary(_decide(STRONG))
    assert "SELECTED" in text and "confidence" in text