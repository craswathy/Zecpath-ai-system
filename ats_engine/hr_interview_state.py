from enum import Enum
from utils.logger import logger


class InterviewPhase(Enum):
    INTRODUCTION = "introduction"
    CORE_HR_QUESTIONS = "core_hr_questions"
    ROLE_BASED_EVALUATION = "role_based_evaluation"
    CLOSING = "closing"
    ENDED = "ended"


PHASE_CATEGORY_MAP = {
    InterviewPhase.INTRODUCTION: ["Self-Introduction"],
    InterviewPhase.CORE_HR_QUESTIONS: ["Career Journey", "Strengths & Weaknesses", "Teamwork & Culture Fit"],
    InterviewPhase.ROLE_BASED_EVALUATION: ["Career Goals", "Availability & Commitment"],
}


class HRInterviewState:
    """
    Tracks one candidate's HR interview session: current phase, which
    question is active, captured responses, and follow-up eligibility --
    extends Day 29's conversation state machine with interview-specific
    phase structure (PRD Phase 14-21).
    """

    def __init__(self, interview_id, candidate_id, questions):
        self.interview_id = interview_id
        self.candidate_id = candidate_id
        self.questions = questions
        self.phase = InterviewPhase.INTRODUCTION
        self.current_question_index = 0
        self.responses = []  # list of {question_id, response_text, follow_up_asked}

    def current_question(self):
        phase_categories = PHASE_CATEGORY_MAP.get(self.phase, [])
        phase_questions = [q for q in self.questions if q["category"] in phase_categories]
        if self.current_question_index < len(phase_questions):
            return phase_questions[self.current_question_index]
        return None

    def capture_response(self, question_id, response_text, is_follow_up=False):
        """Record a candidate's response, tagged with whether it was a follow-up answer."""
        self.responses.append({
            "question_id": question_id,
            "response_text": response_text,
            "is_follow_up": is_follow_up,
        })
        logger.info(f"[{self.interview_id}] Captured response for {question_id}")

    def is_follow_up_eligible(self, question_id):
        """Check whether the current question allows a dynamic follow-up (PRD Phase 15's adaptive questioning)."""
        question = next((q for q in self.questions if q["id"] == question_id), None)
        return question["follow_up_eligible"] if question else False

    def advance_question(self):
        """Move to the next question within the current phase, or advance the phase if exhausted."""
        self.current_question_index += 1
        if self.current_question() is None:
            self._advance_phase()

    def _advance_phase(self):
        phase_order = [
            InterviewPhase.INTRODUCTION,
            InterviewPhase.CORE_HR_QUESTIONS,
            InterviewPhase.ROLE_BASED_EVALUATION,
            InterviewPhase.CLOSING,
            InterviewPhase.ENDED,
        ]
        current_index = phase_order.index(self.phase)
        if current_index + 1 < len(phase_order):
            self.phase = phase_order[current_index + 1]
            self.current_question_index = 0
            logger.info(f"[{self.interview_id}] Advanced to phase: {self.phase.value}")