import os
import sys
sys.path.append(".")

from ats_engine.polished_decision_service import safe_decide

FILES = [
    "MOCK_QA_BANK_DAY67.md", "DEMO_FEEDBACK_REPORT_DAY67.md",
    "DEMO_READINESS_CHECKLIST.md",
]


def test_day67_documents_exist():
    assert [f for f in FILES if not os.path.exists(f)] == []


def test_demo_dataset_is_present():
    assert len(os.listdir("demo_dataset_day63/resumes")) == 8


def test_api_demo_paths_behave():
    good = safe_decide({"round_scores": {"ats": 80, "screening": 70, "hr_interview": 65}})
    assert "error" not in good
    assert safe_decide({"round_scores": {"ats": 250}})["error"]["code"] == "SCORE_OUT_OF_RANGE"
    assert safe_decide({"round_scores": {}})["decision"] == "Needs Manual Review"