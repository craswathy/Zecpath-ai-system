from utils.logger import logger

# Interviews shorter than this are considered less reliable for scoring
MIN_RELIABLE_TURNS = 4


def normalize_for_interview_length(hr_score_result):
    """
    Adjust confidence in the score based on how many turns the interview
    actually had -- a 3-question interview and a 12-question interview
    shouldn't be compared with equal confidence, even if both produce a
    numeric score. Adds a reliability flag rather than changing the score
    itself, since shortening the interview isn't necessarily the
    candidate's fault (early call drop, time constraints).
    """
    turns_scored = hr_score_result.get("turns_scored", 0)

    if turns_scored == 0:
        reliability = "no_data"
    elif turns_scored < MIN_RELIABLE_TURNS:
        reliability = "low_reliability"
    else:
        reliability = "reliable"

    hr_score_result["score_reliability"] = reliability
    hr_score_result["reliability_note"] = (
        f"Based on {turns_scored} turn(s); "
        + ("sufficient for reliable scoring." if reliability == "reliable"
           else "fewer turns than recommended minimum, interpret with caution.")
    )

    logger.info(f"Interview length reliability: {reliability} ({turns_scored} turns)")
    return hr_score_result


def normalize_scores_across_candidates(score_list):
    """
    Min-max normalize final HR scores across a candidate pool -- same
    pattern as Day 15/35 -- so relative comparisons stay meaningful.
    """
    if not score_list:
        return []

    min_s, max_s = min(score_list), max(score_list)
    spread = max_s - min_s

    if spread == 0:
        return [50.0 for _ in score_list]

    return [round((s - min_s) / spread * 100, 1) for s in score_list]