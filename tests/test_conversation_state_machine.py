import sys
sys.path.append(".")
from ats_engine.conversation_state_machine import ConversationStateMachine, CallState
from ats_engine.call_error_handler import classify_answer_event

def test_state_machine_moves_forward_on_good_answer():
    sm = ConversationStateMachine("test_call", questions=[{"prompt_text": "Q1", "category": "Skills"}])
    sm.transition("start")
    sm.transition("ask")
    state = sm.transition("answer_received_ok")
    assert state == CallState.MOVING_TO_NEXT

def test_state_machine_retries_on_silence():
    sm = ConversationStateMachine("test_call", questions=[{"prompt_text": "Q1", "category": "Skills"}])
    sm.transition("start")
    sm.transition("ask")
    state = sm.transition("silence_detected")
    assert state == CallState.CLARIFYING

def test_state_machine_gives_up_after_max_retries():
    sm = ConversationStateMachine("test_call", questions=[{"prompt_text": "Q1", "category": "Skills"}], max_silence_retries=1)
    sm.transition("start")
    sm.transition("ask")
    sm.transition("silence_detected")
    state = sm.transition("silence_detected")
    assert state == CallState.MOVING_TO_NEXT

def test_classify_answer_event_silence():
    event = classify_answer_event({"text": "", "confidence": 0.0}, {})
    assert event == "silence_detected"

def test_classify_answer_event_ok():
    event = classify_answer_event(
        {"text": "I have three years experience", "confidence": 0.9},
        {"is_off_topic": False, "structured_answer": {"is_vague_or_missing": False}}
    )
    assert event == "answer_received_ok"