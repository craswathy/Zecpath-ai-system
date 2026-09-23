from ats_engine.hr_interview_summary_builder import (
    identify_hr_strengths, identify_hr_weaknesses, identify_cultural_fit_indicators,
    identify_risk_flags, summarize_overall_hr_performance,
)
from utils.logger import logger


def build_hr_interview_summary(candidate_id, hr_score_result, aptitude_results,
                                communication_data, confidence_stress_data, contradiction_count):
    """Assemble the full structured HR interview summary object."""
    summary = {
        "candidate_id": candidate_id,
        "overall_hr_score": hr_score_result.get("hr_interview_score", 0),
        "overall_performance_summary": summarize_overall_hr_performance(hr_score_result),
        "strengths": identify_hr_strengths(hr_score_result, aptitude_results, communication_data),
        "weaknesses": identify_hr_weaknesses(hr_score_result, aptitude_results, communication_data),
        "cultural_fit_indicators": identify_cultural_fit_indicators(aptitude_results, confidence_stress_data),
        "risk_flags": identify_risk_flags(hr_score_result, confidence_stress_data, contradiction_count),
    }
    logger.info(f"Built HR interview summary for {candidate_id}")
    return summary


def generate_natural_language_narrative(summary):
    """
    Convert the structured summary into a short, readable paragraph --
    the kind of write-up a recruiter could paste directly into an
    internal note, rather than reading through a bulleted breakdown.
    """
    strengths_text = "; ".join(summary["strengths"][:2]).lower()
    weaknesses_text = "; ".join(summary["weaknesses"][:2]).lower()
    culture_text = summary["cultural_fit_indicators"][0].lower() if summary["cultural_fit_indicators"] else ""

    narrative = (
        f"{summary['overall_performance_summary']} "
        f"The candidate showed {strengths_text}. "
    )

    if "no significant weaknesses" not in weaknesses_text:
        narrative += f"Areas to probe further include {weaknesses_text}. "

    if culture_text and "insufficient data" not in culture_text:
        narrative += f"On cultural fit, {culture_text}. "

    if summary["risk_flags"] and "no significant risk" not in summary["risk_flags"][0].lower():
        narrative += f"Note: {summary['risk_flags'][0].lower()}."

    return narrative.strip()


def format_hr_summary_as_text(summary, narrative):
    """Render the full HR interview summary report as readable plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("AI HR INTERVIEW SUMMARY REPORT")
    lines.append("=" * 60)
    lines.append(f"Candidate: {summary['candidate_id']}")
    lines.append(f"Overall HR Score: {summary['overall_hr_score']}/100")
    lines.append("")
    lines.append("--- NARRATIVE SUMMARY ---")
    lines.append(narrative)
    lines.append("")
    lines.append("--- STRENGTHS ---")
    for s in summary["strengths"]:
        lines.append(f"  + {s}")
    lines.append("")
    lines.append("--- WEAKNESSES ---")
    for w in summary["weaknesses"]:
        lines.append(f"  - {w}")
    lines.append("")
    lines.append("--- CULTURAL FIT INDICATORS ---")
    for c in summary["cultural_fit_indicators"]:
        lines.append(f"  * {c}")
    lines.append("")
    lines.append("--- RISK FLAGS ---")
    for r in summary["risk_flags"]:
        lines.append(f"  ! {r}")
    lines.append("=" * 60)

    return "\n".join(lines)