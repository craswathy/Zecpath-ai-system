import sys
sys.path.append(".")
import json
from ats_engine.e2e_stages import parse_resume, run_ats, run_screening, run_hr, estimate_confidence
from ats_engine.run_e2e_simulation import (
    run_pipeline, load_questions, check_invariants, find_inconsistencies, compare_with_humans, load_reviews,
    write_review_packet,
)
from ats_engine.governance_controls import AuditLog

with open("data/e2e/e2e_candidates.json", encoding="utf-8") as f:
    DATA = json.load(f)
QUESTIONS = load_questions()
CANDS = {c["id"]: c for c in DATA["candidates"]}


def _run(cid, **kw):
    return run_pipeline(CANDS[cid], DATA, QUESTIONS, **kw)


def test_unreadable_resume_is_detected_and_gives_no_ats_score():
    parsed = parse_resume("")
    assert parsed["status"] == "unreadable"
    assert run_ats(parsed, DATA["job"])["score"] is None


def test_ats_finds_skills_and_scores_them():
    parsed = parse_resume(DATA["banks"]["resume"]["strong"])
    assert {"python", "sql", "statistics", "excel"} <= set(parsed["skills"])
    assert run_ats(parsed, DATA["job"])["score"] >= 85


def test_keyword_stuffed_resume_scores_full_marks():
    stuffed = run_ats(parse_resume(DATA["banks"]["resume"]["stuffed"]), DATA["job"])["score"]
    medium = run_ats(parse_resume(DATA["banks"]["resume"]["medium"]), DATA["job"])["score"]
    assert stuffed == 100.0 and stuffed > medium


def test_screening_rewards_concrete_answers():
    good = run_screening(DATA["banks"]["screening"]["good"])["score"]
    poor = run_screening(DATA["banks"]["screening"]["poor"])["score"]
    assert good > poor


def test_every_flagged_hr_answer_gets_a_follow_up():
    result = run_hr(DATA["banks"]["hr"]["weak"], "technical")
    assert result["flagged_without_follow_up"] == 0 and result["follow_ups"] >= 3


def test_hedged_answers_lower_the_confidence_estimate():
    assert estimate_confidence("um I guess maybe, I am not sure") < estimate_confidence("I built a model that reached 90 percent accuracy")


def test_strong_candidate_is_selected():
    j = _run("e2e_01")
    assert j["decision"]["decision"] == "Selected" and not j["errors"]


def test_integrity_high_candidate_goes_to_review():
    assert _run("e2e_07")["decision"]["decision"] == "Hold / Review"


def test_candidate_who_stopped_early_is_preliminary_and_on_hold():
    j = _run("e2e_09")
    assert j["unified"]["hiring_fit"]["result_status"] == "preliminary"
    assert j["decision"]["decision"] == "Hold / Review"


def test_failed_resume_upload_is_recorded_and_pipeline_continues():
    j = _run("e2e_08")
    assert j["stages"]["resume_upload"]["status"] == "unreadable"
    assert j["scores"]["ats"] is None and j["scores"]["technical_interview"] is not None


def test_all_consistency_checks_pass_on_the_full_set():
    audit = AuditLog()
    journeys = [run_pipeline(c, DATA, QUESTIONS, audit) for c in DATA["candidates"]]
    checks = check_invariants(journeys, DATA, QUESTIONS, audit)
    assert all(c["passed"] for c in checks), [c for c in checks if not c["passed"]]


def test_inconsistency_finder_flags_keyword_inflation_and_failed_upload():
    journeys = [_run(c) for c in ("e2e_05", "e2e_08")]
    titles = {(cid, t) for cid, t, _ in find_inconsistencies(journeys)}
    assert ("e2e_05", "Resume score far above later rounds") in titles
    assert ("e2e_08", "Resume upload failed") in titles


def test_human_comparison_labels_each_kind_of_disagreement():
    journeys = [_run(c) for c in ("e2e_01", "e2e_06", "e2e_08")]
    rows = [{"candidate_id": "e2e_01", "reviewer": "x", "decision": "Selected"},
            {"candidate_id": "e2e_06", "reviewer": "x", "decision": "Selected"},
            {"candidate_id": "e2e_08", "reviewer": "x", "decision": "Hold / Review"}]
    kinds = {c["candidate_id"]: c["kind"] for c in compare_with_humans(journeys, rows)}
    assert kinds["e2e_01"] == "match"
    assert kinds["e2e_06"] == "AI deferred to a person"
    assert kinds["e2e_08"] == "match"          # Day 57: a failed resume upload now goes to Hold / Review


def test_review_file_loads_and_covers_every_candidate():
    rows, source = load_reviews()
    assert {r["candidate_id"] for r in rows} == set(CANDS)


def test_review_packet_hides_ai_results(tmp_path, monkeypatch):
    import ats_engine.run_e2e_simulation as sim
    monkeypatch.setattr(sim, "OUT_DIR", str(tmp_path))
    write_review_packet(DATA)
    text = (tmp_path / "REVIEW_PACKET.txt").read_text(encoding="utf-8")
    assert "CANDIDATE e2e_01" in text and "CANDIDATE e2e_12" in text
    assert "Hiring fit" not in text and "AI decision" not in text and "confidence" not in text.lower()