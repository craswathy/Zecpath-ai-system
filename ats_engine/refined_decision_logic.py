import logging
from contextlib import contextmanager
from ats_engine.decision_config import SELECTED, HOLD, REJECTED
from ats_engine.decision_engine import decide, ROUND_LABELS
from utils.logger import logger

REFINED_VERSION = "decision_v1.1"

# Day 54 refinements. Values chosen on the development set (see run_optimization_analysis.py).
CRITICAL_ROUNDS = {"technical": ["technical_interview", "machine_test"], "senior": ["technical_interview"]}
CRITICAL_FLOOR = 65     # a role's key round below this cannot give Selected
SPREAD_LIMIT = 50       # best round minus worst round at or above this cannot give Selected or Rejected


def decide_refined(unified_obj, critical_floor=CRITICAL_FLOOR, spread_limit=SPREAD_LIMIT):
    """
    Day 52 decision plus two consistency rules. The new rules can only move a
    Selected or Rejected result to Hold / Review, never the other way.
    """
    d = decide(unified_obj)
    if d["decision"] == HOLD:
        return d

    scores = {n: r["score"] for n, r in unified_obj["rounds"].items() if r["score"] is not None}
    role = unified_obj.get("role_category", "default")
    found = []

    weak_key = [ROUND_LABELS[n] for n in CRITICAL_ROUNDS.get(role, []) if n in scores and scores[n] < critical_floor]
    if d["decision"] == SELECTED and weak_key:
        found.append(("CRITICAL_ROUND_WEAK",
                      f"Key round for this role below {critical_floor}: {', '.join(weak_key)}",
                      f"Review the key round ({', '.join(weak_key)}) before any decision."))

    if len(scores) >= 2 and max(scores.values()) - min(scores.values()) >= spread_limit:
        found.append(("ROUNDS_DISAGREE",
                      f"Rounds disagree: best {max(scores.values())}, worst {min(scores.values())} (gap of {spread_limit} or more)",
                      "Rounds disagree. A recruiter checks which rounds are reliable."))

    if not found:
        return d

    for rule_id, reason, step in found:
        d["rules_triggered"].append({"id": rule_id, "reason": reason, "moves_to_hold": True})
        d["next_steps"].insert(0, step)
    d["decision"] = HOLD
    d["recommendation"] = "A recruiter should review this candidate before any decision."
    d["next_steps"] = [s for s in d["next_steps"] if "confirms" not in s]
    d["metadata"]["model_version"] = REFINED_VERSION
    d["explanation"] += " Day 54 rules: " + "; ".join(f"{r}: {why}" for r, why, _ in found) + f". Final recommendation: {HOLD}."
    logger.info(f"Refined decision for {unified_obj['candidate_id']}: {HOLD} ({', '.join(r for r, _, _ in found)})")
    return d


@contextmanager
def batch_mode():
    """Silence per-candidate INFO logging while scoring many candidates, then restore it."""
    old_level = logger.level
    logger.setLevel(logging.WARNING)
    try:
        yield
    finally:
        logger.setLevel(old_level)