import os
from datetime import datetime, timedelta, timezone
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.governance_controls import (
    AuditLog, log_score, log_decision, log_human_decision, check_access,
    find_expired, find_withdrawal_deletions,
)

AUDIT_PATH = "data/audit/demo_audit_log.jsonl"
NOW = datetime.now(timezone.utc)

USERS = {
    "rec_asha": {"user_id": "rec_asha", "role": "recruiter", "assigned_jobs": ["jd_data_analyst"]},
    "rec_ravi": {"user_id": "rec_ravi", "role": "recruiter", "assigned_jobs": ["jd_java_developer"]},
    "mgr_neha": {"user_id": "mgr_neha", "role": "hiring_manager", "assigned_jobs": ["jd_data_analyst"]},
    "adm_sam": {"user_id": "adm_sam", "role": "admin"},
    "aud_lee": {"user_id": "aud_lee", "role": "auditor"},
}
CANDIDATE = {"candidate_id": "demo_confident", "job_id": "jd_data_analyst"}
CONSENT_GIVEN = {"candidate_id": "demo_confident", "purposes": {
    "interview_scoring": {"granted_at": "2026-10-01T09:00:00", "withdrawn_at": None},
    "video_behavior_analysis": {"granted_at": None, "withdrawn_at": None}}}
CONSENT_WITHDRAWN = {"candidate_id": "demo_confident", "purposes": {
    "interview_scoring": {"granted_at": "2026-10-01T09:00:00", "withdrawn_at": "2026-10-20T09:00:00"}}}


def run():
    if os.path.exists(AUDIT_PATH):
        os.remove(AUDIT_PATH)          # demo only: start a fresh log
    audit = AuditLog(AUDIT_PATH)

    print("1. SCORE AND DECISION LOGS")
    unified = build_unified_score_object(
        "demo_confident", "jd_data_analyst",
        {"ats": 82, "screening": 78, "hr_interview": 94.5, "technical_interview": 81.7, "machine_test": 85},
        "technical", None, {"integrity_review_priority": "No concern"})
    decision = decide(unified)
    log_score(audit, unified)
    log_decision(audit, decision)
    print(f"   Logged score ({unified['hiring_fit']['percentage']}%) and decision ({decision['decision']})")

    print("\n2. ACCESS CHECKS (every attempt is logged)")
    tests = [
        ("rec_asha", "view_transcript", CONSENT_GIVEN), ("rec_ravi", "view_report", CONSENT_GIVEN),
        ("mgr_neha", "view_transcript", CONSENT_GIVEN), ("adm_sam", "view_report", CONSENT_GIVEN),
        ("aud_lee", "view_audit_log", CONSENT_GIVEN), ("rec_asha", "view_report", CONSENT_WITHDRAWN),
    ]
    for uid, action, consent in tests:
        allowed, reason = check_access(USERS[uid], action, CANDIDATE, consent, audit)
        print(f"   {uid:<10}{action:<17}{'ALLOWED' if allowed else 'DENIED ':<8}{reason}")

    log_human_decision(audit, USERS["rec_asha"], "demo_confident", "Selected", "Confirmed after reading the report")

    print("\n3. RETENTION SWEEP")
    records = [
        {"id": "t1", "candidate_id": "demo_confident", "type": "transcript", "created_at": (NOW - timedelta(days=200)).isoformat()},
        {"id": "t2", "candidate_id": "demo_confident", "type": "transcript", "created_at": (NOW - timedelta(days=30)).isoformat()},
        {"id": "r1", "candidate_id": "demo_confident", "type": "report", "created_at": (NOW - timedelta(days=400)).isoformat()},
        {"id": "r2", "candidate_id": "demo_confident", "type": "report", "created_at": (NOW - timedelta(days=400)).isoformat(), "legal_hold": True},
        {"id": "b1", "candidate_id": "demo_confident", "type": "behavior_features", "created_at": (NOW - timedelta(days=10)).isoformat()},
    ]
    print("   Past retention:", [r["id"] for r in find_expired(records, NOW)], "(r2 skipped: legal hold)")
    print("   Consent withdrawn, list for deletion review:",
          [r["id"] for r in find_withdrawal_deletions(records, "demo_confident", CONSENT_WITHDRAWN)])

    print("\n4. AUDIT LOG CHECK")
    ok, bad = audit.verify()
    print(f"   {len(audit.entries)} entries. Chain intact: {ok}")
    audit.entries[1]["detail"]["decision"] = "Rejected"      # simulate tampering with the decision entry, in memory only
    ok, bad = audit.verify()
    print(f"   After editing the decision entry (2) in memory: chain intact: {ok}, first bad entry: {bad}")
    print(f"\nSaved demo log to {AUDIT_PATH}")


if __name__ == "__main__":
    run()