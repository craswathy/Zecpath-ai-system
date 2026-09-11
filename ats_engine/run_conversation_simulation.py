import json
from ats_engine.conversation_state_machine import ConversationStateMachine, CallState
from ats_engine.fallback_questions import get_fallback_question, get_polite_closing_message
from utils.logger import logger

def run():
    with open("data/screening_questions/jd_data_analyst_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    # Simulated sequence of events for one demo call --
    # mixes normal answers, silence, and an off-topic answer to show all paths
    simulated_events = [
        "answer_received_ok",      # Q1 answered fine
        "silence_detected",        # Q2 silence...
        "answer_received_ok",      # ...then answered on retry
        "off_topic_detected",      # Q3 off-topic...
        "off_topic_detected",      # ...off-topic again...
        "answer_received_ok",      # ...answered correctly on 3rd try
        "answer_received_ok",      # Q4 fine
        "vague_answer",            # Q5 vague...
        "answer_received_ok",      # ...answered on retry
    ]

    sm = ConversationStateMachine(call_id="demo_call_01", questions=questions)
    call_log = []

    sm.transition("start")  # GREETING -> ASKING_QUESTION

    event_index = 0
    while sm.state not in (CallState.ENDED_SUCCESS, CallState.ENDED_FAILURE):
        sm.transition("ask")  # ASKING_QUESTION -> AWAITING_ANSWER

        if event_index >= len(simulated_events):
            break

        event = simulated_events[event_index]
        event_index += 1

        current_q = sm.current_question()
        new_state = sm.transition(event)

        log_entry = {
            "question": current_q["prompt_text"] if current_q else None,
            "event": event,
            "resulting_state": new_state.value,
        }

        if new_state == CallState.CLARIFYING and current_q:
            fallback_reason = event
            fallback_text = get_fallback_question(fallback_reason, current_q["category"])
            log_entry["ai_says"] = fallback_text

        call_log.append(log_entry)

        if new_state == CallState.MOVING_TO_NEXT:
            sm.transition("advance")

    closing_message = get_polite_closing_message("normal_completion")
    call_log.append({"ai_says": closing_message, "resulting_state": "ended"})

    output = {"call_id": sm.call_id, "call_log": call_log, "final_state": sm.state.value}

    with open("data/conversation_simulation_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Done. Simulated call with {len(call_log)} steps. Final state: {sm.state.value}")
    print("Check data/conversation_simulation_result.json")

if __name__ == "__main__":
    run()