# Aptitude & Situational Judgment Question Bank -- Zecpath
# Distinct from Day 33's HR interview questions: these test reasoning
# ability and judgment under scenarios, not self-description.

LOGICAL_REASONING_QUESTIONS = [
    {
        "id": "apt_logic_01",
        "category": "Numerical Reasoning",
        "text": "If a project takes 3 people 12 days to complete, how many days would it take 4 people, assuming equal work distribution?",
        "ideal_answer_structure": ["identifies total work as person-days (36)", "divides by new team size (4)", "arrives at 9 days"],
        "expected_answer_type": "numeric",
        "correct_answer": 9,
        "role_type": "all",
    },
    {
        "id": "apt_logic_02",
        "category": "Pattern Recognition",
        "text": "What comes next in this sequence: 2, 6, 12, 20, 30, ...?",
        "ideal_answer_structure": ["identifies the pattern as n(n+1)", "calculates next term as 42"],
        "expected_answer_type": "numeric",
        "correct_answer": 42,
        "role_type": "all",
    },
    {
        "id": "apt_verbal_01",
        "category": "Verbal Reasoning",
        "text": "If all analysts are detail-oriented, and some detail-oriented people are slow decision-makers, can we conclude all analysts are slow decision-makers?",
        "ideal_answer_structure": ["recognizes this is a logical fallacy", "explains why the conclusion doesn't follow", "answers 'no' with reasoning"],
        "expected_answer_type": "reasoning",
        "correct_answer": "no",
        "role_type": "all",
    },
]

SITUATIONAL_JUDGMENT_SCENARIOS = [
    {
        "id": "apt_sjt_01",
        "category": "Situational Judgment",
        "text": "You discover a mistake in a report that was already sent to a client yesterday. What would you do?",
        "ideal_answer_structure": ["acknowledges the mistake promptly", "proposes informing relevant stakeholders", "focuses on correction, not blame"],
        "expected_answer_type": "free_text",
        "role_type": "all",
    },
    {
        "id": "apt_sjt_02",
        "category": "Situational Judgment",
        "text": "A teammate is consistently missing deadlines, affecting your own work. How would you handle this?",
        "ideal_answer_structure": ["mentions direct communication first", "avoids immediately escalating to management", "focuses on understanding root cause"],
        "expected_answer_type": "free_text",
        "role_type": "all",
    },
    {
        "id": "apt_sjt_03",
        "category": "Situational Judgment",
        "text": "You're asked to deliver a technical solution faster than you believe is safely possible. How do you respond?",
        "ideal_answer_structure": ["communicates the risk clearly", "proposes alternatives (reduced scope, phased delivery)", "doesn't simply agree or simply refuse"],
        "expected_answer_type": "free_text",
        "role_type": "technical",
    },
]


def get_aptitude_questions(role_type="all", category=None):
    all_questions = LOGICAL_REASONING_QUESTIONS + SITUATIONAL_JUDGMENT_SCENARIOS
    matched = [q for q in all_questions if q["role_type"] in ("all", role_type)]
    if category:
        matched = [q for q in matched if q["category"] == category]
    return matched