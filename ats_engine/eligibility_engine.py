from ats_engine.eligibility_config import get_rules
from utils.logger import logger


def check_mandatory_skills(candidate_skills, mandatory_skills):
    """Return (passed: bool, missing: list) for mandatory skill requirements."""
    if not mandatory_skills:
        return True, []

    candidate_skill_names = {s["skill"].lower() for s in (candidate_skills or [])}
    missing = [s for s in mandatory_skills if s.lower() not in candidate_skill_names]
    return len(missing) == 0, missing


def check_experience_range(total_experience_years, min_years, max_years):
    """Return True if candidate's total experience falls within the job's range."""
    if total_experience_years is None:
        return False  # can't confirm eligibility without data -- fail safe, route to review
    return min_years <= total_experience_years <= max_years


def check_location(candidate_location, allowed_locations):
    """Return True if no location restriction, or candidate matches an allowed location."""
    if not allowed_locations:
        return True
    if not candidate_location:
        return False
    return candidate_location.strip().lower() in [loc.lower() for loc in allowed_locations]


def evaluate_eligibility(candidate_id, job_id, ats_score, candidate_skills,
                          total_experience_years, candidate_location=None):
    """
    Combine rule-based checks (mandatory skills, experience range, location)
    with the score-based ATS result (Day 13) to produce one eligibility tag:
    Eligible / Review / Rejected.
    """
    rules = get_rules(job_id)
    reasons = []

    score_ok = ats_score is not None and ats_score >= rules["min_ats_score"]
    if not score_ok:
        reasons.append(f"ATS score {ats_score} below minimum {rules['min_ats_score']}")

    skills_ok, missing_skills = check_mandatory_skills(candidate_skills, rules["mandatory_skills"])
    if not skills_ok:
        reasons.append(f"Missing mandatory skills: {', '.join(missing_skills)}")

    experience_ok = check_experience_range(
        total_experience_years, rules["min_experience_years"], rules["max_experience_years"]
    )
    if not experience_ok:
        if total_experience_years is None:
            reasons.append("Experience data unavailable")
        else:
            reasons.append(
                f"Experience {total_experience_years} yrs outside range "
                f"[{rules['min_experience_years']}-{rules['max_experience_years']}]"
            )

    location_ok = check_location(candidate_location, rules["allowed_locations"])
    if not location_ok:
        reasons.append(f"Location '{candidate_location}' not in allowed list")

    # Decision logic:
    # - All hard checks pass -> Eligible
    # - Score is close (within 5 points) or exactly one soft check fails -> Review
    # - Multiple failures or score far below minimum -> Rejected
    all_pass = score_ok and skills_ok and experience_ok and location_ok
    failures = sum([not score_ok, not skills_ok, not experience_ok, not location_ok])

    if all_pass:
        tag = "Eligible"
    elif failures == 1 and ats_score is not None and ats_score >= rules["min_ats_score"] - 5:
        tag = "Review"
    else:
        tag = "Rejected"

    logger.info(f"Eligibility for {candidate_id} vs {job_id}: {tag}")

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "eligibility_tag": tag,
        "checks": {
            "ats_score_ok": score_ok,
            "mandatory_skills_ok": skills_ok,
            "experience_range_ok": experience_ok,
            "location_ok": location_ok,
        },
        "reasons": reasons if reasons else ["All eligibility checks passed"],
    }