import json
from ats_engine.aptitude_question_bank import get_aptitude_questions
from ats_engine.logical_reasoning_scorer import score_logical_reasoning
from ats_engine.scenario_evaluator import evaluate_scenario_response, assess_problem_solving_clarity
from utils.logger import logger

DEMO_RESPONSES = {
    "apt_logic_01": "So 3 people take 12 days, that means 36 person-days total. With 4 people it would take 9 days.",
    "apt_logic_02": "The differences are 4, 6, 8, 10, so the next difference is 12, giving 42.",
    "apt_verbal_01": "No, that doesn't follow, because only some detail-oriented people are slow, not all of them.",
    "apt_sjt_01": "I would first acknowledge the mistake and then immediately inform the client and my team so we can correct it together.",
    "apt_sjt_02": "I would first talk to them directly to understand why, before escalating to management.",
}

def run():
    questions = get_aptitude_questions(role_type="technical")
    results = []

    for question in questions:
        response_text = DEMO_RESPONSES.get(question["id"], "")

        if question["expected_answer_type"] in ("numeric", "reasoning"):
            score_result = score_logical_reasoning(response_text, question)
            results.append({
                "question_id": question["id"],
                "category": question["category"],
                "response": response_text,
                "type": "logical_reasoning",
                **score_result,
            })
        else:
            coverage_result = evaluate_scenario_response(response_text, question["ideal_answer_structure"])
            clarity_result = assess_problem_solving_clarity(response_text)
            results.append({
                "question_id": question["id"],
                "category": question["category"],
                "response": response_text,
                "type": "situational_judgment",
                **coverage_result,
                **clarity_result,
            })

    output_path = "data/aptitude_evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Evaluated {len(results)} aptitude/scenario questions.")
    for r in results:
        score_display = r.get("score", r.get("coverage_score", "N/A"))
        print(f"  [{r['category']}] {r['question_id']}: {score_display}")
    print(f"Check {output_path}")

if __name__ == "__main__":
    run()