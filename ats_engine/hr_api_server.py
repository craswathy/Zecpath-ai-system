from typing import List, Literal, Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ats_engine.answer_extractor import is_vague_or_missing
from ats_engine.follow_up_state_tracker import FollowUpStateTracker
from ats_engine.hr_interview_question_bank import get_questions_for_candidate
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from ats_engine.hr_interview_state import HRInterviewState
from ats_engine.hr_score_normalizer import normalize_for_interview_length
from ats_engine.transcript_normalizer import normalize_transcript_text
from utils.logger import logger

app = FastAPI(title="Zecpath HR Interview API", version="1.0")

# In-memory sessions: lost on restart, not safe across several workers.
# A real deployment needs persistent storage (see the Day 7 storage design).
SESSIONS = {}


class StartInterviewRequest(BaseModel):
    candidate_id: str
    job_id: str
    seniority: Literal["fresher", "experienced"]
    role_type: Literal["technical", "non_technical", "all"] = "all"


class AnswerRequest(BaseModel):
    question_id: str
    answer_text: str
    is_follow_up: bool = False


class TurnData(BaseModel):
    is_off_topic: bool
    is_vague_or_missing: bool
    communication_score: Optional[float] = None
    behavioral_confidence_score: Optional[float] = None


class ScoreRequest(BaseModel):
    per_turn_data: List[TurnData]
    contradiction_count: int = Field(default=0, ge=0)
    role_category: Optional[Literal["technical", "client_facing", "senior"]] = None


def _error(status_code, code, message):
    """One error shape for the whole API."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _question_view(question):
    if question is None:
        return None
    return {
        "id": question["id"],
        "category": question["category"],
        "text": question["text"],
        "follow_up_eligible": question["follow_up_eligible"],
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    fields = [".".join(str(part) for part in err["loc"]) for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "INVALID_REQUEST", "message": "Request failed validation.", "fields": fields}},
    )


@app.post("/api/v1/hr-interviews", status_code=201)
def start_interview(req: StartInterviewRequest):
    questions = get_questions_for_candidate(seniority=req.seniority, role_type=req.role_type)
    interview_id = f"hrint_{len(SESSIONS) + 1:04d}"
    state = HRInterviewState(interview_id, req.candidate_id, questions)
    SESSIONS[interview_id] = {"state": state, "tracker": FollowUpStateTracker(), "job_id": req.job_id}
    logger.info(f"Started HR interview {interview_id} for {req.candidate_id}")

    return {
        "interview_id": interview_id,
        "candidate_id": req.candidate_id,
        "job_id": req.job_id,
        "phase": state.phase.value,
        "question_count": len(questions),
        "first_question": _question_view(state.current_question()),
    }


@app.get("/api/v1/hr-interviews/{interview_id}")
def get_interview(interview_id: str):
    session = SESSIONS.get(interview_id)
    if session is None:
        return _error(404, "INTERVIEW_NOT_FOUND", f"No interview with id {interview_id}.")

    state = session["state"]
    tracker = session["tracker"]
    return {
        "interview_id": interview_id,
        "candidate_id": state.candidate_id,
        "job_id": session["job_id"],
        "phase": state.phase.value,
        "responses_captured": len(state.responses),
        "follow_ups_asked": sum(len(v) for v in tracker.asked_follow_ups.values()),
    }


@app.post("/api/v1/hr-interviews/{interview_id}/answers")
def submit_answer(interview_id: str, req: AnswerRequest):
    session = SESSIONS.get(interview_id)
    if session is None:
        return _error(404, "INTERVIEW_NOT_FOUND", f"No interview with id {interview_id}.")

    state = session["state"]
    tracker = session["tracker"]

    current = state.current_question()
    if current is None:
        return _error(409, "INTERVIEW_COMPLETE", "No further questions in this interview.")
    if req.question_id != current["id"]:
        return _error(409, "QUESTION_MISMATCH", f"Expected an answer to {current['id']}.")

    clean_text = normalize_transcript_text(req.answer_text)
    vague = is_vague_or_missing(clean_text)
    eligible = state.is_follow_up_eligible(req.question_id)

    state.capture_response(req.question_id, clean_text, is_follow_up=req.is_follow_up)
    decision = tracker.process_answer(req.question_id, clean_text, vague, eligible)

    next_question = None
    if decision["action"] == "move_to_next":
        state.advance_question()
        next_question = _question_view(state.current_question())

    return {
        "interview_id": interview_id,
        "question_id": req.question_id,
        "normalized_answer": clean_text,
        "is_vague_or_missing": vague,
        "follow_up": decision,
        "phase": state.phase.value,
        "next_question": next_question,
    }


@app.post("/api/v1/hr-interviews/{interview_id}/score")
def score_interview(interview_id: str, req: ScoreRequest):
    if interview_id not in SESSIONS:
        return _error(404, "INTERVIEW_NOT_FOUND", f"No interview with id {interview_id}.")

    turns = [turn.model_dump() for turn in req.per_turn_data]
    result = compute_hr_interview_score(turns, req.contradiction_count, req.role_category)
    return normalize_for_interview_length(result)