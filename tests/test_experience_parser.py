import sys
sys.path.append(".")

from parsers.experience_parser import extract_experience_entries, compute_experience_summary
from parsers.experience_relevance import score_role_relevance

def test_extract_single_entry():
    text = "WATSICA-WITTING 06/2020 - present Phoenix, AZ // Senior HR Consultant"
    entries = extract_experience_entries(text)
    assert len(entries) == 1
    assert "Senior HR Consultant" in entries[0]["designation"]

def test_relevance_scoring_exact_match():
    score = score_role_relevance("Data Analyst", "Data Analyst")
    assert score == 1.0

def test_relevance_scoring_no_match():
    score = score_role_relevance("Civil Engineer", "Data Analyst")
    assert score < 0.5