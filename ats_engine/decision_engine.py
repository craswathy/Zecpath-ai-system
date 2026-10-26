from datetime import datetime
from ats_engine.decision_config import (
    MODEL_VERSION, SELECTED, HOLD, REJECTED, CATEGORY_TO_DECISION, SELECT_LINE, REJECT_LINE,
    BORDER_MARGIN, CONFIDENCE_WEIGHTS, AGREEMENT_RANGE, MARGIN_FULL, PRELIMINARY_CONFIDENCE_CAP,
    INTEGRITY_PENALTY, MIN_CONFIDENCE, HIGH_CONFIDENCE, MEDIUM_CONFIDENCE, REQUIRED_ROUNDS, ROUND_FLOOR,
)
from utils.logger import logger

ROUND_LABELS = {
    "ats": "ATS", "screening": "Screening", "hr_interview": "HR interview",
    "technical_interview": "Technical interview", "machine_test": "Machine test",
}


def compute_confidence(unified_obj, integrity_priority=None):
    """
    How much to trust the score-based result (0 to 1). Four parts:
    completeness (share of rounds scored), reliability (share not marked low reliability),
    agreement (how close the round scores are), margin (distance from a decision line).
    Integrity risk lowers it. A preliminary result is capped.
    """
    rounds = unified_obj["rounds"]
    scored = {n: r for n, r in rounds.items() if r["score"] is not None}
    if not scored:
        return {"score": 0.0, "band": "low", "components": {}}

    scores = [r["score"] for r in scored.values()]
    pct = unified_obj["hiring_fit"]["percentage"]
    components = {
        "completeness": len(scored) / len(rounds),
        "reliability": sum(1 for r in scored.values() if not r["low_reliability"]) / len(scored),
        "agreement": 1 - min((max(scores) - min(scores)) / AGREEMENT_RANGE, 1),
        "margin": min(min(abs(pct - SELECT_LINE), abs(pct - REJECT_LINE)) / MARGIN_FULL, 1),
    }
    total = sum(components[k] * CONFIDENCE_WEIGHTS[k] for k in components)
    total -= INTEGRITY_PENALTY.get(integrity_priority, 0.0)
    if unified_obj["hiring_fit"]["result_status"] != "final":
        total = min(total, PRELIMINARY_CONFIDENCE_CAP)
    total = round(max(0.0, min(total, 1.0)), 2)

    if total >= HIGH_CONFIDENCE:
        band = "high"
    elif total >= MEDIUM_CONFIDENCE:
        band = "medium"
    else:
        band = "low"
    return {"score": total, "band": band, "components": {k: round(v, 2) for k, v in components.items()}}


def decide(unified_obj):
    """
    Rule + score hybrid. The score gives a starting decision, then safety rules can move it
    to Hold / Review. No rule can move a candidate toward Selected or Rejected.
    Integrity and behavioral results never cause a rejection.
    """
    fit = unified_obj["hiring_fit"]
    pct, category, status = fit["percentage"], fit["category"], fit["result_status"]
    context = unified_obj.get("context_not_scored", {})
    integrity = context.get("integrity_review_priority")
    behavior = context.get("behavioral_label")
    role = unified_obj.get("role_category", "default")

    confidence = compute_confidence(unified_obj, integrity)
    score_decision = CATEGORY_TO_DECISION.get(category, HOLD)

    rules, next_steps = [], []

    def add_rule(rule_id, reason, forces_hold, step=None):
        rules.append({"id": rule_id, "reason": reason, "moves_to_hold": forces_hold})
        if step:
            next_steps.append(step)

    can_move = score_decision in (SELECTED, REJECTED)

    if status != "final":
        add_rule("NOT_FINAL", f"Result is {status}: too few rounds scored", can_move,
                 "Complete the missing rounds, then run the decision again.")

    required = REQUIRED_ROUNDS.get(role, REQUIRED_ROUNDS["default"])
    missing_required = [r for r in required if unified_obj["rounds"][r]["score"] is None]
    if missing_required:
        names = ", ".join(ROUND_LABELS[r] for r in missing_required)
        add_rule("REQUIRED_ROUND_MISSING", f"Required round not scored: {names}", can_move,
                 f"Complete the {names} before deciding.")

    weak = [ROUND_LABELS[n] for n, r in unified_obj["rounds"].items()
            if r["score"] is not None and r["score"] < ROUND_FLOOR]
    if weak:
        add_rule("WEAK_ROUND", f"Round below {ROUND_FLOOR}: {', '.join(weak)}", False,
                 None if score_decision == REJECTED else f"Review the weak round ({', '.join(weak)}) before deciding.")

    if integrity == "High":
        add_rule("INTEGRITY_HIGH", "Integrity review priority is High", can_move,
                 "Recruiter reviews the integrity timeline. Consider a short live follow-up interview.")
    elif integrity == "Medium":
        add_rule("INTEGRITY_MEDIUM", "Integrity review priority is Medium (confidence lowered)", False,
                 "Consider a verification follow-up question before any offer.")

    if score_decision == SELECTED and abs(pct - SELECT_LINE) < BORDER_MARGIN:
        add_rule("BORDERLINE", f"{pct}% is within {BORDER_MARGIN} points of the selection line ({SELECT_LINE})",
                 True, "Score is close to the decision line. Recruiter reviews the round details.")
    if score_decision == REJECTED and abs(pct - REJECT_LINE) < BORDER_MARGIN:
        add_rule("BORDERLINE", f"{pct}% is within {BORDER_MARGIN} points of the rejection line ({REJECT_LINE})",
                 True, "Score is close to the decision line. Recruiter reviews the round details.")

    if score_decision in MIN_CONFIDENCE and confidence["score"] < MIN_CONFIDENCE[score_decision]:
        add_rule("LOW_CONFIDENCE",
                 f"Confidence {confidence['score']} is below {MIN_CONFIDENCE[score_decision]} needed for {score_decision}",
                 True, "Confidence is too low for a firm recommendation. Review the round details.")

    decision = HOLD if any(r["moves_to_hold"] for r in rules) else score_decision

    if decision == SELECTED:
        recommendation = "Recommend moving this candidate to the next stage."
        next_steps.append("A recruiter confirms the decision before any offer or message to the candidate.")
    elif decision == REJECTED:
        recommendation = "Recommend not moving this candidate forward on current evidence."
        next_steps.append("A recruiter confirms before the candidate is told. Offer a feedback and review route.")
    else:
        recommendation = "A recruiter should review this candidate before any decision."
        if not next_steps:
            next_steps.append("Score is in the review range. Recruiter reviews the round details and decides.")

    risk_factors = {
        "integrity": {"review_priority": integrity or "not available",
                      "effect": ("moves decision to Hold / Review" if integrity == "High"
                                 else "lowers confidence" if integrity == "Medium" else "none")},
        "behavioral": {"label": behavior or "not available",
                       "effect": "none (context only, never changes a decision)"},
    }

    parts = [f"Hiring fit {pct}% ({category}, {status}) suggests {score_decision}."]
    for r in rules:
        parts.append(f"{r['id']}: {r['reason']}" + (" -> moved to Hold / Review." if r["moves_to_hold"] else "."))
    parts.append(f"Confidence {confidence['score']} ({confidence['band']}).")
    parts.append(f"Final recommendation: {decision}.")

    logger.info(f"Decision for {unified_obj['candidate_id']}: {decision} (confidence {confidence['score']})")
    return {
        "candidate_id": unified_obj["candidate_id"],
        "job_id": unified_obj["job_id"],
        "role_category": role,
        "metadata": {"model_version": MODEL_VERSION, "timestamp": datetime.now().isoformat(),
                     "stage": "decision", "status": "recommended"},
        "decision": decision,
        "recommendation": recommendation,
        "score_based_decision": score_decision,
        "hiring_fit": {"percentage": pct, "category": category, "result_status": status},
        "rules_triggered": rules,
        "confidence": confidence,
        "risk_factors": risk_factors,
        "next_steps": next_steps,
        "human_review": {"required": True, "final_decision": None, "reviewed_by": None},
        "explanation": " ".join(parts),
        "note": "Recommendation only. A human recruiter makes the final decision.",
    }


def format_decision_summary(d):
    """Short recruiter-readable summary of one decision object."""
    lines = [f"{d['candidate_id']}: {d['decision'].upper()} (confidence {d['confidence']['score']}, {d['confidence']['band']})",
             f"  Hiring fit: {d['hiring_fit']['percentage']}% {d['hiring_fit']['category']} ({d['hiring_fit']['result_status']})",
             f"  Score alone suggests: {d['score_based_decision']}"]
    for r in d["rules_triggered"]:
        lines.append(f"  Rule {r['id']}: {r['reason']}" + (" [moved to Hold / Review]" if r["moves_to_hold"] else ""))
    lines.append(f"  Integrity: {d['risk_factors']['integrity']['review_priority']} | "
                 f"Behavioral: {d['risk_factors']['behavioral']['label']} (context only)")
    for step in d["next_steps"]:
        lines.append(f"  Next: {step}")
    return "\n".join(lines)