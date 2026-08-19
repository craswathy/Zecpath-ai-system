from utils.logger import logger

# Configurable decision thresholds (0-100 scale, matches Day 13's final_score)
THRESHOLDS = {
    "auto_shortlist": 75,   # score >= this -> Shortlisted
    "review_zone_min": 50,  # score in [review_zone_min, auto_shortlist) -> Needs Review
    # anything below review_zone_min -> Auto-Rejected
}


def classify_candidate(score):
    """Assign a decision zone based on final ATS score."""
    if score >= THRESHOLDS["auto_shortlist"]:
        return "Shortlisted"
    elif score >= THRESHOLDS["review_zone_min"]:
        return "Needs Review"
    else:
        return "Auto-Rejected"


def rank_candidates(scored_candidates):
    """
    scored_candidates: list of dicts, each with at least {candidate, final_score}
    (Day 13's compute_ats_score output, one per candidate)

    Returns candidates sorted by score (highest first), each tagged with
    rank position and decision zone.
    """
    ranked = sorted(scored_candidates, key=lambda c: c["final_score"], reverse=True)

    for i, candidate in enumerate(ranked, start=1):
        candidate["rank"] = i
        candidate["decision_zone"] = classify_candidate(candidate["final_score"])

    logger.info(f"Ranked {len(ranked)} candidates")
    return ranked


def get_shortlist(ranked_candidates):
    """Return only candidates in the Shortlisted zone."""
    return [c for c in ranked_candidates if c["decision_zone"] == "Shortlisted"]


def get_review_zone(ranked_candidates):
    """Return only candidates needing manual recruiter review."""
    return [c for c in ranked_candidates if c["decision_zone"] == "Needs Review"]


def get_auto_rejected(ranked_candidates):
    """Return only auto-rejected candidates."""
    return [c for c in ranked_candidates if c["decision_zone"] == "Auto-Rejected"]