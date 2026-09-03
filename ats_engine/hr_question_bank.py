# NOTE: Question text is currently English-only. For multilingual support
# (PRD Phase 4: "Language selection English, Hindi, Malayalam, Tamil"),
# each question would need a translations dict keyed by language code,
# e.g. question["translations"]["ml"] = "..." -- not implemented yet,
# tracked as a future enhancement.

# HR Screening Question Bank -- Zecpath
# Each question is tagged with category, expected answer type,
# mandatory/optional status, and scoring importance (used later by
# the AI screening conversation engine, PRD Phase 5).

QUESTION_BANK = [
    {
        "id": "q_intro_01",
        "category": "Introduction",
        "text": "Can you briefly introduce yourself and your professional background?",
        "expected_answer_type": "free_text",
        "mandatory": True,
        "scoring_importance": "low",
        "applicable_roles": "all",
    },
    {
        "id": "q_edu_01",
        "category": "Education",
        "text": "What is your highest educational qualification and field of study?",
        "expected_answer_type": "free_text",
        "mandatory": True,
        "scoring_importance": "medium",
        "applicable_roles": "all",
    },
    {
        "id": "q_edu_02",
        "category": "Education",
        "text": "Do you have any relevant certifications for this role?",
        "expected_answer_type": "free_text",
        "mandatory": False,
        "scoring_importance": "low",
        "applicable_roles": "all",
    },
    {
        "id": "q_exp_01",
        "category": "Experience",
        "text": "How many years of relevant work experience do you have?",
        "expected_answer_type": "numeric",
        "mandatory": True,
        "scoring_importance": "high",
        "applicable_roles": "all",
    },
    {
        "id": "q_exp_02",
        "category": "Experience",
        "text": "Can you describe your current or most recent role and key responsibilities?",
        "expected_answer_type": "free_text",
        "mandatory": True,
        "scoring_importance": "high",
        "applicable_roles": "all",
    },
    {
        "id": "q_skill_01",
        "category": "Skills",
        "text": "Which of the following tools/technologies have you worked with: {role_specific_skill_list}?",
        "expected_answer_type": "multiple_choice",
        "mandatory": True,
        "scoring_importance": "high",
        "applicable_roles": "technical",
    },
    {
        "id": "q_skill_02",
        "category": "Skills",
        "text": "On a scale of 1-5, how would you rate your proficiency in {primary_skill}?",
        "expected_answer_type": "numeric_scale",
        "mandatory": False,
        "scoring_importance": "medium",
        "applicable_roles": "technical",
    },
    {
        "id": "q_loc_01",
        "category": "Location",
        "text": "Are you currently based in {job_location}, or open to relocating?",
        "expected_answer_type": "yes_no",
        "mandatory": True,
        "scoring_importance": "medium",
        "applicable_roles": "all",
    },
    {
        "id": "q_loc_02",
        "category": "Location",
        "text": "Are you open to remote or hybrid work arrangements?",
        "expected_answer_type": "multiple_choice",
        "mandatory": False,
        "scoring_importance": "low",
        "applicable_roles": "all",
    },
    {
        "id": "q_sal_01",
        "category": "Salary",
        "text": "What is your current CTC and expected CTC for this role?",
        "expected_answer_type": "numeric",
        "mandatory": True,
        "scoring_importance": "medium",
        "applicable_roles": "all",
    },
    {
        "id": "q_notice_01",
        "category": "Notice Period",
        "text": "What is your current notice period, or when would you be available to join?",
        "expected_answer_type": "free_text",
        "mandatory": True,
        "scoring_importance": "medium",
        "applicable_roles": "all",
    },
]


def get_questions_by_category(category):
    """Return all questions in a given category."""
    return [q for q in QUESTION_BANK if q["category"].lower() == category.lower()]


def get_questions_for_role(role_type):
    """Return questions applicable to a role type ('technical', 'business', or 'all')."""
    return [q for q in QUESTION_BANK if q["applicable_roles"] in ("all", role_type)]


def get_mandatory_questions():
    """Return only mandatory questions -- used to ensure minimum screening coverage."""
    return [q for q in QUESTION_BANK if q["mandatory"]]