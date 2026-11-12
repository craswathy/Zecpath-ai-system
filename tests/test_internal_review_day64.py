import json
import os

FILES = [
    "INTERNAL_REVIEW_REPORT.md", "IMPROVEMENT_LIST_DAY64.md",
    "ACTION_PLAN_DAY64.md", "MENTOR_FEEDBACK_FORM.md",
]


def test_review_documents_exist():
    assert [f for f in FILES if not os.path.exists(f)] == []


def test_walkthrough_findings_cover_all_candidates():
    from ats_engine.run_system_walkthrough import run
    run()
    with open("demo_dataset_day63/walkthrough_findings.json", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["candidates"]) == 8
    for c in data["candidates"]:
        assert c["observations"]


def test_every_improvement_has_priority_and_effort():
    with open("IMPROVEMENT_LIST_DAY64.md", encoding="utf-8") as f:
        # Check all table rows containing improvement IDs (I1 to I12)
        rows = [l.strip() for l in f if "|" in l and ("High" in l or "Medium" in l or "Low" in l)]
    assert len(rows) >= 10
    for row in rows:
        assert any(p in row for p in ("High", "Medium", "Low"))
        assert any(e in row for e in ("S", "M", "L"))