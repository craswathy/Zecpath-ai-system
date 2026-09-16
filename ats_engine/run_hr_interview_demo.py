import json
from ats_engine.hr_interview_question_bank import get_questions_for_candidate
from ats_engine.hr_interview_state import HRInterviewState, InterviewPhase
from utils.logger import logger

def run():
    questions = get_questions_for_candidate(seniority="fresher", role_type="technical")

    state = HRInterviewState(interview_id="hrint_001", candidate_id="cand_00123", questions=questions)

    demo_log = []
    demo_responses = [
        "I'm a recent MSc Statistics graduate with a strong interest in data science.",
        "My capstone project on retail recommendation systems really shaped my interest in ML.",
        "I'd say my analytical thinking is my biggest strength.",
        "I collaborate well by staying organized and communicating early about blockers.",
        "In 2-3 years I hope to grow into a senior data scientist role.",
        "I'm comfortable with occasional flexible hours when needed.",
    ]

    response_index = 0
    while state.phase != InterviewPhase.ENDED and response_index < len(demo_responses):
        current_q = state.current_question()
        if current_q is None:
            state._advance_phase()
            continue

        response_text = demo_responses[response_index]
        response_index += 1

        state.capture_response(current_q["id"], response_text)
        demo_log.append({
            "phase": state.phase.value,
            "question_id": current_q["id"],
            "question_text": current_q["text"],
            "response": response_text,
            "follow_up_eligible": state.is_follow_up_eligible(current_q["id"]),
        })

        state.advance_question()

    output = {
        "interview_id": state.interview_id,
        "final_phase": state.phase.value,
        "total_responses_captured": len(state.responses),
        "interview_log": demo_log,
    }

    with open("data/hr_interview_demo_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Done. HR interview demo completed. Final phase: {state.phase.value}")
    print(f"Check data/hr_interview_demo_result.json")

if __name__ == "__main__":
    run()