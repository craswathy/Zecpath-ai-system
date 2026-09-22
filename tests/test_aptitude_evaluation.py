import sys
sys.path.append(".")
from ats_engine.logical_reasoning_scorer import extract_numeric_answer, score_numeric_reasoning, score_verbal_reasoning
from ats_engine.scenario_evaluator import evaluate_scenario_response, assess_problem_solving_clarity

def test_extract_numeric_answer():
    assert extract_numeric_answer("the answer is 9 days") == 9.0

def test_score_numeric_reasoning_correct():
    result = score_numeric_reasoning("the answer is 9", 9, "test_q")
    assert result["correct"] is True
    assert result["score"] == 1.0

def test_score_numeric_reasoning_incorrect():
    result = score_numeric_reasoning("the answer is 12", 9, "test_q")
    assert result["correct"] is False

def test_score_verbal_reasoning_correct_no():
    result = score_verbal_reasoning("No, that conclusion doesn't follow logically", "no", "test_q")
    assert result["correct"] is True

def test_evaluate_scenario_response_full_coverage():
    result = evaluate_scenario_response(
        "I would first talk to them directly to understand why before escalating",
        ["mentions direct communication first", "focuses on understanding root cause"],
    )
    assert result["coverage_score"] > 0

def test_problem_solving_clarity_structured():
    result = assess_problem_solving_clarity("First I would check the logs, then identify the root cause, therefore fixing it quickly")
    assert result["has_structured_reasoning"] is True