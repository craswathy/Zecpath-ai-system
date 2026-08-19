from utils.logger import logger


def format_candidate_row(candidate):
    """One-line summary for a candidate, recruiter-readable."""
    name = candidate.get("candidate", "Unknown")
    score = candidate.get("final_score", 0)
    zone = candidate.get("decision_zone", "Unclassified")
    rank = candidate.get("rank", "-")
    return f"#{rank}  {name:<30}  Score: {score:>5.1f}/100   [{zone}]"


def generate_recruiter_report(ranked_candidates, job_title="Unspecified Role"):
    """
    Build a plain-text, recruiter-friendly ranked report:
    top candidates first, grouped by decision zone, with explanations.
    """
    lines = []
    lines.append(f"Candidate Ranking Report — {job_title}")
    lines.append("=" * 60)
    lines.append(f"Total candidates evaluated: {len(ranked_candidates)}")
    lines.append("")

    for zone in ["Shortlisted", "Needs Review", "Auto-Rejected"]:
        zone_candidates = [c for c in ranked_candidates if c["decision_zone"] == zone]
        lines.append(f"--- {zone} ({len(zone_candidates)}) ---")
        if not zone_candidates:
            lines.append("  (none)")
        for c in zone_candidates:
            lines.append("  " + format_candidate_row(c))
            if c.get("explanation"):
                lines.append(f"      Reason: {c['explanation']}")
        lines.append("")

    report = "\n".join(lines)
    logger.info("Generated recruiter report")
    return report