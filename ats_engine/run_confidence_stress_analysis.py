import json
from ats_engine.confidence_analyzer import compute_confidence_indicator
from ats_engine.sentiment_scorer import score_sentiment
from ats_engine.pause_repetition_detector import detect_long_pause, detect_repeated_words
from ats_engine.contradiction_detector import scan_for_contradictions
from ats_engine.stress_indicator import compute_stress_score, compute_behavioral_confidence_score
from utils.logger import logger

def run():
    with open("data/demo_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    with open("data/answer_understanding_result.json", "r", encoding="utf-8") as f:
        answers_data = json.load(f)

    results = []

    for turn in transcript["turns"]:
        raw_text = turn["candidate_response_raw"]
        word_count = len(raw_text.split())

        confidence_result = compute_confidence_indicator(
            raw_text, word_count, turn["response_duration_seconds"], turn["response_confidence"]
        )
        sentiment_result = score_sentiment(turn["candidate_response_normalized"])
        pause_result = detect_long_pause(word_count, turn["response_duration_seconds"])
        repetition_result = detect_repeated_words(raw_text)

        contradictions = scan_for_contradictions(answers_data, "experience_years")
        has_contradiction = any(c["turn_a"] == turn["turn_id"] or c["turn_b"] == turn["turn_id"] for c in contradictions)

        stress_score = compute_stress_score(
            confidence_result["hesitation_count"],
            pause_result["long_pause_detected"],
            repetition_result["repetition_count"],
            sentiment_result["label"],
            has_contradiction,
        )
        behavioral_score = compute_behavioral_confidence_score(confidence_result, stress_score)

        results.append({
            "turn_id": turn["turn_id"],
            "question_category": turn["question_category"],
            "confidence": confidence_result,
            "sentiment": sentiment_result,
            "pause_analysis": pause_result,
            "repetition_analysis": repetition_result,
            "contradiction_detected": has_contradiction,
            "stress_score": stress_score,
            "behavioral_confidence": behavioral_score,
        })

    output_path = "data/confidence_stress_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Analyzed {len(results)} turns. Check {output_path}")
    for r in results:
        print(f"  [{r['question_category']}] Behavioral Confidence: {r['behavioral_confidence']['behavioral_confidence_score']}/100")

if __name__ == "__main__":
    run()