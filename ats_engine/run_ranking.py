import os
import json
from ats_engine.candidate_ranker import rank_candidates, get_shortlist, get_review_zone, get_auto_rejected
from ats_engine.recruiter_report import generate_recruiter_report
from utils.logger import logger

SCORES_DIR = "data/ats_scores"
OUTPUT_DIR = "data/rankings"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    score_files = [f for f in os.listdir(SCORES_DIR) if f.endswith("_ats_score.json")]
    scored_candidates = []

    for filename in score_files:
        with open(os.path.join(SCORES_DIR, filename), "r", encoding="utf-8") as f:
            scored_candidates.append(json.load(f))

    logger.info(f"Loaded {len(scored_candidates)} scored candidates for ranking")

    ranked = rank_candidates(scored_candidates)

    ranked_output_path = os.path.join(OUTPUT_DIR, "ranked_candidates.json")
    with open(ranked_output_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2)

    shortlist = get_shortlist(ranked)
    review_zone = get_review_zone(ranked)
    auto_rejected = get_auto_rejected(ranked)

    with open(os.path.join(OUTPUT_DIR, "shortlist.json"), "w", encoding="utf-8") as f:
        json.dump(shortlist, f, indent=2)

    report_text = generate_recruiter_report(ranked, job_title="Data Analyst")
    report_path = os.path.join(OUTPUT_DIR, "recruiter_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Done. Ranked {len(ranked)} candidates.")
    print(f"  Shortlisted: {len(shortlist)}")
    print(f"  Needs Review: {len(review_zone)}")
    print(f"  Auto-Rejected: {len(auto_rejected)}")
    print(f"Check {OUTPUT_DIR}/ for full outputs.")

if __name__ == "__main__":
    run()