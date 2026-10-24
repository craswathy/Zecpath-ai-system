from datetime import datetime
from ats_engine.cross_round_config import MODEL_VERSION, ROUND_NAMES
from ats_engine.cross_round_aggregation_engine import aggregate_rounds, rank_in_pool
from ats_engine.hiring_fit_calculator_v2 import classify_hiring_fit
from utils.logger import logger


def build_unified_score_object(candidate_id, job_id, round_scores, role_category=None,
                               low_reliability_rounds=None, context=None, pool=None):
    """
    Build the unified candidate score object (Day 7 metadata standard).
    round_scores: dict with any of ats, screening, hr_interview, technical_interview, machine_test.
    context: optional extra information (integrity tag, behavioral label). Shown, never scored.
    pool: list of (category, hiring_fit_percentage) for comparable candidates; used for rank when the result is final.
    """
    aggregate = aggregate_rounds(round_scores, role_category, low_reliability_rounds)
    fit = classify_hiring_fit(aggregate)

    completed = aggregate["rounds_completed"]
    status = "complete" if completed == len(ROUND_NAMES) else ("partial" if completed > 0 else "pending")

    rounds = {}
    for name in ROUND_NAMES:
        score = aggregate["round_scores"].get(name)
        rounds[name] = {
            "score": score,
            "weight_used": aggregate["weights_used"].get(name),
            "points_contributed": aggregate["contributions"].get(name),
            "low_reliability": name in aggregate["low_reliability_rounds"],
        }

    rank = None
    if fit["status"] == "final":
        rank = rank_in_pool(fit["fit_category"], fit["hiring_fit_percentage"], pool)

    obj = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "role_category": aggregate["role_used"],
        "metadata": {
            "model_version": MODEL_VERSION,
            "timestamp": datetime.now().isoformat(),
            "stage": "unified_scored",
            "status": status,
        },
        "rounds": rounds,
        "hiring_fit": {
            "percentage": fit["hiring_fit_percentage"],
            "category": fit["fit_category"],
            "result_status": fit["status"],
            "flags": fit["flags"],
        },
        "missing_rounds": aggregate["missing_rounds"],
        "rank_in_pool": rank,
        "context_not_scored": context or {},
        "weights_used": aggregate["weights_used"],
        "explanation": aggregate["explanation"],
        "note": "Decision support only. A human recruiter makes the final decision.",
    }
    logger.info(f"Built unified v2 object for {candidate_id}: {fit['fit_category']}")
    return obj