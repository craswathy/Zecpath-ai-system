import json
import os
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from ats_engine.hr_score_normalizer import normalize_for_interview_length
from ats_engine.hr_interview_report_generator import build_hr_interview_summary, generate_natural_language_narrative
from utils.logger import logger

# Four distinct candidate profiles, covering the required test types.
# Each simulates per_turn_data directly (bypassing live audio/STT) so
# the HR scoring/summary pipeline (Days 37-39) can be tested end-to-end
# with controlled, repeatable inputs.
CANDIDATE_SIMULATIONS = {
    "confident_candidate": {
        "per_turn_data": [
            {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 88, "behavioral_confidence_score": 90},
            {"turn_id": "t2", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 85, "behavioral_confidence_score": 88},
            {"turn_id": "t3", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 82, "behavioral_confidence_score": 85},
            {"turn_id": "t4", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 90, "behavioral_confidence_score": 92},
        ],
        "contradiction_count": 0,
        "expected_manual_verdict": "Strong",
    },
    "hesitant_candidate": {
        "per_turn_data": [
            {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 55, "behavioral_confidence_score": 48},
            {"turn_id": "t2", "is_off_topic": False, "is_vague_or_missing": True, "communication_score": 40, "behavioral_confidence_score": 45},
            {"turn_id": "t3", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 58, "behavioral_confidence_score": 50},
            {"turn_id": "t4", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 60, "behavioral_confidence_score": 52},
        ],
        "contradiction_count": 0,
        "expected_manual_verdict": "Adequate, coaching needed on confidence",
    },
    "inexperienced_candidate": {
        "per_turn_data": [
            {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 70, "behavioral_confidence_score": 75},
            {"turn_id": "t2", "is_off_topic": False, "is_vague_or_missing": True, "communication_score": 45, "behavioral_confidence_score": 60},
            {"turn_id": "t3", "is_off_topic": True, "is_vague_or_missing": False, "communication_score": 50, "behavioral_confidence_score": 65},
        ],
        "contradiction_count": 0,
        "expected_manual_verdict": "Below-expectation on role-specific depth, acceptable communication",
    },
    "overqualified_candidate": {
        "per_turn_data": [
            {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 92, "behavioral_confidence_score": 88},
            {"turn_id": "t2", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 90, "behavioral_confidence_score": 90},
            {"turn_id": "t3", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 95, "behavioral_confidence_score": 91},
            {"turn_id": "t4", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 88, "behavioral_confidence_score": 87},
            {"turn_id": "t5", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 91, "behavioral_confidence_score": 89},
        ],
        "contradiction_count": 1,  # e.g. inconsistent stated salary expectations vs seniority
        "expected_manual_verdict": "Strong content, but 1 contradiction flagged -- possible over-scripted answers, needs manual review",
    },
}


def run():
    results = []

    for name, data in CANDIDATE_SIMULATIONS.items():
        hr_score_result = compute_hr_interview_score(
            data["per_turn_data"], data["contradiction_count"], role_category="technical"
        )
        hr_score_result = normalize_for_interview_length(hr_score_result)

        summary = build_hr_interview_summary(
            name, hr_score_result, [], data["per_turn_data"], [], data["contradiction_count"]
        )
        narrative = generate_natural_language_narrative(summary)

        results.append({
            "candidate_type": name,
            "hr_score_result": hr_score_result,
            "narrative": narrative,
            "expected_manual_verdict": data["expected_manual_verdict"],
        })

        logger.info(f"{name}: score={hr_score_result['hr_interview_score']}, reliability={hr_score_result['score_reliability']}")

    output_dir = "data"
    with open(os.path.join(output_dir, "hr_interview_simulation_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Done. Simulated 4 candidate types through the HR interview scoring pipeline.")
    for r in results:
        print(f"  {r['candidate_type']}: AI score = {r['hr_score_result']['hr_interview_score']}/100")
    print("Check data/hr_interview_simulation_results.json")

if __name__ == "__main__":
    run()