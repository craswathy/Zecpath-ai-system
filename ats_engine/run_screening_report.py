import json
from ats_engine.screening_report_builder import build_screening_report
from ats_engine.report_formatter import export_report

def run():
    with open("data/answer_understanding_result.json", "r", encoding="utf-8") as f:
        answers_data = json.load(f)

    with open("data/screening_score_result.json", "r", encoding="utf-8") as f:
        screening_scores = json.load(f)

    with open("data/behavioral_analysis_result.json", "r", encoding="utf-8") as f:
        behavioral_report = json.load(f)

    report = build_screening_report(
        candidate_id="cand_00123",
        job_id="job_00045",
        answers_data=answers_data,
        screening_scores=screening_scores,
        behavioral_report=behavioral_report,
    )

    paths = export_report(report)

    print(f"Done. Screening report generated.")
    print(f"JSON: {paths['json_path']}")
    print(f"Text: {paths['text_path']}")
    print()
    print("--- Preview ---")
    from ats_engine.report_formatter import format_report_as_text
    print(format_report_as_text(report))

if __name__ == "__main__":
    run()