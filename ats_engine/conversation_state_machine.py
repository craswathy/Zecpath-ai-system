from enum import Enum
from utils.logger import logger


class CallState(Enum):
    GREETING = "greeting"
    ASKING_QUESTION = "asking_question"
    AWAITING_ANSWER = "awaiting_answer"
    CLARIFYING = "clarifying"
    FOLLOWING_UP = "following_up"
    MOVING_TO_NEXT = "moving_to_next"
    CLOSING = "closing"
    ENDED_SUCCESS = "ended_success"
    ENDED_FAILURE = "ended_failure"


class ConversationStateMachine:
    """
    Tracks the state of one live screening call, from Day 22's question
    bank through Day 25's answer understanding, deciding what happens next
    at each step (ask next question, retry, clarify, or end the call).
    """

    def __init__(self, call_id, questions, max_retries_per_question=2, max_silence_retries=1):
        self.call_id = call_id
        self.questions = questions  # from Day 22's build_conversation_questions()
        self.current_index = 0
        self.state = CallState.GREETING
        self.retry_count = 0
        self.silence_count = 0
        self.max_retries_per_question = max_retries_per_question
        self.max_silence_retries = max_silence_retries
        self.history = []

    def current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def transition(self, event, event_data=None):
        """
        Advance the state machine based on an event (e.g. 'answer_received',
        'silence_detected', 'off_topic_detected', 'question_answered').
        """
        logger.info(f"[{self.call_id}] State={self.state.value}, Event={event}")
        self.history.append({"state": self.state.value, "event": event})

        if self.state == CallState.GREETING:
            self.state = CallState.ASKING_QUESTION

        elif self.state == CallState.ASKING_QUESTION:
            self.state = CallState.AWAITING_ANSWER

        elif self.state == CallState.AWAITING_ANSWER:
            self.state = self._handle_answer_event(event, event_data)

        elif self.state == CallState.CLARIFYING:
            self.state = self._handle_answer_event(event, event_data)

        elif self.state == CallState.MOVING_TO_NEXT:
            self.current_index += 1
            self.retry_count = 0
            if self.current_index >= len(self.questions):
                self.state = CallState.CLOSING
            else:
                self.state = CallState.ASKING_QUESTION

        elif self.state == CallState.CLOSING:
            self.state = CallState.ENDED_SUCCESS

        return self.state

    def _handle_answer_event(self, event, event_data):
        """Core decision logic: what to do based on the quality of the answer received."""
        if event == "silence_detected":
            self.silence_count += 1
            if self.silence_count > self.max_silence_retries:
                return CallState.MOVING_TO_NEXT  # give up on this question, move on
            return CallState.CLARIFYING  # re-prompt once

        if event == "off_topic_detected" or event == "vague_answer":
            self.retry_count += 1
            if self.retry_count > self.max_retries_per_question:
                return CallState.MOVING_TO_NEXT  # accept what we have, move on
            return CallState.CLARIFYING  # ask a fallback/clarifying question

        if event == "answer_received_ok":
            self.silence_count = 0
            self.retry_count = 0
            return CallState.MOVING_TO_NEXT

        if event == "call_dropped":
            return CallState.ENDED_FAILURE

        return CallState.MOVING_TO_NEXT