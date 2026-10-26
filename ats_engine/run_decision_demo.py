import json
import os
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide, format_decision_summary
from utils.logger import logger

DATA_PATH = "data/decision_demo/decision_candidates.json"
OUTPUT_DIR = "data/decision_results"


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for c in data["candidates"]:
        unified = build_unified_score_object(
            c["candidate_id"], data["job_id"], c["scores"], data["role_category"],
            c.get("low_reliability_rounds"), c.get("context"),
        )
        decision = decide(unified)
        print(format_decision_summary(decision))
        print()
        with open(f"{OUTPUT_DIR}/{c['candidate_id']}_decision.json", "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2)
        rows.append(decision)

    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"{'Candidate':<22}{'Fit %':>7}  {'Score says':<15}{'Decision':<15}{'Conf.':>6}")
    for d in rows:
        print(f"{d['candidate_id']:<22}{d['hiring_fit']['percentage']:>7}  {d['score_based_decision']:<15}"
              f"{d['decision']:<15}{d['confidence']['score']:>6}")
    print(f"\nSaved decisions to {OUTPUT_DIR}/")
    logger.info("Decision demo finished")


if __name__ == "__main__":
    run()