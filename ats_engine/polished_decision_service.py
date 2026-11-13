import math

from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit

MODEL_VERSION = "unified_v1.1"
ALLOWED = {"ats", "screening", "hr_interview"}


def _error(code, message, retryable, field=None):
    return {"error": {"code": code, "message": message, "retryable": retryable, "field": field},
            "decision": "Needs Manual Review", "model_version": MODEL_VERSION}


def validate(payload):
    """Return (round_scores, None) or (None, error_dict)."""
    if not isinstance(payload, dict) or not isinstance(payload.get("round_scores"), dict):
        return None, _error("BAD_REQUEST", "round_scores must be an object.", False, "round_scores")
    scores = payload["round_scores"]
    for name, value in scores.items():
        if name not in ALLOWED:
            return None, _error("UNKNOWN_ROUND", f"Unknown round '{name}'. Allowed: {sorted(ALLOWED)}.", False, name)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or math.isnan(value):
            return None, _error("INVALID_SCORE", f"{name} must be a number or null.", False, name)
        if not 0 <= value <= 100:
            return None, _error("SCORE_OUT_OF_RANGE", f"{name} must be between 0 and 100, got {value}.", False, name)
    if all(scores.get(k) is None for k in ALLOWED):
        return None, _error("NO_ROUND_SCORES", "At least one round score is required.", False, "round_scores")
    return {k: scores.get(k) for k in ALLOWED}, None


def safe_decide(payload):
    """Never raises. A system failure becomes manual review, never a rejection."""
    scores, error = validate(payload)
    if error:
        return error
    try:
        unified = compute_unified_score(scores, payload.get("role_category"))
        fit = classify_hiring_fit(unified)
    except Exception as exc:
        return _error("INTERNAL_ERROR", f"Scoring failed: {type(exc).__name__}", True)
    return {
        "candidate_id": payload.get("candidate_id"), "job_id": payload.get("job_id"),
        "hiring_fit_percentage": fit["hiring_fit_percentage"], "category": fit["fit_category"],
        "flags": fit["flags"], "missing_rounds": unified["missing_rounds"],
        "explanation": unified["explanation"], "model_version": MODEL_VERSION,
    }