import json
from datetime import datetime
from ats_engine.e2e_stages import run_hr, run_screening, run_technical
from ats_engine.cross_round_aggregation_engine import aggregate_rounds
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.technical_scoring_engine import score_answer
from ats_engine.governance_controls import AuditLog, has_consent, check_access, find_expired
from ats_engine.refined_intent import classify_follow_up_refined
from ats_engine.run_e2e_simulation import run_pipeline, load_questions


def show(name, fn):
    try:
        print(f"{name:<44}{fn()}")
    except Exception as exc:
        print(f"{name:<44}CRASH {type(exc).__name__}")


def run():
    q = load_questions()
    with open("data/e2e/e2e_candidates.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    cands = {c["id"]: c for c in data["candidates"]}
    typo = dict(cands["e2e_01"], hr="typo")
    show("B1  HR interview with no answers", lambda: run_hr([], "technical")["score"])
    show("B2  screening with no answers", lambda: run_screening([])["score"])
    show("B3  technical interview with no answers", lambda: run_technical({}, q)["score"])
    show("B4  round scores missing (None)", lambda: aggregate_rounds(None)["rounds_completed"])
    show("B5  transcript cleanup of a number", lambda: repr(normalize_transcript_text(12345)))
    show("B6  unknown question type", lambda: score_answer({"id": "x", "type": "design", "level": "L1", "key_points": ["a"]}, "t", "x"))
    show("B7  audit log with a date value", lambda: bool(AuditLog().log("access", "u", "c", {"when": datetime.now()})))
    show("B8  malformed consent record", lambda: has_consent({"purposes": ["x"]}, "interview_scoring"))
    show("B9  access check with no user", lambda: check_access(None, "view_report", {"candidate_id": "c", "job_id": "j"}, {}, AuditLog()))
    show("B10 one record with a bad date", lambda: [r["id"] for r in find_expired([{"id": "a", "type": "transcript", "created_at": "bad"}, {"id": "b", "type": "transcript", "created_at": "2020-01-01T00:00:00"}])])
    show("B11 wrong data key for a candidate", lambda: run_pipeline(typo, data, q)["decision"]["decision"])
    show("B12 failed resume upload, strong elsewhere", lambda: run_pipeline(cands["e2e_08"], data, q)["decision"]["decision"])
    show("B13 'this kind of work' counted as hedge", lambda: classify_follow_up_refined("I handle this kind of data work every day and I clean the tables before reporting", False))


if __name__ == "__main__":
    run()