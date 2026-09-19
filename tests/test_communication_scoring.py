import sys
sys.path.append(".")
from ats_engine.fluency_analyzer import count_filler_words, measure_sentence_continuity
from ats_engine.grammar_vocabulary_analyzer import measure_vocabulary_range
from ats_engine.communication_scorer import score_communication

def test_count_filler_words():
    assert count_filler_words("um so I uh think that") >= 2

def test_sentence_continuity_complete_sentences():
    score = measure_sentence_continuity("I have three years of experience. I work with Python daily.")
    assert score == 1.0

def test_vocabulary_range_varied():
    result = measure_vocabulary_range("Python SQL machine learning data analysis statistics")
    assert result["vocabulary_score"] > 0.5

def test_score_communication_empty_input():
    result = score_communication("", "")
    assert result["communication_score"] == 0.0

def test_score_communication_returns_valid_range():
    result = score_communication(
        "I have three years of experience in data analysis and machine learning.",
        "I have three years of experience in data analysis and machine learning.",
    )
    assert 0 <= result["communication_score"] <= 100