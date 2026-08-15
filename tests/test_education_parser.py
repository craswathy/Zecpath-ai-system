import sys
sys.path.append(".")
from parsers.education_parser import normalize_degree, extract_graduation_year
from parsers.education_relevance import score_degree_match

def test_normalize_degree_masters():
    assert normalize_degree("Master of Science in Statistics") == "Master's"

def test_extract_graduation_year():
    assert extract_graduation_year("Completed in 2023") == 2023

def test_degree_match_exact():
    assert score_degree_match("Master's", "Master's") == 1.0

def test_degree_match_below_requirement():
    assert score_degree_match("Bachelor's", "Master's") == 0.5