import json
import os
import time
import uuid
from datetime import datetime

LOG_DIR = "data/observability"
os.makedirs(LOG_DIR, exist_ok=True)

# Fields that must never appear in logs (privacy rule from Day 15/43)
FORBIDDEN_FIELDS = {"name", "email", "phone", "resume_text", "transcript", "answer_text"}


def _write(filename, record):
    clean = {k: v for k, v in record.items() if k not in FORBIDDEN_FIELDS}
    with open(os.path.join(LOG_DIR, filename), "a", encoding="utf-8") as f:
        f.write(json.dumps(clean) + "\n")


def new_request_id():
    return "req_" + uuid.uuid4().hex[:10]


def log_api_call(request_id, endpoint, status_code, duration_ms, candidate_id=None, job_id=None):
    _write("api_log.jsonl", {
        "timestamp": datetime.now().isoformat(), "request_id": request_id,
        "endpoint": endpoint, "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "candidate_id": candidate_id, "job_id": job_id,
    })


def log_model_output(request_id, model_name, model_version, score, duration_ms, candidate_id=None):
    _write("model_output_log.jsonl", {
        "timestamp": datetime.now().isoformat(), "request_id": request_id,
        "model_name": model_name, "model_version": model_version,
        "score": score, "duration_ms": round(duration_ms, 2),
        "candidate_id": candidate_id,
    })


def log_error(request_id, endpoint, error_code, message, retryable, candidate_id=None):
    _write("error_log.jsonl", {
        "timestamp": datetime.now().isoformat(), "request_id": request_id,
        "endpoint": endpoint, "error_code": error_code,
        "message": message, "retryable": retryable, "candidate_id": candidate_id,
    })


def log_decision(request_id, candidate_id, job_id, decision, fit_percentage, model_version, flags):
    _write("decision_audit_log.jsonl", {
        "timestamp": datetime.now().isoformat(), "request_id": request_id,
        "candidate_id": candidate_id, "job_id": job_id,
        "decision": decision, "hiring_fit_percentage": fit_percentage,
        "model_version": model_version, "flags": flags,
    })


def timed_call(fn, *args, **kwargs):
    """Run fn and return (result, duration_ms)."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, (time.perf_counter() - start) * 1000