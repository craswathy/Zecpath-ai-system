import sys
sys.path.append(".")
from datetime import datetime, timedelta, timezone
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.governance_controls import (
    AuditLog, log_score, log_decision, log_human_decision, is_allowed, has_consent, check_access,
    find_expired, find_withdrawal_deletions, ROLE_PERMISSIONS, RETENTION_DAYS,
)

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)
RECRUITER = {"user_id": "r1", "role": "recruiter", "assigned_jobs": ["j1"]}
CANDIDATE = {"candidate_id": "c1", "job_id": "j1"}
CONSENT = {"purposes": {"interview_scoring": {"granted_at": "2026-10-01T00:00:00", "withdrawn_at": None}}}
WITHDRAWN = {"purposes": {"interview_scoring": {"granted_at": "2026-10-01T00:00:00", "withdrawn_at": "2026-10-10T00:00:00"}}}
SCORES = {"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84}


def test_recruiter_can_view_own_job_candidate():
    assert is_allowed(RECRUITER, "view_report", CANDIDATE)[0] is True


def test_recruiter_cannot_view_other_job_candidate():
    allowed, reason = is_allowed(RECRUITER, "view_report", {"candidate_id": "c2", "job_id": "j2"})
    assert allowed is False and "assigned jobs" in reason


def test_hiring_manager_cannot_view_transcripts():
    manager = {"user_id": "m1", "role": "hiring_manager", "assigned_jobs": ["j1"]}
    assert is_allowed(manager, "view_transcript", CANDIDATE)[0] is False


def test_admin_cannot_see_candidate_data():
    admin = {"user_id": "a1", "role": "admin"}
    for action in ("view_report", "view_scores", "view_transcript", "export_report"):
        assert is_allowed(admin, action, CANDIDATE)[0] is False


def test_auditor_is_read_only_on_the_audit_log():
    assert ROLE_PERMISSIONS["auditor"] == {"view_audit_log"}


def test_unknown_role_has_no_access():
    assert is_allowed({"user_id": "x", "role": "stranger"}, "view_report", CANDIDATE)[0] is False


def test_consent_granted_withdrawn_and_missing():
    assert has_consent(CONSENT, "interview_scoring") is True
    assert has_consent(WITHDRAWN, "interview_scoring") is False
    assert has_consent(CONSENT, "video_behavior_analysis") is False
    assert has_consent(None, "interview_scoring") is False
    assert has_consent(None, None) is True


def test_access_without_consent_is_denied_and_logged():
    audit = AuditLog()
    allowed, reason = check_access(RECRUITER, "view_report", CANDIDATE, WITHDRAWN, audit)
    assert allowed is False and "consent" in reason
    assert audit.entries[-1]["detail"]["allowed"] is False


def test_every_access_attempt_is_logged_allowed_or_denied():
    audit = AuditLog()
    check_access(RECRUITER, "view_report", CANDIDATE, CONSENT, audit)
    check_access(RECRUITER, "manage_users", CANDIDATE, CONSENT, audit)
    assert [e["detail"]["allowed"] for e in audit.entries] == [True, False]


def test_audit_chain_is_intact_then_detects_editing():
    audit = AuditLog()
    for i in range(4):
        audit.log("access", "u1", "c1", {"n": i})
    assert audit.verify() == (True, None)
    audit.entries[1]["detail"]["n"] = 99
    assert audit.verify() == (False, 2)


def test_audit_chain_detects_a_removed_entry():
    audit = AuditLog()
    for i in range(4):
        audit.log("access", "u1", "c1", {"n": i})
    del audit.entries[1]
    assert audit.verify()[0] is False


def test_audit_log_reloads_from_file(tmp_path):
    path = str(tmp_path / "audit.jsonl")
    first = AuditLog(path)
    first.log("access", "u1", "c1", {"n": 1})
    first.log("access", "u1", "c1", {"n": 2})
    second = AuditLog(path)
    assert len(second.entries) == 2 and second.verify() == (True, None)
    second.log("access", "u1", "c1", {"n": 3})
    assert len(AuditLog(path).entries) == 3


def test_score_and_decision_logs_hold_key_facts_and_no_transcript_text():
    audit = AuditLog()
    unified = build_unified_score_object("c1", "j1", SCORES, "technical")
    decision = decide(unified)
    score_entry = log_score(audit, unified)
    decision_entry = log_decision(audit, decision)
    assert score_entry["event"] == "score" and score_entry["detail"]["round_scores"]["ats"] == 85
    assert "model_version" in score_entry["detail"] and "weights_used" in score_entry["detail"]
    assert decision_entry["detail"]["human_review_required"] is True
    assert decision_entry["detail"]["final_decision"] is None
    assert "transcript" not in str(score_entry).lower() and "answer" not in str(decision_entry).lower()


def test_human_decision_is_logged_with_the_reviewer():
    audit = AuditLog()
    entry = log_human_decision(audit, RECRUITER, "c1", "Selected", "Read the report")
    assert entry["event"] == "human_decision" and entry["actor"] == "r1"


def test_retention_finds_only_expired_records_and_skips_legal_hold():
    old = (NOW - timedelta(days=RETENTION_DAYS["transcript"] + 1)).isoformat()
    fresh = (NOW - timedelta(days=10)).isoformat()
    records = [
        {"id": "a", "candidate_id": "c1", "type": "transcript", "created_at": old},
        {"id": "b", "candidate_id": "c1", "type": "transcript", "created_at": fresh},
        {"id": "c", "candidate_id": "c1", "type": "transcript", "created_at": old, "legal_hold": True},
    ]
    assert [r["id"] for r in find_expired(records, NOW)] == ["a"]


def test_withdrawal_lists_candidate_records_but_never_the_audit_log():
    records = [
        {"id": "t", "candidate_id": "c1", "type": "transcript", "created_at": "2026-10-02T00:00:00"},
        {"id": "o", "candidate_id": "c2", "type": "transcript", "created_at": "2026-10-02T00:00:00"},
        {"id": "l", "candidate_id": "c1", "type": "audit_log", "created_at": "2026-10-02T00:00:00"},
        {"id": "h", "candidate_id": "c1", "type": "report", "created_at": "2026-10-02T00:00:00", "legal_hold": True},
    ]
    assert [r["id"] for r in find_withdrawal_deletions(records, "c1", WITHDRAWN)] == ["t"]