# JSON Schema definitions for API request/response validation.
# These mirror the resume_schema.json / jd_schema.json from Day 4,
# adapted for API contract use.

RESUME_UPLOAD_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
    },
}

RESUME_UPLOAD_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["candidate_id", "status", "stage"],
    "properties": {
        "candidate_id": {"type": "string"},
        "status": {"type": "string", "enum": ["pending", "processing", "complete", "failed"]},
        "stage": {"type": "string", "enum": ["uploaded", "parsed", "ats_scored", "screening_complete", "interview_complete", "decision_complete"]},
    },
}

SCORE_REQUEST_SCHEMA = {
    "type": "object",
    "required": ["candidate_id", "job_id"],
    "properties": {
        "candidate_id": {"type": "string"},
        "job_id": {"type": "string"},
        "role_category": {"type": "string", "enum": ["technical", "business", "entry_level"]},
    },
}

SCORE_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["candidate_id", "job_id", "final_score", "component_scores"],
    "properties": {
        "candidate_id": {"type": "string"},
        "job_id": {"type": "string"},
        "final_score": {"type": "number", "minimum": 0, "maximum": 100},
        "component_scores": {
            "type": "object",
            "properties": {
                "skill_match": {"type": ["number", "null"]},
                "experience_relevance": {"type": ["number", "null"]},
                "education_alignment": {"type": ["number", "null"]},
                "semantic_similarity": {"type": ["number", "null"]},
            },
        },
        "explanation": {"type": "string"},
    },
}

SHORTLIST_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["job_id", "shortlisted", "needs_review", "auto_rejected"],
    "properties": {
        "job_id": {"type": "string"},
        "shortlisted": {"type": "array"},
        "needs_review": {"type": "array"},
        "auto_rejected": {"type": "array"},
    },
}

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "candidate_id": {"type": "string"},
            },
        },
    },
}