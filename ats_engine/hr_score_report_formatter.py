from utils.logger import logger


def format_hr_score_report(candidate_id, hr_score_result):
    """Render the HR interview score as a clean, readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("HR INTERVIEW SCORE REPORT")
    lines.append("=" * 60)
    lines.append(f"Candidate: {candidate_id}")
    lines.append(f"Final HR Interview Score: {hr_score_result['hr_interview_score']}/100")
    lines.append(f"Reliability: {hr_score_result.get('score_reliability', 'unknown')}")
    lines.append(f"  {hr_score_result.get('reliability_note', '')}")
    lines.append("")

    lines.append("--- COMPONENT BREAKDOWN ---")
    for component, score in hr_score_result["component_scores"].items():
        weight = hr_score_result["weights_used"].get(component, 0)
        lines.append(f"  {component.title()}: {score} (weight {weight})")
    lines.append("")

    lines.append(f"Turns Scored: {hr_score_result['turns_scored']}")
    lines.append("=" * 60)

    return "\n".join(lines)


def export_hr_score_report(candidate_id, hr_score_result, output_dir="data/hr_score_reports"):
    """Save the HR score report in JSON and readable text formats."""
    import os, json
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, f"{candidate_id}_hr_score.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(hr_score_result, f, indent=2)

    text_path = os.path.join(output_dir, f"{candidate_id}_hr_score.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(format_hr_score_report(candidate_id, hr_score_result))

    logger.info(f"Exported HR score report for {candidate_id}")
    return {"json_path": json_path, "text_path": text_path}