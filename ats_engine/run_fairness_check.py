import os
import json
from ats_engine.fairness_normalizer import mask_personal_attributes, normalize_score_distribution
from ats_engine.bias_checker import check_keyword_overdependence
from utils.logger import logger

SCORES_DIR = "data/ats_scores"
OUTPUT_DIR = "data/fairness_review"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    score_files = [f for f in os.listdir(SCORES_DIR) if f.endswith("_ats_score.json")]
    all_final_scores = []
    flagged_candidates = []

    for filename in score_files:
        with open(os.path.join(SCORES_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        all_final_scores.append(data["final_score"])

        if check_keyword_overdependence(data["component_scores"]):
            flagged_candidates.append({
                "candidate": data.get("candidate", filename),
                "reason": "Keyword-overdependence: high skill match, low other-component scores",
            })

    normalized = normalize_score_distribution(all_final_scores)

    result = {
        "total_candidates": len(score_files),
        "keyword_overdependence_flags": flagged_candidates,
        "raw_scores": all_final_scores,
        "normalized_scores": normalized,
    }

    output_path = os.path.join(OUTPUT_DIR, "fairness_check_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Done. Checked {len(score_files)} candidates. {len(flagged_candidates)} flagged for review.")
    print(f"See {output_path}")

if __name__ == "__main__":
    run()