import sys
sys.path.append(".")
import json
import logging
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.refined_decision_logic import decide_refined, batch_mode
from ats_engine.refined_intent import classify_follow_up_refined, count_hedges
from ats_engine.run_optimization_analysis import score_set, reference_decision
from utils.logger import logger


def _unified(scores, role="technical", context=None):
    return build_unified_score_object("c1", "j1", scores, role, None, context or {"integrity_review_priority": "No concern"})


def test_weak_technical_interview_blocks_selected():
    u = _unified({"ats": 95, "screening": 95, "hr_interview": 95, "technical_interview": 45, "machine_test": 95})
    assert decide(u)["decision"] == "Selected"
    d = decide_refined(u)
    assert d["decision"] == "Hold / Review"
    assert any(r["id"] == "CRITICAL_ROUND_WEAK" for r in d["rules_triggered"])


def test_weak_machine_test_blocks_selected_for_technical_role():
    u = _unified({"ats": 90, "screening": 90, "hr_interview": 90, "technical_interview": 90, "machine_test": 52})
    assert decide_refined(u)["decision"] == "Hold / Review"


def test_key_round_rule_does_not_apply_to_other_roles():
    u = _unified({"ats": 90, "screening": 90, "hr_interview": 90, "technical_interview": 62, "machine_test": 90}, role="client_facing")
    assert decide_refined(u)["decision"] == decide(u)["decision"]


def test_rounds_disagree_moves_selected_to_hold():
    u = _unified({"ats": 97, "screening": 40, "hr_interview": 95, "technical_interview": 96, "machine_test": 94})
    assert decide(u)["decision"] == "Selected"
    d = decide_refined(u)
    assert d["decision"] == "Hold / Review"
    assert any(r["id"] == "ROUNDS_DISAGREE" for r in d["rules_triggered"])


def test_rounds_disagree_moves_rejected_to_hold():
    u = _unified({"ats": 20, "screening": 20, "hr_interview": 20, "technical_interview": 20, "machine_test": 95})
    assert decide(u)["decision"] == "Rejected"
    assert decide_refined(u)["decision"] == "Hold / Review"


def test_refined_never_moves_hold_to_selected_or_rejected():
    for scores in ({"ats": 65, "screening": 62, "hr_interview": 66, "technical_interview": 64, "machine_test": 63},
                   {"ats": 90, "screening": 88, "hr_interview": None, "technical_interview": None, "machine_test": None}):
        u = _unified(scores)
        assert decide(u)["decision"] == "Hold / Review"
        assert decide_refined(u)["decision"] == "Hold / Review"


def test_clean_strong_candidate_is_unchanged():
    u = _unified({"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84})
    assert decide_refined(u)["decision"] == "Selected"


def test_refined_output_keeps_human_review_and_version():
    u = _unified({"ats": 95, "screening": 95, "hr_interview": 95, "technical_interview": 45, "machine_test": 95})
    d = decide_refined(u)
    assert d["human_review"]["required"] is True
    assert d["metadata"]["model_version"] == "decision_v1.1"
    assert "confirms" not in " ".join(d["next_steps"])


def test_off_topic_answer_gets_clarification():
    assert classify_follow_up_refined("I like watching cricket on the weekend with my family and friends", False, True) == "clarification"


def test_long_hedged_answer_gets_clarification():
    text = "Maybe a data analyst role for now, and I will see how it goes after that, I am not very sure"
    assert classify_follow_up_refined(text, False) == "clarification"


def test_concrete_answer_with_hedge_word_gets_no_clarification():
    text = "I think I built the pipeline in Python and reduced the runtime by 40 percent"
    assert classify_follow_up_refined(text, False) != "clarification"


def test_single_weak_hedge_in_a_clear_answer_is_not_enough():
    text = "I think my main strength is breaking a messy problem into small steps and testing each step before moving on"
    assert count_hedges(text) == (0, 1)
    assert classify_follow_up_refined(text, False) is None


def test_refined_scoring_is_better_on_the_development_set():
    with open("data/optimization/labeled_candidates.json", encoding="utf-8") as f:
        dev = json.load(f)["dev"]
    before, after = score_set(dev, False), score_set(dev, True)
    assert after["fp"] < before["fp"]
    assert after["fn"] <= before["fn"]
    assert after["correct"] > before["correct"]


def test_reference_rubric_basics():
    base = {"role": "technical", "low_reliability": [], "integrity": "No concern", "id": "x", "why": ""}
    strong = dict(base, scores={"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84})
    assert reference_decision(strong) == "Selected"
    assert reference_decision(dict(strong, integrity="High")) == "Hold / Review"


def test_batch_mode_restores_logging_level():
    before = logger.level
    with batch_mode():
        assert logger.level == logging.WARNING
    assert logger.level == before