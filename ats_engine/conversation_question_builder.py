from ats_engine.hr_question_bank import get_questions_for_role, get_mandatory_questions
from utils.logger import logger


def build_conversation_questions(job_data, role_type="all"):
    """
    Build a job-specific, ordered list of AI-ready question objects,
    with template placeholders filled in from the JD (Day 6 output).

    job_data: dict with keys like 'required_skills', 'location' (from jd_parsed/)
    """
    questions = get_questions_for_role(role_type)

    skill_names = [s["name"] for s in job_data.get("required_skills", [])]
    skill_list_str = ", ".join(skill_names) if skill_names else "relevant tools"
    primary_skill = skill_names[0] if skill_names else "your primary skill"
    job_location = job_data.get("location", "the job location")

    conversation_ready = []
    for q in questions:
        filled_text = q["text"].format(
            role_specific_skill_list=skill_list_str,
            primary_skill=primary_skill,
            job_location=job_location,
        ) if "{" in q["text"] else q["text"]

        conversation_ready.append({
            "question_id": q["id"],
            "category": q["category"],
            "prompt_text": filled_text,
            "expected_answer_type": q["expected_answer_type"],
            "mandatory": q["mandatory"],
            "scoring_importance": q["scoring_importance"],
        })

    logger.info(f"Built {len(conversation_ready)} conversation-ready questions for role_type={role_type}")
    return conversation_ready


def validate_mandatory_coverage(answered_question_ids):
    """Check whether all mandatory questions were covered in a completed call."""
    mandatory_ids = {q["id"] for q in get_mandatory_questions()}
    answered_ids = set(answered_question_ids)
    missing = mandatory_ids - answered_ids
    return len(missing) == 0, list(missing)