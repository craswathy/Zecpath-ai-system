from rapidfuzz import fuzz
from utils.logger import logger

DEGREE_RANK = {
    "PhD": 4,
    "Master's": 3,
    "Bachelor's": 2,
    "Diploma": 1,
    "Higher Secondary": 0,
}


def score_degree_match(candidate_degree, required_degree):
    """
    Score how well a candidate's highest degree meets a job's requirement.
    1.0 = meets or exceeds requirement, partial credit if below.
    """
    if not candidate_degree or not required_degree:
        return 0.0

    cand_rank = DEGREE_RANK.get(candidate_degree, 0)
    req_rank = DEGREE_RANK.get(required_degree, 0)

    if cand_rank >= req_rank:
        return 1.0
    elif req_rank - cand_rank == 1:
        return 0.5
    else:
        return 0.0


def score_field_match(candidate_field, required_field):
    """Fuzzy-match field of study against a job's required field."""
    if not candidate_field or not required_field:
        return 0.0
    score = fuzz.token_sort_ratio(candidate_field.lower(), required_field.lower())
    return round(score / 100, 2)


def score_education_relevance(education_entries, required_degree, required_field):
    """
    Given a candidate's education entries and a job's requirement,
    return the best-matching entry with a combined relevance score.
    """
    if not education_entries:
        return {"relevance_score": 0.0, "best_match": None}

    scored = []
    for entry in education_entries:
        degree_score = score_degree_match(entry.get("degree"), required_degree)
        field_score = score_field_match(entry.get("field_of_study"), required_field)
        combined = round((degree_score * 0.6) + (field_score * 0.4), 2)
        scored.append({**entry, "relevance_score": combined})

    scored.sort(key=lambda x: -x["relevance_score"])
    logger.info(f"Best education match scored {scored[0]['relevance_score']}")
    return {"relevance_score": scored[0]["relevance_score"], "best_match": scored[0]}