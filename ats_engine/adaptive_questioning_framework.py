from utils.logger import logger

FOLLOW_UP_TEMPLATES = {
    "clarification": [
        "Could you clarify what you mean by that?",
        "I want to make sure I understood correctly -- could you rephrase that?",
    ],
    "deepening": [
        "Could you give me a specific example of that?",
        "Can you walk me through a particular situation where that applied?",
        "What made that experience stand out for you?",
    ],
    "scenario_based": [
        "Given that experience, how would you handle a situation where a teammate strongly disagreed with your approach?",
        "If you had to do that project again with half the time, what would you change?",
        "How would you apply that same approach to a completely unfamiliar problem?",
    ],
}

MAX_FOLLOW_UPS_PER_QUESTION = 2


def select_follow_up_question(follow_up_type, question_id, asked_follow_ups):
    """
    Pick a follow-up question of the given type that hasn't already been
    asked for this question_id, preventing repetitive questioning.

    asked_follow_ups: dict of {question_id: [follow_up_texts_already_used]}
    """
    if follow_up_type is None:
        return None

    already_asked = asked_follow_ups.get(question_id, [])
    if len(already_asked) >= MAX_FOLLOW_UPS_PER_QUESTION:
        logger.info(f"Max follow-ups reached for {question_id}, moving on")
        return None

    candidates = FOLLOW_UP_TEMPLATES.get(follow_up_type, [])
    unused = [q for q in candidates if q not in already_asked]

    if not unused:
        return None  # exhausted all templates for this type

    selected = unused[0]
    asked_follow_ups.setdefault(question_id, []).append(selected)
    return selected


def decide_next_action(follow_up_type, question_id, asked_follow_ups, base_eligible=True):
    """
    The core decision tree for Day 34: given the classified follow-up
    need (Day 34 Step 1), the question's base eligibility (Day 33's
    follow_up_eligible flag), and repeat-prevention state, decide the
    single next action.

    Returns one of: 'ask_follow_up' (with question text), 'move_to_next'
    """
    if not base_eligible:
        return {"action": "move_to_next", "follow_up_text": None, "reason": "question not follow_up_eligible"}

    if follow_up_type is None:
        return {"action": "move_to_next", "follow_up_text": None, "reason": "no follow-up need detected"}

    follow_up_text = select_follow_up_question(follow_up_type, question_id, asked_follow_ups)

    if follow_up_text is None:
        return {"action": "move_to_next", "follow_up_text": None, "reason": "follow-up limit reached or templates exhausted"}

    return {"action": "ask_follow_up", "follow_up_text": follow_up_text, "reason": follow_up_type}