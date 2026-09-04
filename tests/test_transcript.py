import sys
sys.path.append(".")
from ats_engine.transcript_normalizer import normalize_transcript_text, extract_numeric_answer, extract_yes_no_answer
from ats_engine.transcript_schema import build_empty_transcript

def test_normalize_removes_fillers():
    result = normalize_transcript_text("uh yeah so um I have three years")
    assert "uh" not in result.lower()
    assert "um" not in result.lower()

def test_normalize_converts_number_words():
    result = normalize_transcript_text("I have three years of experience")
    assert "3" in result

def test_extract_numeric_answer():
    assert extract_numeric_answer("I have 3 years of experience") == 3.0

def test_extract_yes_no_answer():
    assert extract_yes_no_answer("yes definitely") == "yes"
    assert extract_yes_no_answer("no not really") == "no"

def test_build_empty_transcript_structure():
    t = build_empty_transcript("call_1", "cand_1", "job_1")
    assert t["call_id"] == "call_1"
    assert t["turns"] == []