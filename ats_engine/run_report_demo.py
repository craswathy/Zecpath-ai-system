import json
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.hiring_report_generator import build_report
from ats_engine.report_exporter import export_report, render_text
from utils.logger import logger

DATA_PATH = "data/report_demo/report_candidates.json"
OUTPUT_DIR = "data/hiring_reports"


def run():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for c in data["candidates"]:
        unified = build_unified_score_object(
            c["candidate_id"], data["job_id"], c["scores"], data["role_category"],
            c.get("low_reliability_rounds"), c.get("context"),
        )
        decision = decide(unified)
        report = build_report(unified, decision, c.get("details"))
        paths = export_report(report, OUTPUT_DIR)
        rows.append((c["candidate_id"], report, paths))

    # Print the first report in full so it can be read and screenshotted
    print(render_text(rows[0][1]))
    print()
    print("=" * 70)
    print("ALL REPORTS")
    print("=" * 70)
    print(f"{'Candidate':<22}{'Decision':<16}{'Fit %':>7}{'Conf.':>7}{'Risks':>7}")
    for name, rep, paths in rows:
        h = rep["headline"]
        risks = [r for r in rep["risk_indicators"] if r["level"] in ("high", "medium")]
        print(f"{name:<22}{h['decision']:<16}{h['hiring_fit_percentage']:>7}{h['confidence_score']:>7}{len(risks):>7}")
    print(f"\nExported .html, .txt and .json for each candidate to {OUTPUT_DIR}/")
    logger.info("Report demo finished")


if __name__ == "__main__":
    run()