import os
import json
from ats_engine.eligibility_engine import evaluate_eligibility
from utils.logger import logger

SCORES_DIR = "data/ats_scores"
SKILLS_DIR = "data/skills_extracted"
EXPERIENCE_DIR = "data/experience_parsed"
OUTPUT_DIR = "data/eligibility_results"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    score_files = [f for f in os.listdir(SCORES_DIR) if f.endswith("_ats_score.json")]

    logger.info(f"Evaluating eligibility for {len(score_files)} candidates")

    all_results = []

    for filename in score_files:
        score_data = load_json(os.path.join(SCORES_DIR, filename))
        candidate_id = score_data.get("candidate", filename)
        base_name = candidate_id.replace("_ats_score.json", "")

        skills_data = load_json(os.path.join(SKILLS_DIR, f"{base_name}_skills.json"))
        experience_data = load_json(os.path.join(EXPERIENCE_DIR, f"{base_name}_experience.json"))
        total_experience = experience_data.get("total_experience_years") if experience_data else None

        # Using a sample job_id for demo purposes -- in production this would
        # come from whichever job the candidate is being evaluated against.
        job_id = "jd_data_analyst"

        result = evaluate_eligibility(
            candidate_id=base_name,
            job_id=job_id,
            ats_score=score_data.get("final_score"),
            candidate_skills=skills_data,
            total_experience_years=total_experience,
        )

        all_results.append(result)

        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_eligibility.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    summary_path = os.path.join(OUTPUT_DIR, "eligibility_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    eligible_count = sum(1 for r in all_results if r["eligibility_tag"] == "Eligible")
    review_count = sum(1 for r in all_results if r["eligibility_tag"] == "Review")
    rejected_count = sum(1 for r in all_results if r["eligibility_tag"] == "Rejected")

    print(f"Done. Evaluated {len(all_results)} candidates.")
    print(f"  Eligible: {eligible_count}")
    print(f"  Review: {review_count}")
    print(f"  Rejected: {rejected_count}")
    print(f"Check {OUTPUT_DIR}/ for full outputs.")

if __name__ == "__main__":
    run()