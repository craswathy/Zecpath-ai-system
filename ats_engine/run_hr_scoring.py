import json
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from ats_engine.hr_score_normalizer import normalize_for_interview_length
from ats_engine.hr_score_report_formatter import export_hr_score_report, format_hr_score_report
from ats_engine.contradiction_detector import scan_for_contradictions
from utils.logger import logger

def run():
    with open("data/answer_understanding_result.json", "r", encoding="utf-8") as f:
        answers_data = json.load(f)

    with open("data/communication_score_results.json", "r", encoding="utf-8") as f:
        comm_data = json.load(f)

    with open("data/confidence_stress_results.json", "r", encoding="utf-8") as f:
        confidence_data = json.load(f)

    comm_by_turn = {c["turn_id"]: c["communication_score"] for c in comm_data}
    conf_by_turn = {c["turn_id"]: c["behavioral_confidence"]["behavioral_confidence_score"] for c in confidence_data}

    per_turn_data = []
    for answer in answers_data:
        turn_id = answer["turn_id"]
        per_turn_data.append({
            "turn_id": turn_id,
            "is_off_topic": answer["is_off_topic"],
            "is_vague_or_missing": answer["structured_answer"]["is_vague_or_missing"],
            "communication_score": comm_by_turn.get(turn_id, 50.0),
            "behavioral_confidence_score": conf_by_turn.get(turn_id, 50.0),
        })

    contradictions = scan_for_contradictions(answers_data, "experience_years")

    hr_score_result = compute_hr_interview_score(per_turn_data, len(contradictions), role_category="technical")
    hr_score_result = normalize_for_interview_length(hr_score_result)

    candidate_id = "cand_00123"
    paths = export_hr_score_report(candidate_id, hr_score_result)

    print(f"Done. HR interview score: {hr_score_result['hr_interview_score']}/100")
    print(f"Reliability: {hr_score_result['score_reliability']}")
    print()
    print(format_hr_score_report(candidate_id, hr_score_result))

if __name__ == "__main__":
    run()