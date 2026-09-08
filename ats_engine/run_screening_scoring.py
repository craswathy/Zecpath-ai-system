import json
from ats_engine.screening_scorer import score_answer
from ats_engine.screening_aggregator import normalize_scores, aggregate_screening_score
from utils.logger import logger

def run():
    with open("data/answer_understanding_result.json", "r", encoding="utf-8") as f:
        answers = json.load(f)

    with open("data/demo_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    confidence_by_turn = {t["turn_id"]: t["response_confidence"] for t in transcript["turns"]}

    per_question_scores = []
    previous_experience_value = None

    for answer in answers:
        confidence = confidence_by_turn.get(answer["turn_id"], 0.8)

        prev_value = previous_experience_value if answer["question_category"] == "Experience" else None
        scored = score_answer(answer, confidence, previously_stated_value=prev_value)
        per_question_scores.append(scored)

        if answer["question_category"] == "Experience":
            previous_experience_value = answer["structured_answer"]["extracted_value"]

    per_question_scores = normalize_scores(per_question_scores)
    final_result = aggregate_screening_score(per_question_scores)

    output = {
        "per_question_scores": per_question_scores,
        "final_screening_score": final_result,
    }

    output_path = "data/screening_score_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Done. Final screening score: {final_result['final_screening_score']}/100")
    print(f"Check {output_path} for full breakdown.")

if __name__ == "__main__":
    run()