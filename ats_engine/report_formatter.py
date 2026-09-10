from utils.logger import logger


def format_report_as_text(report):
    """Render the structured screening report as a clean, readable plain-text document."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"AI SCREENING REPORT")
    lines.append("=" * 60)
    lines.append(f"Candidate: {report['candidate_id']}")
    lines.append(f"Job: {report['job_id']}")
    lines.append(f"Final Screening Score: {report['final_screening_score']}/100")
    lines.append(f"Communication Strength: {report['overall_communication_strength']}")
    lines.append("")

    lines.append("--- KEY HIGHLIGHTS ---")
    h = report["highlights"]
    lines.append(f"Salary Expectation: {h['salary_expectation'] or 'Not captured'}")
    lines.append(f"Availability: {h['availability'] or 'Not captured'}")
    lines.append(f"Skills Confirmed: {', '.join(h['skills_confirmed']) if h['skills_confirmed'] else 'None confirmed'}")
    lines.append("")

    lines.append("--- KEY ANSWERS ---")
    for category, value in report["key_answers"].items():
        lines.append(f"  {category}: {value}")
    lines.append("")

    lines.append("--- STRENGTHS ---")
    for s in report["strengths"]:
        lines.append(f"  + {s}")
    lines.append("")

    lines.append("--- RISKS / FLAGS ---")
    for r in report["risks"]:
        lines.append(f"  ! {r}")
    lines.append("")

    lines.append("--- MISSING DATA ---")
    if report["missing_data"]:
        for m in report["missing_data"]:
            lines.append(f"  ? {m}")
    else:
        lines.append("  None -- all expected categories covered")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def export_report(report, output_dir="data/screening_reports"):
    """Save the report in both JSON (machine-readable) and TXT (human-readable) formats."""
    import os, json
    os.makedirs(output_dir, exist_ok=True)

    candidate_id = report["candidate_id"]

    json_path = os.path.join(output_dir, f"{candidate_id}_screening_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    text_path = os.path.join(output_dir, f"{candidate_id}_screening_report.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(format_report_as_text(report))

    logger.info(f"Exported screening report for {candidate_id} to {output_dir}")
    return {"json_path": json_path, "text_path": text_path}