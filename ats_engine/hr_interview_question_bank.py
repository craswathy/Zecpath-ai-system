# HR Interview Question Bank -- Zecpath
# Distinct from Day 22's screening question bank: this covers the deeper
# HR interview round (PRD Phase 14-21), with fresher/experienced and
# technical/non-technical branching.

HR_INTERVIEW_QUESTIONS = [
    {
        "id": "hr_intro_01",
        "category": "Self-Introduction",
        "text": "Walk me through your background and what led you to apply for this role.",
        "seniority": "all",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_journey_01",
        "category": "Career Journey",
        "text": "Can you describe your career journey so far and the key transitions in it?",
        "seniority": "experienced",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_journey_02",
        "category": "Career Journey",
        "text": "What projects or coursework during your studies do you feel best prepared you for this role?",
        "seniority": "fresher",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_strengths_01",
        "category": "Strengths & Weaknesses",
        "text": "What would you say is your greatest strength, and how has it helped you professionally?",
        "seniority": "all",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_strengths_02",
        "category": "Strengths & Weaknesses",
        "text": "Tell me about an area you're actively working to improve.",
        "seniority": "all",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_team_01",
        "category": "Teamwork & Culture Fit",
        "text": "Describe a time you disagreed with a teammate. How did you resolve it?",
        "seniority": "experienced",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_team_02",
        "category": "Teamwork & Culture Fit",
        "text": "How do you prefer to collaborate with others when working on a group project or assignment?",
        "seniority": "fresher",
        "role_type": "all",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_team_03",
        "category": "Teamwork & Culture Fit",
        "text": "How do you handle working with team members from different technical backgrounds, like designers or product managers?",
        "seniority": "all",
        "role_type": "technical",
        "follow_up_eligible": True,
    },
    {
        "id": "hr_goals_01",
        "category": "Career Goals",
        "text": "Where do you see yourself professionally in the next 2-3 years?",
        "seniority": "all",
        "role_type": "all",
        "follow_up_eligible": False,
    },
    {
        "id": "hr_avail_01",
        "category": "Availability & Commitment",
        "text": "This role may require flexibility in working hours occasionally -- how do you feel about that?",
        "seniority": "all",
        "role_type": "all",
        "follow_up_eligible": False,
    },
    {
        "id": "hr_avail_02",
        "category": "Availability & Commitment",
        "text": "What is your notice period, and are you currently interviewing elsewhere?",
        "seniority": "experienced",
        "role_type": "all",
        "follow_up_eligible": False,
    },
]


def get_questions_for_candidate(seniority="fresher", role_type="all"):
    """
    Filter the question bank for a specific candidate profile.
    seniority: 'fresher' or 'experienced'
    role_type: 'technical', 'non_technical', or 'all'
    """
    matched = []
    for q in HR_INTERVIEW_QUESTIONS:
        seniority_match = q["seniority"] in ("all", seniority)
        role_match = q["role_type"] in ("all", role_type)
        if seniority_match and role_match:
            matched.append(q)
    return matched


def get_questions_by_category(category):
    return [q for q in HR_INTERVIEW_QUESTIONS if q["category"] == category]