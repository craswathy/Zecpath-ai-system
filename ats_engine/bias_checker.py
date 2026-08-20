from utils.logger import logger


def check_keyword_overdependence(component_scores):
    """
    Flag if a candidate's score is driven almost entirely by keyword/skill
    match while other components (experience, education, semantic fit)
    contributed very little -- a sign of keyword-stuffing bias rather than
    genuine fit.
    """
    skill = component_scores.get("skill_match") or 0
    others = [
        v for k, v in component_scores.items()
        if k != "skill_match" and v is not None
    ]
    avg_others = sum(others) / len(others) if others else 0

    if skill > 0.8 and avg_others < 0.3:
        return True
    return False


def check_score_distribution_bias(all_scores, group_field, candidate_groups):
    """
    Compare average scores across candidate groups (e.g. by graduation
    institution tier, location, or another attribute NOT used in scoring)
    to flag systematic score gaps worth human review.

    all_scores: list of final_score values, aligned with candidate_groups
    candidate_groups: list of group labels, same order/length as all_scores
    """
    from collections import defaultdict

    group_totals = defaultdict(list)
    for score, group in zip(all_scores, candidate_groups):
        group_totals[group].append(score)

    group_averages = {
        group: round(sum(vals) / len(vals), 1)
        for group, vals in group_totals.items()
    }

    if len(group_averages) < 2:
        return {"flag": False, "group_averages": group_averages}

    spread = max(group_averages.values()) - min(group_averages.values())
    flag = spread > 15  # more than 15-point average gap between groups is worth reviewing

    if flag:
        logger.info(f"Bias check flagged a {spread}-point score gap across '{group_field}' groups")

    return {"flag": flag, "group_averages": group_averages, "spread": spread}