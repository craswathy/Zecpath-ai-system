from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from ats_engine.ats_scorer import compute_ats_score
from utils.logger import logger

app = FastAPI(title="Zecpath ATS API", version="1.0")


class ScoreRequest(BaseModel):
    candidate_id: str
    job_id: str
    role_category: Optional[str] = None


@app.post("/api/v1/resumes")
def upload_resume(candidate_id: Optional[str] = None):
    """Stub: in production, accepts multipart file upload and enqueues extraction."""
    cid = candidate_id or "cand_generated_id"
    logger.info(f"Resume upload received for {cid}")
    return {"candidate_id": cid, "status": "processing", "stage": "uploaded"}


@app.get("/api/v1/resumes/{candidate_id}")
def get_resume_status(candidate_id: str):
    """Stub: in production, looks up real parsing status from storage (Day 7)."""
    return {"candidate_id": candidate_id, "status": "complete", "stage": "parsed"}


@app.post("/api/v1/scores")
def score_candidate(req: ScoreRequest):
    """Synchronous scoring endpoint, wraps Day 13's compute_ats_score."""
    # In production, candidate_data/jd_data would be loaded from storage by ID
    candidate_data = {"skills": [], "experience_summary": None, "education_relevance": None, "semantic_match": None}
    jd_data = {"required_skills": []}

    result = compute_ats_score(candidate_data, jd_data, role_category=req.role_category)
    result["candidate_id"] = req.candidate_id
    result["job_id"] = req.job_id
    return result


@app.get("/api/v1/jobs/{job_id}/shortlist")
def get_shortlist(job_id: str):
    """Stub: in production, reads Day 14's ranking output for this job."""
    return {"job_id": job_id, "shortlisted": [], "needs_review": [], "auto_rejected": []}