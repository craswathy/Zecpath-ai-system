import sys
sys.path.append(".")
from ats_engine.hr_interview_summary_builder import (
    identify_hr_strengths, identify_risk_flags, summarize_overall_hr_performance,
)
from ats_engine.hr_interview_report_generator import generate_natural_language_narrative

def test_summarize_overall_performance_strong():
    result = summarize_overall_hr_performance({"hr_interview_score": 80})
    assert "Strong" in result

def test_summarize_overall_performance_weak():
    result = summarize_overall_hr_performance({"hr_interview_score": 30})
    assert "Below-expectation" in result

def test_identify_risk_flags_with_contradictions():
    risks = identify_risk_flags({"score_reliability": "reliable", "turns_scored": 6}, [], 2)
    assert any("contradiction" in r.lower() for r in risks)

def test_identify_risk_flags_none():
    risks = identify_risk_flags({"score_reliability": "reliable", "turns_scored": 6}, [], 0)
    assert "No significant risk flags" in risks[0]

def test_generate_narrative_includes_score_summary():
    summary = {
        "overall_performance_summary": "Strong overall HR interview performance.",
        "strengths": ["Strong relevance"],
        "weaknesses": ["No significant weaknesses identified"],
        "cultural_fit_indicators": ["Calm, composed demeanor under interview conditions"],
        "risk_flags": ["No significant risk flags identified"],
    }
    narrative = generate_natural_language_narrative(summary)
    assert "Strong overall HR interview performance" in narrative