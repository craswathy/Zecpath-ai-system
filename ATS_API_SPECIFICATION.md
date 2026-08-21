# ATS API Specification -- Zecpath

## Overview
This document defines the REST API surface that exposes the ATS pipeline
(Days 5-15: extraction, parsing, scoring, ranking) to backend/frontend
consumers, per the Day 2 architecture (REST for sync calls, Queue+Webhook
for async jobs).

## Endpoints

### 1. Resume Upload
`POST /api/v1/resumes`

Uploads a raw resume file, stores it, and kicks off the extraction pipeline.

**Request:** multipart/form-data
- `file`: PDF or DOCX file
- `candidate_id`: string (optional, generated if omitted)

**Response (202 Accepted -- async):**
```json
{
  "candidate_id": "cand_00123",
  "status": "processing",
  "stage": "uploaded"
}
```

### 2. Get Parsing Result
`GET /api/v1/resumes/{candidate_id}`

Fetch the parsed candidate profile once extraction/section-classification/
skill/experience/education parsing (Days 5, 8-11) has completed.

**Response (200 OK):**
```json
{
  "candidate_id": "cand_00123",
  "status": "complete",
  "stage": "parsed",
  "profile": { "skills": [...], "experience": [...], "education": [...] }
}
```
**Response (202 Accepted -- still processing):**
```json
{ "candidate_id": "cand_00123", "status": "processing", "stage": "parsed" }
```

### 3. Score Candidate Against Job
`POST /api/v1/scores`

Triggers ATS scoring (Day 13) for a candidate against a specific job.
Synchronous -- caller waits for the response.

**Request:**
```json
{ "candidate_id": "cand_00123", "job_id": "job_00045", "role_category": "technical" }
```

**Response (200 OK):**
```json
{
  "candidate_id": "cand_00123",
  "job_id": "job_00045",
  "final_score": 78.4,
  "component_scores": { "skill_match": 0.82, "experience_relevance": 0.7, "education_alignment": 0.9, "semantic_similarity": 0.75 },
  "explanation": "Skill Match: 0.82 (weight 0.45) | ..."
}
```

### 4. Get Shortlist for a Job
`GET /api/v1/jobs/{job_id}/shortlist`

Returns the ranked, shortlisted candidates (Day 14) for a given job posting.

**Response (200 OK):**
```json
{
  "job_id": "job_00045",
  "shortlisted": [
    { "candidate_id": "cand_00123", "rank": 1, "final_score": 84.2, "decision_zone": "Shortlisted" }
  ],
  "needs_review": [ ... ],
  "auto_rejected": [ ... ]
}
```

## Async Job Handling
- Resume upload (`POST /resumes`) is async: returns `202 Accepted` immediately
  with `status: processing`, since extraction + parsing takes time (Day 2
  pattern: Queue -> Webhook).
- A `webhook_url` can optionally be supplied at upload time; the platform
  calls it once `stage` reaches `parsed`, so backend doesn't need to poll.
- Scoring (`POST /scores`) is synchronous, since it operates on already-parsed
  data and completes in milliseconds (Day 13's scoring is pure computation,
  no external calls).

## Error Standards
All error responses follow one shape:
```json
{
  "error": {
    "code": "RESUME_PARSE_FAILED",
    "message": "Could not extract text -- file may be a scanned image with no text layer.",
    "candidate_id": "cand_00123"
  }
}
```

| HTTP Status | Meaning |
|---|---|
| 400 | Bad request (missing/invalid fields) |
| 404 | Candidate or job not found |
| 422 | File uploaded but unparseable (e.g. scanned PDF, per Day 5's known limitation) |
| 500 | Internal processing error |

## Logging Standard
Every API call logs (via `utils/logger.py`, Day 3): endpoint, `candidate_id`/`job_id`,
timestamp, response status, and processing duration -- consistent with the
metadata standard from Day 7 (`stage`, `status`, `timestamp`).