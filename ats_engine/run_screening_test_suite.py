import json
from ats_engine.conversation_state_machine import ConversationStateMachine, CallState
from ats_engine.fallback_questions import get_fallback_question, get_polite_closing_message
from utils.logger import logger

# Multiple simulated candidates, covering different behavior patterns --
# this is what "run simulated AI screening calls" means at this stage,
# since real live calls aren't available.
TEST_SCENARIOS = {
    "ideal_candidate": [
        "answer_received_ok", "answer_received_ok", "answer_received_ok",
        "answer_received_ok", "answer_received_ok",
    ],
    "hesitant_candidate": [
        "silence_detected", "answer_received_ok", "silence_detected",
        "answer_received_ok", "vague_answer", "answer_received_ok",
    ],
    "off_topic_candidate": [
        "off_topic_detected", "off_topic_detected", "off_topic_detected",
        "answer_received_ok", "answer_received_ok",
    ],
    "dropped_call_candidate": [
        "answer_received_ok", "call_dropped",
    ],
}


def simulate_call(scenario_name, events, questions):
    sm = ConversationStateMachine(call_id=scenario_name, questions=questions)
    call_log = []
    sm.transition("start")

    event_index = 0
    while sm.state not in (CallState.ENDED_SUCCESS, CallState.ENDED_FAILURE):
        sm.transition("ask")
        if event_index >= len(events):
            break
        event = events[event_index]
        event_index += 1
        new_state = sm.transition(event)
        call_log.append({"event": event, "resulting_state": new_state.value})
        if new_state == CallState.MOVING_TO_NEXT:
            sm.transition("advance")
        if new_state == CallState.ENDED_FAILURE:
            break

    return {
        "scenario": scenario_name,
        "final_state": sm.state.value,
        "questions_reached": sm.current_index,
        "total_questions": len(questions),
        "call_log": call_log,
    }


def run():
    with open("data/screening_questions/jd_data_analyst_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    results = []
    for scenario_name, events in TEST_SCENARIOS.items():
        result = simulate_call(scenario_name, events, questions)
        results.append(result)
        logger.info(f"Scenario '{scenario_name}': ended at {result['final_state']}, reached {result['questions_reached']}/{result['total_questions']} questions")

    output_path = "data/screening_test_suite_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Ran {len(results)} test scenarios. Check {output_path}")
    for r in results:
        print(f"  {r['scenario']}: {r['final_state']} ({r['questions_reached']}/{r['total_questions']} questions reached)")

if __name__ == "__main__":
    run()