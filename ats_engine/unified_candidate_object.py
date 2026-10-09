from datetime import datetime
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit
from utils.logger import logger

MODEL_VERSION = "unified_v1.0"


def build_unified_candidate_object(candidate_id, job_id, ats_result=None,
                                   screening_result=None, hr_result=None,
                                   role_category=None):
    """
    Build one unified score object for a candidate, combining ATS (Day 13),
    screening (Day 26), and HR interview (Day 37) results, plus the
    hiring-fit result (Day 41) and the Day 7 metadata standard.

    Any result can be None -- that round is treated as missing.
    """
    ats_score = ats_result.get("final_score") if ats_result else None
    screening_score = (
        screening_result["final_screening_score"]["final_screening_score"]
        if screening_result else None
    )
    hr_score = hr_result.get("hr_interview_score") if hr_result else None

    round_scores = {"ats": ats_score, "screening": screening_score, "hr_interview": hr_score}
    unified = compute_unified_score(round_scores, role_category=role_category)
    fit = classify_hiring_fit(unified)

    completed = unified["rounds_completed"]
    status = "complete" if completed == 3 else ("partial" if completed > 0 else "pending")

    obj = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "role_category": role_category or "default",
        "metadata": {
            "model_version": MODEL_VERSION,
            "timestamp": datetime.now().isoformat(),
            "stage": "unified_scored",
            "status": status,
        },
        "rounds": {
            "ats": {
                "score": ats_score,
                "explanation": ats_result.get("explanation") if ats_result else None,
            },
            "screening": {
                "score": screening_score,
                "explanation": screening_result["final_screening_score"].get("explanation") if screening_result else None,
            },
            "hr_interview": {
                "score": hr_score,
                "reliability": hr_result.get("score_reliability") if hr_result else None,
                "explanation": hr_result.get("explanation") if hr_result else None,
            },
        },
        "hiring_fit": {
            "percentage": fit["hiring_fit_percentage"],
            "category": fit["fit_category"],
            "flags": fit["flags"],
        },
        "weights_used": unified["weights_used"],
        "missing_rounds": unified["missing_rounds"],
        "explanation": unified["explanation"],
    }

    logger.info(f"Built unified candidate object for {candidate_id}: {fit['fit_category']}")
    return obj