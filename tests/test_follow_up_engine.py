import sys
sys.path.append(".")
from ats_engine.follow_up_trigger_detector import classify_follow_up_need, needs_deepening, is_confident_response
from ats_engine.adaptive_questioning_framework import decide_next_action, select_follow_up_question

def test_classify_clarification_for_vague():
    result = classify_follow_up_need("", is_vague_or_missing=True)
    assert result == "clarification"

def test_classify_deepening_for_shallow():
    result = classify_follow_up_need("good", is_vague_or_missing=False)
    assert result == "deepening"

def test_classify_scenario_for_confident():
    result = classify_follow_up_need(
        "I specifically led the redesign, for example cutting delivery time significantly in my experience.",
        is_vague_or_missing=False,
    )
    assert result == "scenario_based"

def test_decide_next_action_respects_ineligible_question():
    decision = decide_next_action("deepening", "q1", {}, base_eligible=False)
    assert decision["action"] == "move_to_next"

def test_no_repeat_follow_up_questions():
    asked = {}
    first = select_follow_up_question("deepening", "q1", asked)
    second = select_follow_up_question("deepening", "q1", asked)
    assert first != second

def test_follow_up_limit_enforced():
    asked = {"q1": ["a", "b"]}
    result = select_follow_up_question("deepening", "q1", asked)
    assert result is None