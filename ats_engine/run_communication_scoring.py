import json
from ats_engine.communication_scorer import score_communication
from ats_engine.communication_score_normalizer import normalize_communication_scores, apply_grammar_leniency_flag
from utils.logger import logger

def run():
    with open("data/demo_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    results = []
    for turn in transcript["turns"]:
        raw_text = turn["candidate_response_raw"]
        normalized_text = turn["candidate_response_normalized"]

        scored = score_communication(raw_text, normalized_text)
        word_count = len(raw_text.split())
        leniency_flag = apply_grammar_leniency_flag(scored.get("grammar_error_count", 0), word_count)

        results.append({
            "turn_id": turn["turn_id"],
            "question_category": turn["question_category"],
            "raw_answer": raw_text,
            **scored,
            "short_answer_leniency_flag": leniency_flag,
        })

    all_scores = [r["communication_score"] for r in results]
    normalized = normalize_communication_scores(all_scores)
    for r, n in zip(results, normalized):
        r["normalized_score"] = n

    output_path = "data/communication_score_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Scored {len(results)} responses. Check {output_path}")
    for r in results:
        print(f"  [{r['question_category']}] Score: {r['communication_score']}/100")

if __name__ == "__main__":
    run()