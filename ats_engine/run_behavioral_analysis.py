import json
from ats_engine.confidence_analyzer import compute_confidence_indicator
from ats_engine.sentiment_scorer import score_sentiment
from ats_engine.behavioral_indicators import build_communication_strength_indicator, build_call_level_report
from utils.logger import logger

def run():
    with open("data/demo_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    per_turn_indicators = []

    for turn in transcript["turns"]:
        raw_text = turn["candidate_response_raw"]
        word_count = len(raw_text.split())

        confidence_result = compute_confidence_indicator(
            raw_text, word_count, turn["response_duration_seconds"], turn["response_confidence"]
        )
        sentiment_result = score_sentiment(turn["candidate_response_normalized"])
        indicator = build_communication_strength_indicator(confidence_result, sentiment_result)

        per_turn_indicators.append({
            "turn_id": turn["turn_id"],
            "question_category": turn["question_category"],
            "confidence": confidence_result,
            "sentiment": sentiment_result,
            "indicator": indicator,
        })

    call_report = build_call_level_report(per_turn_indicators)

    output = {
        "per_turn_indicators": per_turn_indicators,
        "call_level_report": call_report,
    }

    output_path = "data/behavioral_analysis_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Done. Overall communication strength: {call_report['overall_strength']}")
    print(f"Check {output_path} for full breakdown.")

if __name__ == "__main__":
    run()