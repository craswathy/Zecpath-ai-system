from ats_engine.follow_up_trigger_detector import classify_follow_up_need
from ats_engine.adaptive_questioning_framework import decide_next_action
from utils.logger import logger

MAX_TOTAL_FOLLOW_UPS = 6


class FollowUpStateTracker:
    """
    Tracks follow-ups per question (never repeat a probe) and per interview
    (never let follow-ups take over the whole interview).
    """

    def __init__(self, max_total_follow_ups=MAX_TOTAL_FOLLOW_UPS):
        self.asked_follow_ups = {}  # {question_id: [follow_up_texts]}
        self.follow_up_history = []
        self.max_total_follow_ups = max_total_follow_ups

    def total_follow_ups_asked(self):
        return sum(len(v) for v in self.asked_follow_ups.values())

    def process_answer(self, question_id, answer_text, is_vague_or_missing, base_follow_up_eligible):
        follow_up_type = classify_follow_up_need(answer_text, is_vague_or_missing)

        if self.total_follow_ups_asked() >= self.max_total_follow_ups:
            decision = {"action": "move_to_next", "follow_up_text": None,
                        "reason": "interview follow-up cap reached"}
        else:
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