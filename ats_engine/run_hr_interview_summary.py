import json
import os
from ats_engine.hr_interview_report_generator import (
    build_hr_interview_summary, generate_natural_language_narrative, format_hr_summary_as_text,
)
from ats_engine.contradiction_detector import scan_for_contradictions

def run():
    with open("data/hr_score_reports/cand_00123_hr_score.json", "r", encoding="utf-8") as f:
        hr_score_result = json.load(f)

    with open("data/aptitude_evaluation_results.json", "r", encoding="utf-8") as f:
        aptitude_results = json.load(f)

    with open("data/communication_score_results.json", "r", encoding="utf-8") as f:
        communication_data = json.load(f)

    with open("data/confidence_stress_results.json", "r", encoding="utf-8") as f:
        confidence_stress_data = json.load(f)

    with open("data/answer_understanding_result.json", "r", encoding="utf-8") as f:
        answers_data = json.load(f)

    contradictions = scan_for_contradictions(answers_data, "experience_years")

    candidate_id = "cand_00123"
    summary = build_hr_interview_summary(
        candidate_id, hr_score_result, aptitude_results,
        communication_data, confidence_stress_data, len(contradictions),
    )
    narrative = generate_natural_language_narrative(summary)
    report_text = format_hr_summary_as_text(summary, narrative)

    output_dir = "data/hr_interview_summaries"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, f"{candidate_id}_hr_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "narrative": narrative}, f, indent=2)

    with open(os.path.join(output_dir, f"{candidate_id}_hr_summary.txt"), "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Done. HR interview summary generated for {candidate_id}.")
    print()
    print(report_text)

if __name__ == "__main__":
    run()