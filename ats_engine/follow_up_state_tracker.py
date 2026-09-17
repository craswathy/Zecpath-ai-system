from ats_engine.follow_up_trigger_detector import classify_follow_up_need
from ats_engine.adaptive_questioning_framework import decide_next_action
from utils.logger import logger


class FollowUpStateTracker:
    """
    Wraps Day 33's HRInterviewState with dynamic follow-up tracking:
    remembers which follow-ups have already been asked per question,
    so the same probe is never repeated, and provides one method the
    conversation flow (Day 29/33) can call after each answer.
    """

    def __init__(self):
        self.asked_follow_ups = {}  # {question_id: [follow_up_texts]}
        self.follow_up_history = []

    def process_answer(self, question_id, answer_text, is_vague_or_missing, base_follow_up_eligible):
        """
        Given a candidate's answer to a question, decide the next action:
        ask a follow-up (and which one) or move on.
        """
        follow_up_type = classify_follow_up_need(answer_text, is_vague_or_missing)
        decision = decide_next_action(
            follow_up_type, question_id, self.asked_follow_ups, base_follow_up_eligible
        )

        self.follow_up_history.append({
            "question_id": question_id,
            "answer_text": answer_text,
            "follow_up_type_detected": follow_up_type,
            "decision": decision,
        })

        logger.info(f"Follow-up decision for {question_id}: {decision['action']} ({decision['reason']})")
        return decision

    def get_follow_up_count(self, question_id):
        return len(self.asked_follow_ups.get(question_id, []))