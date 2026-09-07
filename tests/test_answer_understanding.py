import sys
sys.path.append(".")
from ats_engine.intent_classifier import classify_intent, is_off_topic
from ats_engine.answer_extractor import extract_experience_years, extract_salary_expectation, is_vague_or_missing, build_structured_answer

def test_classify_intent_skills():
    intents = classify_intent("I have worked with Python and SQL extensively")
    assert "skills_mention" in intents

def test_off_topic_detection():
    assert is_off_topic("I love hiking on weekends", "Skills") is True
    assert is_off_topic("I have worked with Python", "Skills") is False

def test_extract_experience_years():
    assert extract_experience_years("I have 3 years of experience") == 3.0

def test_extract_salary():
    assert extract_salary_expectation("My expected salary is 6 lakh") == 6.0

def test_vague_answer_detected():
    assert is_vague_or_missing("maybe") is True
    assert is_vague_or_missing("I have three years of solid experience in data analysis") is False

def test_build_structured_answer():
    result = build_structured_answer("Experience", "I have 3 years of experience")
    assert result["extracted_value"] == 3.0
    assert result["is_vague_or_missing"] is False