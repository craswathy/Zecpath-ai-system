import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from utils.logger import logger

# Day 55: starting values for review by the project owner, a data protection lead and a lawyer.

ROLE_PERMISSIONS = {
    "recruiter": {"view_report", "view_scores", "view_transcript", "export_report", "record_decision"},
    "hiring_manager": {"view_report", "view_scores", "record_decision"},
    "dpo": {"view_audit_log", "delete_data"},
    "auditor": {"view_audit_log"},
    "admin": {"manage_users"},
    "system": {"write_score", "write_decision", "write_audit"},
}
JOB_SCOPED_ROLES = {"recruiter", "hiring_manager"}   # these roles only see candidates on their own jobs

# Actions that touch candidate data need consent for this purpose
ACTION_PURPOSE = {
    "view_report": "interview_scoring", "view_scores": "interview_scoring",
    "view_transcript": "interview_scoring", "export_report": "interview_scoring",
    "record_decision": "interview_scoring", "write_score": "interview_scoring",
    "write_decision": "interview_scoring",
}

# Days to keep each kind of data, then delete (unless a legal hold applies)
RETENTION_DAYS = {
    "transcript": 180, "report": 365, "score_record": 365, "decision_record": 365,
    "behavior_features": 90, "code_snapshot": 180, "consent_record": 1095, "audit_log": 365,
}
# Which consent purpose each kind of data depends on
DATA_PURPOSE = {
    "transcript": "interview_scoring", "report": "interview_scoring", "score_record": "interview_scoring",
    "decision_record": "interview_scoring", "behavior_features": "video_behavior_analysis",
    "code_snapshot": "interview_scoring",
}


class AuditLog:
    """Append-only log. Each entry holds the hash of the one before it, so edits are detectable."""

    def __init__(self, path=None):
        self.path = path
        self.entries = []
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.entries = [json.loads(line) for line in f if line.strip()]

    @staticmethod
    def _hash(entry):
        body = {k: v for k, v in entry.items() if k != "hash"}
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()

    def log(self, event, actor, candidate_id=None, detail=None, now=None):
        prev = self.entries[-1]["hash"] if self.entries else "0" * 64
        entry = {
            "seq": len(self.entries) + 1,
            "time": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            "event": event, "actor": actor, "candidate_id": candidate_id,
            "detail": detail or {}, "prev_hash": prev,
        }
        entry["hash"] = self._hash(entry)
        self.entries.append(entry)
        if self.path:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        return entry

    def verify(self):
        """Return (True, None) if the chain is intact, else (False, seq of the first bad entry)."""
        prev = "0" * 64
        for e in self.entries:
            if e["prev_hash"] != prev or e["hash"] != self._hash(e):
                return False, e["seq"]
            prev = e["hash"]
        return True, None


def log_score(audit, unified, actor="system"):
    """Score log: what was scored, with which model version and weights. No transcript text."""
    detail = {
        "model_version": unified["metadata"]["model_version"], "job_id": unified["job_id"],
        "role_category": unified["role_category"],
        "hiring_fit": unified["hiring_fit"]["percentage"], "category": unified["hiring_fit"]["category"],
        "result_status": unified["hiring_fit"]["result_status"],
        "round_scores": {n: r["score"] for n, r in unified["rounds"].items()},
        "weights_used": unified["weights_used"],
        "low_reliability_rounds": [n for n, r in unified["rounds"].items() if r["low_reliability"]],
    }
    return audit.log("score", actor, unified["candidate_id"], detail)


def log_decision(audit, decision, actor="system"):
    """Decision log: the recommendation, the rules that shaped it, and that a human must review."""
    detail = {
        "model_version": decision["metadata"]["model_version"], "decision": decision["decision"],
        "score_based_decision": decision["score_based_decision"],
        "confidence": decision["confidence"]["score"],
        "rules": [r["id"] for r in decision["rules_triggered"]],
        "human_review_required": decision["human_review"]["required"],
        "final_decision": decision["human_review"]["final_decision"],
    }
    return audit.log("decision", actor, decision["candidate_id"], detail)


def log_human_decision(audit, user, candidate_id, final_decision, reason):
    """The human reviewer's final decision, linked to the same candidate."""
    return audit.log("human_decision", user["user_id"], candidate_id,
                     {"role": user["role"], "final_decision": final_decision, "reason": reason})


def is_allowed(user, action, candidate=None):
    """Role check, then job-scope check. Returns (allowed, reason)."""
    role = user.get("role")
    if action not in ROLE_PERMISSIONS.get(role, set()):
        return False, f"role '{role}' may not {action}"
    if role in JOB_SCOPED_ROLES:
        if not candidate or candidate.get("job_id") not in user.get("assigned_jobs", []):
            return False, "candidate is not on one of the user's assigned jobs"
    return True, "role and job scope allow it"


def has_consent(consent, purpose):
    """True when the purpose was granted and not withdrawn. No purpose needed means no check."""
    if purpose is None:
        return True
    entry = (consent or {}).get("purposes", {}).get(purpose)
    return bool(entry and entry.get("granted_at") and not entry.get("withdrawn_at"))


def check_access(user, action, candidate, consent, audit):
    """Role, scope and consent checks. Every attempt, allowed or denied, goes to the audit log."""
    allowed, reason = is_allowed(user, action, candidate)
    if allowed and not has_consent(consent, ACTION_PURPOSE.get(action)):
        allowed, reason = False, f"no valid consent for {ACTION_PURPOSE.get(action)}"
    audit.log("access", user["user_id"], (candidate or {}).get("candidate_id"),
              {"action": action, "role": user["role"], "allowed": allowed, "reason": reason})
    return allowed, reason


def find_expired(records, now=None):
    """Records older than their retention period. Records on legal hold are skipped."""
    now = now or datetime.now(timezone.utc)
    expired = []
    for r in records:
        days = RETENTION_DAYS.get(r["type"])
        if r.get("legal_hold") or days is None:
            continue
        created = datetime.fromisoformat(r["created_at"])
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if now - created > timedelta(days=days):
            expired.append(r)
    return expired


def find_withdrawal_deletions(records, candidate_id, consent):
    """Records of this candidate whose consent purpose was withdrawn. The audit log is never listed."""
    out = []
    for r in records:
        if r["candidate_id"] != candidate_id or r.get("legal_hold") or r["type"] == "audit_log":
            continue
        purpose = DATA_PURPOSE.get(r["type"])
        if purpose and not has_consent(consent, purpose):
            out.append(r)
    return out