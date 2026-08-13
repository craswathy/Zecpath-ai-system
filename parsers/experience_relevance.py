from rapidfuzz import fuzz
from utils.logger import logger


def score_role_relevance(designation, job_title):
    """
    Compare a candidate's job title against a target job title.
    Returns a 0-1 similarity score using token-order-independent fuzzy match.
    """
    if not designation or not job_title:
        return 0.0
    score = fuzz.token_sort_ratio(designation.lower(), job_title.lower())
    return round(score / 100, 2)


def score_experience_relevance(experience_entries, job_title):
    """
    Attach a relevance_score to each experience entry, comparing its
    designation to the target job title. Used to weight how relevant a
    candidate's past roles are to a specific job posting.
    """
    scored = []
    for entry in experience_entries:
        relevance = score_role_relevance(entry.get("designation", ""), job_title)
        scored.append({**entry, "relevance_score": relevance})

    scored.sort(key=lambda x: -x["relevance_score"])
    logger.info(f"Scored {len(scored)} experience entries against job title '{job_title}'")
    return scored