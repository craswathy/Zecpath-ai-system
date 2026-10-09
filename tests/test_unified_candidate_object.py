import sys
sys.path.append(".")
from ats_engine.unified_candidate_object import build_unified_candidate_object

SCREENING = {"final_screening_score": {"final_screening_score": 76.0, "explanation": "demo"}}
HR = {"hr_interview_score": 80.0, "score_reliability": "reliable", "explanation": "demo"}
ATS = {"final_score": 82.0, "explanation": "demo"}


def test_complete_object_has_all_rounds():
    obj = build_unified_candidate_object("c1", "j1", ATS, SCREENING, HR, "technical")
    assert obj["metadata"]["status"] == "complete"
    assert obj["missing_rounds"] == []
    assert obj["rounds"]["ats"]["score"] == 82.0


def test_partial_object_flags_missing_rounds():
    obj = build_unified_candidate_object("c2", "j1", ATS)
    assert obj["metadata"]["status"] == "partial"
    assert "screening" in obj["missing_rounds"]


def test_empty_object_is_pending():
    obj = build_unified_candidate_object("c3", "j1")
    assert obj["metadata"]["status"] == "pending"
    assert obj["hiring_fit"]["percentage"] == 0.0


def test_object_follows_metadata_standard():
    obj = build_unified_candidate_object("c1", "j1", ATS, SCREENING, HR)
    for key in ("model_version", "timestamp", "stage", "status"):
        assert key in obj["metadata"]
    assert obj["candidate_id"] == "c1"
    assert obj["job_id"] == "j1"