import sys
sys.path.append(".")
from ats_engine.hr_question_bank import get_questions_by_category, get_mandatory_questions
from ats_engine.conversation_question_builder import build_conversation_questions

def test_get_questions_by_category():
    intro_questions = get_questions_by_category("Introduction")
    assert len(intro_questions) > 0
    assert all(q["category"] == "Introduction" for q in intro_questions)

def test_mandatory_questions_exist():
    mandatory = get_mandatory_questions()
    assert len(mandatory) > 0

def test_build_conversation_questions_fills_placeholders():
    job_data = {"required_skills": [{"name": "python"}], "location": "Kochi"}
    questions = build_conversation_questions(job_data, role_type="technical")
    skill_question = next(q for q in questions if q["question_id"] == "q_skill_01")
    assert "python" in skill_question["prompt_text"].lower()