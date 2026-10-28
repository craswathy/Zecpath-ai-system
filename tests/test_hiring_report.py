import sys
sys.path.append(".")
import json
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.hiring_report_generator import build_report
from ats_engine.report_exporter import render_text, render_html, export_report

STRONG = {"ats": 85, "screening": 82, "hr_interview": 88, "technical_interview": 86, "machine_test": 84}
DETAILS = {
    "ats": {"summary": "Good match.", "matched_skills": ["Python", "SQL", "Statistics"], "missing_skills": ["Power BI"]},
    "hr_interview": {"band": "Strong", "component_scores": {"relevance": 1.0, "communication": 0.45}, "weak_components": ["communication"]},
    "technical_interview": {"band": "Strong", "shallow_answers": 3,
                            "skills": {"react": {"score": 0.9, "label": "Strong", "highest_level_passed": "L3"},
                                       "node": {"score": 0.3, "label": "Weak", "highest_level_passed": None}}},
}


def _report(scores=None, context=None, details=None, low=None):
    unified = build_unified_score_object("c1", "j1", scores or STRONG, "technical", low, context)
    decision = decide(unified)
    return build_report(unified, decision, details if details is not None else DETAILS)


def test_report_has_all_main_parts():
    r = _report()
    for key in ("headline", "round_scores", "strengths", "weaknesses", "risk_indicators",
                "sections", "final_recommendation", "human_review", "limitations", "metadata"):
        assert key in r
    for stage in ("ats", "screening", "hr_interview", "technical_interview", "machine_test", "behavioral_flags"):
        assert stage in r["sections"]


def test_headline_matches_decision_and_fit():
    r = _report()
    assert r["headline"]["decision"] == r["final_recommendation"]["decision"]
    assert r["headline"]["hiring_fit_percentage"] > 0


def test_strengths_and_weaknesses_come_from_the_data():
    r = _report()
    assert any("Technical skills at" in s and "react" in s for s in r["strengths"])
    assert any("Technical skills below" in s and "node" in s for s in r["weaknesses"])
    assert any("HR interview components below" in s and "communication" in s for s in r["weaknesses"])
    assert any("Power BI" in s for s in r["weaknesses"])
    assert any("3 technical answers" in s for s in r["weaknesses"])


def test_integrity_high_is_a_risk_indicator():
    r = _report(context={"integrity_review_priority": "High"})
    assert any(x["level"] == "high" and "Integrity" in x["text"] for x in r["risk_indicators"])


def test_behavioral_label_is_not_a_risk_indicator():
    r = _report(context={"behavioral_label": "Low observed engagement"})
    assert not any("engagement" in x["text"].lower() for x in r["risk_indicators"])
    assert "context only" in " ".join(r["sections"]["behavioral_flags"]["lines"])


def test_weak_round_and_missing_round_are_risks():
    scores = dict(STRONG)
    scores["ats"] = 35
    scores["machine_test"] = None
    r = _report(scores)
    texts = " ".join(x["text"] for x in r["risk_indicators"])
    assert "below 40" in texts and "Not scored" in texts


def test_preliminary_result_is_a_risk():
    r = _report({"ats": 90, "screening": 90})
    assert any("preliminary" in x["text"] for x in r["risk_indicators"])


def test_unscored_stage_says_not_scored():
    scores = dict(STRONG)
    scores["machine_test"] = None
    r = _report(scores)
    assert r["sections"]["machine_test"]["lines"] == ["Not scored yet."]
    assert r["sections"]["machine_test"]["available"] is False


def test_report_works_without_any_details():
    r = _report(details={})
    assert r["sections"]["ats"]["lines"]
    assert r["strengths"] and r["weaknesses"]


def test_human_review_is_required_and_empty():
    r = _report()
    assert r["human_review"]["required"] is True
    assert r["human_review"]["final_decision"] is None


def test_text_report_has_all_headings():
    text = render_text(_report())
    for heading in ("AT A GLANCE", "ROUND SCORES", "STRENGTHS", "WEAKNESSES", "RISK INDICATORS",
                    "DETAILS BY STAGE", "FINAL RECOMMENDATION", "HUMAN REVIEW", "LIMITS"):
        assert heading in text


def test_html_report_is_escaped_and_complete():
    r = _report(details={"ats": {"summary": "<script>alert(1)</script>"}})
    page = render_html(r)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
    assert page.startswith("<!DOCTYPE html>") and page.strip().endswith("</html>")
    assert "Human review" in page


def test_export_writes_three_files(tmp_path):
    paths = export_report(_report(), str(tmp_path))
    for kind in ("html", "txt", "json"):
        assert paths[kind].endswith("." + kind)
    saved = json.load(open(paths["json"], encoding="utf-8"))
    assert saved["candidate"]["candidate_id"] == "c1"


def test_lists_are_capped():
    r = _report()
    assert len(r["strengths"]) <= 6 and len(r["weaknesses"]) <= 6