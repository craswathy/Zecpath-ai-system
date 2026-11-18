import os
import sys
sys.path.append(".")

DOCS = ["FINAL_INTERNSHIP_REPORT.md", "KNOWLEDGE_TRANSFER_GUIDE.md",
        "KT_COMPLETION_RECORD.md", "FINAL_DEMO_RUNBOOK_DAY70.md",
        "INTERNSHIP_EVALUATION_PREP.md"]


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_handover_documents_exist():
    assert [d for d in DOCS if not os.path.exists(d)] == []


def test_final_report_is_fully_filled_in():
    assert "[ ]" not in read("FINAL_INTERNSHIP_REPORT.md"), "Fill every [ ] in the final report"


def test_runbook_covers_the_full_flow():
    text = read("FINAL_DEMO_RUNBOOK_DAY70.md")
    for stage in ("Resume", "ATS", "Screening", "Interview", "Decision"):
        assert stage in text


def test_kt_guide_covers_core_modules():
    text = read("KNOWLEDGE_TRANSFER_GUIDE.md")
    for module in ("ats_scorer.py", "decision_engine.py", "governance_controls.py",
                   "semantic_matcher.py", "polished_decision_service.py"):
        assert module in text