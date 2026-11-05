import json
import math
import os
import random
import time
from datetime import datetime, timezone
from ats_engine.cross_round_aggregation_engine import aggregate_rounds
from ats_engine.decision_config import SELECTED, HOLD, REJECTED
from ats_engine.e2e_stages import parse_resume, run_ats, run_hr, run_screening, run_technical
from ats_engine.governance_controls import AuditLog, check_access, find_expired, find_withdrawal_deletions, has_consent
from ats_engine.refined_decision_logic import decide_refined, batch_mode
from ats_engine.refined_intent import classify_follow_up_refined
from ats_engine.run_e2e_simulation import load_questions, run_pipeline
from ats_engine.technical_scoring_engine import score_answer
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.unified_candidate_score_object import build_unified_score_object

REQUIRED_FILES = ["data/e2e/e2e_candidates.json", "data/technical_interview/question_hierarchy.json",
                  "data/e2e/human_reviews_simulated.csv"]
UNIFIED_KEYS = ["candidate_id", "job_id", "role_category", "metadata", "rounds", "hiring_fit", "missing_rounds",
                "rank_in_pool", "context_not_scored", "weights_used", "explanation", "note"]
DECISION_KEYS = ["candidate_id", "job_id", "role_category", "metadata", "decision", "recommendation",
                 "score_based_decision", "hiring_fit", "rules_triggered", "confidence", "risk_factors",
                 "next_steps", "human_review", "explanation", "note"]
ROUNDS = ["ats", "screening", "hr_interview", "technical_interview", "machine_test"]
GOOD = {"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84}
STRONG_ANSWER = {"id": "x_con_l1", "type": "conceptual", "level": "L1", "key_points": ["a point"]}


def preflight():
    """Data pipeline check: required files exist and parse."""
    results = []
    for path in REQUIRED_FILES:
        if not os.path.exists(path):
            results.append((path, False, "file not found"))
            continue
        try:
            if path.endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
            results.append((path, True, "ok"))
        except ValueError as exc:
            results.append((path, False, f"not valid JSON: {exc}"))
    return results


def validate_e2e_data(data, questions):
    """Data pipeline check: every reference in the candidate file points at something real."""
    issues, banks = [], data.get("banks", {})
    for c in data.get("candidates", []):
        for field, bank in (("resume", "resume"), ("screening", "screening"), ("hr", "hr"), ("tech", "tech")):
            key = c.get(field)
            if key is not None and key not in banks.get(bank, {}):
                issues.append(f"{c['id']}: {field} '{key}' is not in the {bank} bank")
        for q_id in banks.get("tech", {}).get(c.get("tech"), {}):
            if q_id not in questions:
                issues.append(f"{c['id']}: technical answer for unknown question {q_id}")
        m = c.get("machine")
        if m is not None and not (isinstance(m, (int, float)) and 0 <= m <= 100):
            issues.append(f"{c['id']}: machine score {m} is not 0 to 100")
    return issues


def _decision_of(scores, role="technical", context=None, low=None):
    unified = build_unified_score_object("edge", "j", scores, role, low, context or {})
    return decide_refined(unified), unified


def edge_cases(questions, data):
    """Each case returns True when the system behaves sensibly. A crash counts as a failure."""
    q = questions
    c8 = [c for c in data["candidates"] if c["id"] == "e2e_08"][0]
    typo = dict(data["candidates"][0], hr="no_such_bank")
    big_text = "I built a dashboard in Python and it worked well. " * 3000
    cases = [
        ("Conversation", "cleanup of None text gives empty text", lambda: normalize_transcript_text(None) == ""),
        ("Conversation", "cleanup of a number does not crash", lambda: normalize_transcript_text(12345) == "12345"),
        ("Conversation", "cleanup of emoji and Malayalam text does not crash", lambda: bool(normalize_transcript_text("um എനിക്ക് ഇഷ്ടമാണ് 😀 data"))),
        ("Conversation", "cleanup of a 30,000 word text is fast", lambda: _fast(lambda: normalize_transcript_text(big_text), 3.0)),
        ("Conversation", "None answer gets a clarification", lambda: classify_follow_up_refined(None, False) == "clarification"),
        ("Conversation", "'this kind of work' is not a hedge", lambda: classify_follow_up_refined(
            "I handle this kind of data work every day and I clean the tables before reporting", False) != "clarification"),
        ("Conversation", "'I am kind of good at Excel' is a hedge", lambda: classify_follow_up_refined("I am kind of good at Excel", False) == "clarification"),
        ("Scoring", "no round scores (None) gives no data, not a crash", lambda: aggregate_rounds(None)["rounds_completed"] == 0),
        ("Scoring", "NaN, infinity, negative, over 100, text and True are all ignored", lambda: aggregate_rounds(
            {"ats": float("nan"), "screening": float("inf"), "hr_interview": -5, "technical_interview": 101, "machine_test": "85"}
        )["rounds_completed"] == 0 and aggregate_rounds({"ats": True})["rounds_completed"] == 0),
        ("Scoring", "unknown role uses default weights", lambda: aggregate_rounds(GOOD, "astronaut")["role_used"] == "default"),
        ("Scoring", "empty HR interview gives no score, not 0", lambda: run_hr([], "technical")["score"] is None),
        ("Scoring", "empty screening gives no score, not a crash", lambda: run_screening([])["score"] is None),
        ("Scoring", "empty technical interview gives no score", lambda: run_technical({}, q)["score"] is None),
        ("Scoring", "only unknown technical questions gives no score", lambda: run_technical({"zzz_1": "text"}, q)["score"] is None),
        ("Scoring", "unknown question type is a clear ValueError", lambda: _raises(ValueError, lambda: score_answer(
            {"id": "x", "type": "design", "level": "L1", "key_points": ["a"]}, "text", "x"))),
        ("Scoring", "non-text technical answer does not crash", lambda: score_answer(STRONG_ANSWER, 123, "x")["score"] >= 0),
        ("Scoring", "empty technical answer scores 0 as 'no answer'", lambda: score_answer(STRONG_ANSWER, "", "x")["depth_label"] == "no answer"),
        ("Decision", "all rounds missing gives Hold / Review with zero confidence", lambda: (
            lambda r: r[0]["decision"] == HOLD and r[0]["confidence"]["score"] == 0.0)(_decision_of({}))),
        ("Decision", "failed resume with strong scores gives Hold / Review", lambda: (
            lambda r: r[0]["decision"] == HOLD and any(x["id"] == "RESUME_FAILED" for x in r[0]["rules_triggered"]))(
            _decision_of(dict(GOOD, ats=None), context={"resume_status": "unreadable"}))),
        ("Decision", "failed resume and already Hold still records the rule and the re-upload step", lambda: (
            lambda r: any(x["id"] == "RESUME_FAILED" for x in r[0]["rules_triggered"]) and
            any("upload" in s for s in r[0]["next_steps"]))(
            _decision_of({"ats": None, "screening": 80, "hr_interview": None, "technical_interview": None, "machine_test": None},
                         context={"resume_status": "unreadable"}))),
        ("Decision", "a failed pipeline stage gives Hold / Review", lambda: (
            lambda r: r[0]["decision"] == HOLD and any(x["id"] == "STAGE_ERROR" for x in r[0]["rules_triggered"]))(
            _decision_of(GOOD, context={"pipeline_errors": 1}))),
        ("Decision", "readable resume is not affected", lambda: _decision_of(GOOD, context={"resume_status": "ok"})[0]["decision"] == SELECTED),
        ("Governance", "malformed consent is treated as no consent", lambda: has_consent({"purposes": ["x"]}, "interview_scoring") is False),
        ("Governance", "missing user is denied and logged", lambda: (
            lambda a: check_access(None, "view_report", {"candidate_id": "c", "job_id": "j"}, {}, a) == (False, "no verified user")
            and a.entries[-1]["detail"]["allowed"] is False)(AuditLog())),
        ("Governance", "audit log accepts a date value and stays verifiable", lambda: (
            lambda a: a.log("access", "u", "c", {"when": datetime.now(timezone.utc)}) and a.verify() == (True, None))(AuditLog())),
        ("Governance", "unreadable record date is skipped, others are still checked", lambda: [r["id"] for r in find_expired([
            {"id": "a", "type": "transcript", "created_at": "not a date"},
            {"id": "b", "type": "transcript", "created_at": "2020-01-01T00:00:00"}])] == ["b"]),
        ("Governance", "record with missing fields does not crash the withdrawal list", lambda: find_withdrawal_deletions(
            [{"id": "a"}, {"id": "b", "candidate_id": "c1", "type": "transcript"}], "c1", {}) == [{"id": "b", "candidate_id": "c1", "type": "transcript"}]),
        ("Pipeline", "a wrong data key is recorded as an error and the journey still completes", lambda: (
            lambda j: j["decision"]["decision"] == HOLD and j["scores"]["hr_interview"] is None)(
            run_pipeline(typo, data, q))),
        ("Pipeline", "failed resume upload ends as Hold / Review", lambda: run_pipeline(c8, data, q)["decision"]["decision"] == HOLD),
        ("Pipeline", "candidate with every stage empty is pending", lambda: run_pipeline(
            {"id": "empty", "note": "x", "resume": None, "screening": None, "hr": None, "tech": None, "machine": None},
            data, q)["unified"]["metadata"]["status"] == "pending"),
    ]
    return cases


def _fast(fn, seconds):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start < seconds


def _raises(exc, fn):
    try:
        fn()
    except exc:
        return True
    return False


def fuzz(n=300, seed=7):
    """Random and deliberately bad inputs. The output contract and safety rules must always hold."""
    rng = random.Random(seed)
    weird = [float("nan"), float("inf"), -5, 150, "85", True, None, None]
    roles = ["technical", "client_facing", "entry_level", "senior", "default", "astronaut", None]
    failures, decisions = [], {SELECTED: 0, HOLD: 0, REJECTED: 0}
    with batch_mode():
        for i in range(n):
            scores = {r: (rng.choice(weird) if rng.random() < 0.25 else round(rng.uniform(0, 100), 1)) for r in ROUNDS}
            context = {"integrity_review_priority": rng.choice(["No concern", "Low", "Medium", "High", None]),
                       "resume_status": rng.choice(["ok", "ok", "unreadable", None]),
                       "pipeline_errors": rng.choice([0, 0, 0, 1])}
            low = rng.sample(ROUNDS, rng.randint(0, 2))
            role = rng.choice(roles)
            try:
                unified = build_unified_score_object(f"f{i}", "job", scores, role, low, context)
                d = decide_refined(unified)
                again = decide_refined(build_unified_score_object(f"f{i}", "job", scores, role, low, context))
            except Exception as exc:
                failures.append((i, f"crash {type(exc).__name__}: {exc}"))
                continue
            problems = []
            problems += [f"missing unified key {k}" for k in UNIFIED_KEYS if k not in unified]
            problems += [f"missing decision key {k}" for k in DECISION_KEYS if k not in d]
            if d["decision"] not in decisions:
                problems.append("unknown decision")
            if not (0 <= d["confidence"]["score"] <= 1):
                problems.append("confidence out of range")
            if not (0 <= unified["hiring_fit"]["percentage"] <= 100):
                problems.append("fit out of range")
            ws = sum(unified["weights_used"].values())
            if unified["weights_used"] and abs(ws - 1) > 0.01:
                problems.append(f"weights sum {ws}")
            if any(isinstance(v, float) and math.isnan(v) for v in [unified["hiring_fit"]["percentage"], d["confidence"]["score"]]):
                problems.append("NaN in output")
            if not (d["human_review"]["required"] and d["human_review"]["final_decision"] is None):
                problems.append("human review not required")
            if context["integrity_review_priority"] == "High" and d["decision"] == REJECTED:
                problems.append("integrity High rejected")
            if (context["resume_status"] == "unreadable" or context["pipeline_errors"]) and d["decision"] != HOLD:
                problems.append("failed resume or stage not on hold")
            if again["decision"] != d["decision"] or again["confidence"] != d["confidence"]:
                problems.append("not deterministic")
            if problems:
                failures.append((i, "; ".join(problems)))
            else:
                decisions[d["decision"]] += 1
    return {"checked": n, "failures": failures, "decisions": decisions}


def run():
    print("PART 1: DATA PIPELINE CHECKS")
    pre = preflight()
    for path, ok, detail in pre:
        print(f"  {'PASS' if ok else 'FAIL'}  {path} ({detail})")
    if not all(ok for _, ok, _ in pre):
        print("  Stopping: fix the files above first.")
        return 1
    with open("data/e2e/e2e_candidates.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = load_questions()
    issues = validate_e2e_data(data, questions)
    print(f"  {'PASS' if not issues else 'FAIL'}  candidate file references ({len(data['candidates'])} candidates)")
    for i in issues:
        print(f"        {i}")

    print("\nPART 2: EDGE CASES")
    results = []
    with batch_mode():
        for area, name, fn in edge_cases(questions, data):
            try:
                ok = bool(fn())
                detail = ""
            except Exception as exc:
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            results.append({"area": area, "case": name, "passed": ok, "detail": detail})
            print(f"  {'PASS' if ok else 'FAIL'}  [{area}] {name}" + (f"  ({detail})" if detail else ""))
    passed = sum(r["passed"] for r in results)
    print(f"  {passed} of {len(results)} passed")

    print("\nPART 3: RANDOM AND BAD INPUT (fuzz test)")
    fz = fuzz()
    print(f"  {fz['checked']} random candidates, {len(fz['failures'])} failures")
    print(f"  Decisions seen: {fz['decisions']}")
    for i, why in fz["failures"][:5]:
        print(f"    candidate f{i}: {why}")

    os.makedirs("data/stability", exist_ok=True)
    with open("data/stability/stability_results.json", "w", encoding="utf-8") as f:
        json.dump({"data_issues": issues, "edge_cases": results, "fuzz": {"checked": fz["checked"],
                   "failures": len(fz["failures"]), "decisions": fz["decisions"]}}, f, indent=2)
    print("\nSaved data/stability/stability_results.json")
    return 0 if passed == len(results) and not fz["failures"] and not issues else 1


if __name__ == "__main__":
    raise SystemExit(run())