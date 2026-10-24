import json
import os
from ats_engine.cross_round_aggregation_engine import aggregate_rounds, ROUND_LABELS
from ats_engine.hiring_fit_calculator_v2 import classify_hiring_fit
from ats_engine.unified_candidate_score_object import build_unified_score_object
from utils.logger import logger

DATA_PATH = "data/cross_round_demo/cross_round_candidates.json"
OUTPUT_DIR = "data/unified_scores_v2"


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    job_id, role = data["job_id"], data["role_category"]

    # First pass: collect final-status results so ranks compare like with like
    pool = []
    for c in data["candidates"]:
        agg = aggregate_rounds(c["scores"], role, c.get("low_reliability_rounds"))
        fit = classify_hiring_fit(agg)
        if fit["status"] == "final":
            pool.append((fit["fit_category"], fit["hiring_fit_percentage"]))

    rows = []
    for c in data["candidates"]:
        obj = build_unified_score_object(
            c["candidate_id"], job_id, c["scores"], role,
            c.get("low_reliability_rounds"), c.get("context"), pool,
        )
        path = f"{OUTPUT_DIR}/{c['candidate_id']}_unified_v2.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

        print("=" * 66)
        print(f"{c['candidate_id']} | job: {job_id} | role weights: {obj['role_category']}")
        print("=" * 66)
        print(f"  {'Round':<22}{'Score':>7}{'Weight':>8}{'Points':>8}")
        for name, r in obj["rounds"].items():
            score = "-" if r["score"] is None else r["score"]
            weight = "-" if r["weight_used"] is None else r["weight_used"]
            points = "-" if r["points_contributed"] is None else r["points_contributed"]
            print(f"  {ROUND_LABELS[name]:<22}{score:>7}{weight:>8}{points:>8}")
        fit = obj["hiring_fit"]
        print(f"  Hiring fit: {fit['percentage']}% -> {fit['category']} ({fit['result_status']})")
        for flag in fit["flags"]:
            print(f"  Flag: {flag}")
        if obj["rank_in_pool"]:
            print(f"  Rank: {obj['rank_in_pool']['rank']} of {obj['rank_in_pool']['pool_size']} final candidates")
        if obj["context_not_scored"]:
            print(f"  Context (not scored): {obj['context_not_scored']}")
        print()
        rows.append((c["candidate_id"], obj))

    print("=" * 66)
    print("COMPARISON")
    print("=" * 66)
    print(f"{'Candidate':<20}{'Fit %':>7}  {'Category':<14}{'Status':<13}{'Rank':>6}")
    for name, o in rows:
        rank = o["rank_in_pool"]["rank"] if o["rank_in_pool"] else "-"
        print(f"{name:<20}{o['hiring_fit']['percentage']:>7}  {o['hiring_fit']['category']:<14}"
              f"{o['hiring_fit']['result_status']:<13}{rank:>6}")
    print(f"\nSaved objects to {OUTPUT_DIR}/")
    logger.info("Cross-round demo finished")


if __name__ == "__main__":
    run()