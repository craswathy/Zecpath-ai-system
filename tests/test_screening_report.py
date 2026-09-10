import sys
sys.path.append(".")
from ats_engine.screening_report_builder import extract_highlight_fields, identify_missing_data
from ats_engine.report_formatter import format_report_as_text

def test_extract_highlight_fields():
    answers = [
        {"question_category": "Salary", "structured_answer": {"extracted_value": 6.0}},
        {"question_category": "Location", "structured_answer": {"extracted_value": "immediate"}},
    ]
    highlights = extract_highlight_fields(answers)
    assert highlights["salary_expectation"] == "6.0 LPA"
    assert highlights["availability"] == "immediate"

def test_identify_missing_data():
    answers = [
        {"question_category": "Skills", "structured_answer": {"is_vague_or_missing": False}},
    ]
    missing = identify_missing_data(answers, ["Skills", "Education", "Experience"])
    assert "Education" in missing
    assert "Skills" not in missing

def test_format_report_as_text_includes_score():
    report = {
        "candidate_id": "test_cand", "job_id": "test_job", "final_screening_score": 75.0,
        "overall_communication_strength": "Strong",
        "highlights": {"salary_expectation": None, "availability": None, "skills_confirmed": []},
        "key_answers": {}, "strengths": [], "risks": [], "missing_data": [],
    }
    text = format_report_as_text(report)
    assert "75.0" in text
    assert "test_cand" in text