import sys
sys.path.append(".")
import json
import math
import pytest
from ats_engine.cross_round_aggregation_engine import aggregate_rounds
from ats_engine.decision_config import SELECTED, HOLD
from ats_engine.e2e_stages import run_hr, run_screening, run_technical
from ats_engine.governance_controls import AuditLog, check_access, find_expired, find_withdrawal_deletions, has_consent
from ats_engine.refined_decision_logic import decide_refined
from ats_engine.refined_intent import classify_follow_up_refined
from ats_engine.run_e2e_simulation import load_questions, run_pipeline, compare_with_humans
from ats_engine.run_stability_check import DECISION_KEYS, UNIFIED_KEYS, edge_cases, fuzz, validate_e2e_data
from ats_engine.technical_scoring_engine import score_answer
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.unified_candidate_score_object import build_unified_score_object

with open("data/e2e/e2e_candidates.json", encoding="utf-8") as f:
    DATA = json.load(f)
QUESTIONS = load_questions()
GOOD = {"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84}


def _decide(scores, context=None, role="technical"):
    return decide_refined(build_unified_score_object("c1", "j1", scores, role, None, context or {}))


# ---- scoring inconsistencies -------------------------------------------------
def test_empty_hr_interview_gives_no_score_not_zero():
    assert run_hr([], "technical")["score"] is None


def test_empty_screening_gives_no_score_and_does_not_divide_by_zero():
    assert run_screening([])["score"] is None


def test_empty_or_unknown_technical_answers_give_no_score():
    assert run_technical({}, QUESTIONS)["score"] is None
    assert run_technical({"zzz_1": "text"}, QUESTIONS)["score"] is None


def test_none_round_scores_do_not_crash():
    assert aggregate_rounds(None)["rounds_completed"] == 0


def test_bad_score_values_are_ignored():
    result = aggregate_rounds({"ats": float("nan"), "screening": float("inf"), "hr_interview": -5,
                               "technical_interview": 101, "machine_test": "85"})
    assert result["rounds_completed"] == 0 and len(result["invalid_rounds"]) == 5


def test_unknown_question_type_is_a_clear_error_and_is_skipped_by_the_stage():
    with pytest.raises(ValueError):
        score_answer({"id": "x", "type": "design", "level": "L1", "key_points": ["a"]}, "text", "x")
    index = dict(QUESTIONS, bad={"id": "bad", "type": "design", "level": "L1", "key_points": ["a"]})
    result = run_technical({"bad": "text", "mern_react_con_l1_01": "Props come from the parent and state belongs to the component."}, index)
    assert result["skipped_questions"] == 1 and result["score"] is not None


def test_non_text_technical_answer_does_not_crash():
    assert score_answer(QUESTIONS["mern_react_con_l1_01"], 123, "react")["score"] >= 0


# ---- conversation logic errors -----------------------------------------------
def test_cleanup_accepts_none_numbers_and_unicode():
    assert normalize_transcript_text(None) == ""
    assert normalize_transcript_text(12345) == "12345"
    assert normalize_transcript_text("um എനിക്ക് ഇഷ്ടമാണ് 😀 data")


def test_noun_use_of_kind_of_is_not_a_hedge_but_adverb_use_is():
    noun = "I handle this kind of data work every day and I clean the tables before reporting"
    assert classify_follow_up_refined(noun, False) != "clarification"
    assert classify_follow_up_refined("What kind of data do you use? Mostly sales tables from our reporting system every week", False) != "clarification"
    assert classify_follow_up_refined("I am kind of good at Excel", False) == "clarification"
    assert classify_follow_up_refined("Kind of, I did some projects in college but nothing serious", False) == "clarification"


# ---- data pipeline issues ----------------------------------------------------
def test_failed_resume_goes_to_hold_with_a_reupload_step():
    d = _decide(dict(GOOD, ats=None), {"resume_status": "unreadable"})
    assert d["decision"] == HOLD
    assert any(r["id"] == "RESUME_FAILED" for r in d["rules_triggered"])
    assert any("upload" in s for s in d["next_steps"])
    assert d["metadata"]["model_version"] == "decision_v1.2"


def test_failed_resume_is_recorded_even_when_the_score_already_says_hold():
    d = _decide({"ats": None, "screening": 80, "hr_interview": None, "technical_interview": None, "machine_test": None},
                {"resume_status": "unreadable"})
    assert d["decision"] == HOLD and any(r["id"] == "RESUME_FAILED" for r in d["rules_triggered"])


def test_readable_resume_does_not_change_the_decision():
    assert _decide(GOOD, {"resume_status": "ok"})["decision"] == SELECTED


def test_pipeline_records_a_wrong_data_key_as_an_error_and_sends_the_candidate_to_review():
    bad = dict(DATA["candidates"][0], hr="no_such_bank")
    j = run_pipeline(bad, DATA, QUESTIONS)
    assert j["errors"] and j["scores"]["hr_interview"] is None
    assert j["decision"]["decision"] == HOLD
    assert any(r["id"] == "STAGE_ERROR" for r in j["decision"]["rules_triggered"])


def test_a_failed_stage_gives_hold_even_with_strong_scores():
    d = _decide(GOOD, {"pipeline_errors": 2})
    assert d["decision"] == HOLD and any(r["id"] == "STAGE_ERROR" for r in d["rules_triggered"])


def test_failed_resume_candidate_in_the_e2e_set_is_on_hold():
    cand = [c for c in DATA["candidates"] if c["id"] == "e2e_08"][0]
    assert run_pipeline(cand, DATA, QUESTIONS)["decision"]["decision"] == HOLD


def test_data_validation_finds_bad_references():
    bad = json.loads(json.dumps(DATA))
    bad["candidates"][0]["hr"] = "nope"
    bad["candidates"][1]["machine"] = 500
    issues = validate_e2e_data(bad, QUESTIONS)
    assert any("hr 'nope'" in i for i in issues) and any("500" in i for i in issues)
    assert validate_e2e_data(DATA, QUESTIONS) == []


def test_preflight_reports_a_missing_file(monkeypatch):
    import ats_engine.run_stability_check as sc
    monkeypatch.setattr(sc, "REQUIRED_FILES", ["data/does_not_exist.json"])
    assert sc.preflight() == [("data/does_not_exist.json", False, "file not found")]


# ---- error handling in governance --------------------------------------------
def test_malformed_consent_counts_as_no_consent():
    assert has_consent({"purposes": ["x"]}, "interview_scoring") is False
    assert has_consent("yes", "interview_scoring") is False


def test_missing_user_is_denied_and_logged():
    audit = AuditLog()
    assert check_access(None, "view_report", {"candidate_id": "c", "job_id": "j"}, {}, audit) == (False, "no verified user")
    assert audit.entries[-1]["detail"]["allowed"] is False


def test_audit_log_accepts_dates_and_reloads(tmp_path):
    from datetime import datetime, timezone
    path = str(tmp_path / "a.jsonl")
    audit = AuditLog(path)
    audit.log("access", "u", "c", {"when": datetime.now(timezone.utc)})
    assert audit.verify() == (True, None)
    assert AuditLog(path).verify() == (True, None)


def test_unreadable_record_dates_and_missing_fields_do_not_stop_the_sweep():
    records = [{"id": "a", "type": "transcript", "created_at": "not a date"},
               {"id": "b", "type": "transcript", "created_at": "2020-01-01T00:00:00"},
               {"id": "c"}]
    assert [r["id"] for r in find_expired(records)] == ["b"]
    assert find_withdrawal_deletions([{"id": "a"}], "c1", {}) == []


# ---- stable outputs and edge cases -------------------------------------------
def test_output_contract_is_stable_for_a_normal_candidate():
    unified = build_unified_score_object("c1", "j1", GOOD, "technical", None, {})
    decision = decide_refined(unified)
    assert all(k in unified for k in UNIFIED_KEYS) and all(k in decision for k in DECISION_KEYS)


def test_fuzz_with_random_and_bad_input_finds_no_failures():
    result = fuzz(300, seed=11)
    assert result["failures"] == [], result["failures"][:3]


def test_every_edge_case_in_the_stability_battery_passes():
    failed = []
    for area, name, fn in edge_cases(QUESTIONS, DATA):
        try:
            ok = bool(fn())
        except Exception as exc:
            ok = False
            name += f" ({type(exc).__name__}: {exc})"
        if not ok:
            failed.append(f"[{area}] {name}")
    assert failed == []


def test_comparison_still_labels_an_ai_firmer_than_human_case():
    j = run_pipeline([c for c in DATA["candidates"] if c["id"] == "e2e_01"][0], DATA, QUESTIONS)
    rows = [{"candidate_id": "e2e_01", "reviewer": "x", "decision": "Hold / Review"}]
    assert compare_with_humans([j], rows)[0]["kind"] == "AI firmer than the human"


# ---- API ---------------------------------------------------------------------
fastapi_testclient = pytest.importorskip("fastapi.testclient")
pytest.importorskip("httpx")


def _client():
    from ats_engine import hr_api_server as api
    return api, fastapi_testclient.TestClient(api.app, raise_server_exceptions=False)


def _start(client):
    r = client.post("/api/v1/hr-interviews", json={"candidate_id": "c1", "job_id": "j1", "seniority": "fresher"})
    assert r.status_code == 201
    return r.json()["interview_id"]


def test_api_rejects_scores_outside_0_to_100():
    _, client = _client()
    iid = _start(client)
    body = {"per_turn_data": [{"is_off_topic": False, "is_vague_or_missing": False,
                               "communication_score": 150, "behavioral_confidence_score": -20}]}
    r = client.post(f"/api/v1/hr-interviews/{iid}/score", json=body)
    assert r.status_code == 422 and r.json()["error"]["code"] == "INVALID_REQUEST"
    assert any("communication_score" in f for f in r.json()["error"]["fields"])


def test_api_rejects_a_very_long_answer_and_empty_ids():
    _, client = _client()
    iid = _start(client)
    assert client.post(f"/api/v1/hr-interviews/{iid}/answers", json={"question_id": "q", "answer_text": "x" * 6000}).status_code == 422
    assert client.post("/api/v1/hr-interviews", json={"candidate_id": "", "job_id": "j", "seniority": "fresher"}).status_code == 422


def test_api_rejects_too_many_turns():
    _, client = _client()
    iid = _start(client)
    turn = {"is_off_topic": False, "is_vague_or_missing": False, "communication_score": 50, "behavioral_confidence_score": 50}
    assert client.post(f"/api/v1/hr-interviews/{iid}/score", json={"per_turn_data": [turn] * 201}).status_code == 422


def test_api_unknown_interview_uses_the_single_error_shape():
    _, client = _client()
    r = client.get("/api/v1/hr-interviews/hrint_9999")
    assert r.status_code == 404 and r.json()["error"]["code"] == "INTERVIEW_NOT_FOUND"


def test_api_unexpected_error_uses_the_single_error_shape_without_details(monkeypatch):
    api, client = _client()
    iid = _start(client)
    monkeypatch.setattr(api, "compute_hr_interview_score", lambda *a, **k: 1 / 0)
    r = client.post(f"/api/v1/hr-interviews/{iid}/score", json={"per_turn_data": []})
    assert r.status_code == 500 and r.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "division" not in r.text.lower() and "traceback" not in r.text.lower()