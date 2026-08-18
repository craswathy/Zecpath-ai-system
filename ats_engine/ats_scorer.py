from ats_engine.scoring_config import get_weights
from utils.logger import logger


def _skill_match_score(skills_extracted, jd_required_skills):
    """
    skills_extracted: list of {skill, confidence, ...} from Day 9
    jd_required_skills: list of {name, mandatory} from Day 6
    """
    if not jd_required_skills:
        return None  # missing data -- can't score this component

    required_names = {s["name"].lower() for s in jd_required_skills}
    if not required_names:
        return None

    candidate_skills = {s["skill"].lower(): s["confidence"] for s in (skills_extracted or [])}

    matched_confidence_sum = 0.0
    for req in required_names:
        if req in candidate_skills:
            matched_confidence_sum += candidate_skills[req]

    score = matched_confidence_sum / len(required_names)
    return round(min(1.0, score), 3)


def _experience_score(experience_summary):
    """experience_summary: output from Day 10's compute_experience_summary + relevance scoring"""
    if not experience_summary or "experience_entries" not in experience_summary:
        return None

    entries = experience_summary["experience_entries"]
    if not entries:
        return None

    top_relevance = max((e.get("relevance_score", 0) for e in entries), default=0)
    return round(top_relevance, 3)


def _education_score(education_relevance):
    """education_relevance: output from Day 11's score_education_relevance"""
    if not education_relevance or education_relevance.get("relevance_score") is None:
        return None
    return round(education_relevance["relevance_score"], 3)


def _semantic_score(semantic_match):
    """semantic_match: output from Day 12's compare_resume_to_jd"""
    if not semantic_match or "overall_similarity" not in semantic_match:
        return None
    return round(semantic_match["overall_similarity"], 3)


def compute_ats_score(candidate_data, jd_data, role_category=None):
    """
    Combine all four scoring components into one explainable ATS score.

    candidate_data: dict with keys 'skills', 'experience_summary', 'education_relevance', 'semantic_match'
    jd_data: dict with key 'required_skills'
    role_category: optional string ('technical', 'business', 'entry_level') to pick weight profile
    """
    weights = get_weights(role_category)

    raw_scores = {
        "skill_match": _skill_match_score(candidate_data.get("skills"), jd_data.get("required_skills")),
        "experience_relevance": _experience_score(candidate_data.get("experience_summary")),
        "education_alignment": _education_score(candidate_data.get("education_relevance")),
        "semantic_similarity": _semantic_score(candidate_data.get("semantic_match")),
    }

    # Handle missing data: redistribute weight of missing components across available ones
    available = {k: v for k, v in raw_scores.items() if v is not None}
    missing = [k for k, v in raw_scores.items() if v is None]

    if not available:
        return {
            "final_score": 0.0,
            "component_scores": raw_scores,
            "weights_used": weights,
            "missing_components": missing,
            "explanation": "No scoreable data available for this candidate/job pair.",
        }

    available_weight_sum = sum(weights[k] for k in available)
    adjusted_weights = {k: round(weights[k] / available_weight_sum, 3) for k in available}

    final_score = sum(available[k] * adjusted_weights[k] for k in available)
    final_score = round(final_score * 100, 1)  # scale to 0-100

    explanation_parts = [
        f"{k.replace('_', ' ').title()}: {available[k]:.2f} (weight {adjusted_weights[k]:.2f})"
        for k in available
    ]
    if missing:
        explanation_parts.append(
            f"Missing data for: {', '.join(m.replace('_', ' ') for m in missing)} -- weight redistributed."
        )

    logger.info(f"ATS score computed: {final_score}/100")

    return {
        "final_score": final_score,
        "component_scores": raw_scores,
        "weights_used": adjusted_weights,
        "missing_components": missing,
        "explanation": " | ".join(explanation_parts),
    }