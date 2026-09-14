import json
from ats_engine.safety_fallback_framework import diagnose_turn, get_safety_response
from utils.logger import logger

EDGE_CASE_SCENARIOS = [
    {
        "name": "noisy_low_confidence",
        "stt_result": {"text": "I I I have have some some experience", "confidence": 0.35},
        "intent_result": {"is_off_topic": False, "structured_answer": {"is_vague_or_missing": False}},
        "retry_count": 0,
    },
    {
        "name": "total_silence",
        "stt_result": {"text": "", "confidence": 0.0},
        "intent_result": {},
        "retry_count": 0,
    },
    {
        "name": "call_dropped_mid_question",
        "stt_result": {"text": "", "confidence": 0.0},
        "intent_result": {},
        "retry_count": 0,
        "call_status": "dropped",
    },
    {
        "name": "clear_normal_answer",
        "stt_result": {"text": "I have three years of experience in data analysis", "confidence": 0.92},
        "intent_result": {"is_off_topic": False, "structured_answer": {"is_vague_or_missing": False}},
        "retry_count": 0,
    },
    {
        "name": "exhausted_retries",
        "stt_result": {"text": "", "confidence": 0.0},
        "intent_result": {},
        "retry_count": 2,
    },
]

def run():
    results = []
    for scenario in EDGE_CASE_SCENARIOS:
        issue = diagnose_turn(
            scenario["stt_result"],
            scenario["intent_result"],
            scenario["retry_count"],
            scenario.get("call_status", "active"),
        )
        response = get_safety_response(issue, scenario["retry_count"]) if issue else {"action": "proceed", "message": None}

        result = {
            "scenario": scenario["name"],
            "diagnosed_issue": issue,
            "safety_response": response,
        }
        results.append(result)
        logger.info(f"{scenario['name']}: issue={issue}, action={response['action']}")

    output_path = "data/edge_case_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Tested {len(results)} edge cases. Check {output_path}")
    for r in results:
        print(f"  {r['scenario']}: {r['diagnosed_issue']} -> {r['safety_response']['action']}")

if __name__ == "__main__":
    run()