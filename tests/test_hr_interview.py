import sys
sys.path.append(".")
from ats_engine.hr_interview_question_bank import get_questions_for_candidate
from ats_engine.hr_interview_state import HRInterviewState, InterviewPhase

def test_fresher_gets_fresher_specific_questions():
    questions = get_questions_for_candidate(seniority="fresher", role_type="all")
    ids = [q["id"] for q in questions]
    assert "hr_journey_02" in ids
    assert "hr_journey_01" not in ids

def test_experienced_gets_experienced_specific_questions():
    questions = get_questions_for_candidate(seniority="experienced", role_type="all")
    ids = [q["id"] for q in questions]
    assert "hr_journey_01" in ids
    assert "hr_journey_02" not in ids

def test_state_starts_at_introduction():
    state = HRInterviewState("test_int", "test_cand", get_questions_for_candidate("fresher", "all"))
    assert state.phase == InterviewPhase.INTRODUCTION

def test_state_advances_phase_when_questions_exhausted():
    questions = get_questions_for_candidate("fresher", "all")
    state = HRInterviewState("test_int", "test_cand", questions)
    state.advance_question()
    assert state.phase != InterviewPhase.INTRODUCTION or state.current_question_index > 0