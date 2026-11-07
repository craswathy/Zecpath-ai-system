# AI Integration Document -- Zecpath (Day 59)

## 1. Purpose
Defines how every AI module connects to the backend, the database and
external systems. It extends the Day 2 architecture, the Day 16 ATS API
and the Day 32 screening API design.

## 2. AI APIs

| API | Base path | Built from | Mode | Status |
|---|---|---|---|---|
| Resume Parsing API | /api/v1/resumes | Days 5-11 | Async | Day 16 stub exists |
| ATS Scoring API | /api/v1/scores | Days 12-15 | Sync | Day 16 stub exists |
| Screening AI API | /api/v1/screening/calls | Days 22-31 | Async | Design only (Day 32) |
| Interview AI API | /api/v1/interviews | Days 33-45 | Sync scoring, async session | See HR API specification (Day 44) |
| Decision AI API | /api/v1/decisions | Days 41, 51-52 | Sync | Design only |

Note: align the Interview AI paths with HR_API_SPECIFICATION.md from Day 44
if the endpoint names differ.

## 3. Backend to AI to Database interactions

| Flow | Backend does | AI service does | Database write |
|---|---|---|---|
| Resume upload | Stores file, calls Resume Parsing API | Extract, clean, segment, parse, return job id | Raw file to object storage, parsed profile to document DB |
| ATS scoring | Calls ATS Scoring API with candidate id and job id | Reads parsed profile, computes score, ranks | Score record to relational DB |
| Screening call | Enqueues call request | Runs call, transcribes, scores, builds report | Transcript to document DB, audio to object storage, report to relational DB |
| Interview scoring | Sends answer turns | Scores communication, confidence, relevance in real time | Turn scores to document DB |
| Final decision | Calls Decision AI API with all round scores | Unified score, fit category, flags | Decision record plus audit log entry |

Every record carries the Day 7 metadata: candidate_id, job_id,
model_version, timestamp, stage, status.

## 4. Sync vs async

| Process | Mode | Reason |
|---|---|---|
| Resume processing | Async | Extraction, parsing and embeddings take seconds to minutes. Backend gets 202 and a job_id, then polls or receives a webhook. |
| Screening call | Async | A call takes minutes and depends on telephony and speech-to-text. |
| Real-time interview scoring | Sync | The next question depends on the score, so the caller waits. Target under 2 seconds per turn. |
| ATS scoring | Sync | Pure computation on already parsed data. |
| Final decision | Sync | Pure computation on stored round scores. |

Async pattern: backend sends request, AI returns 202 with job_id, work runs
through a queue, AI sends a signed webhook on completion, backend can also
poll GET /jobs/{job_id}.

## 5. Error handling and retries

Error shape (same as Day 16):
error.code, error.message, error.request_id, error.retryable (true or false).

| HTTP status | Meaning | Retry? |
|---|---|---|
| 400 | Invalid request | No |
| 401 / 403 | Auth failed or not allowed | No |
| 404 | Candidate, job or call not found | No |
| 409 | Duplicate (same idempotency key) | No, return the original result |
| 422 | File unreadable (scanned PDF, no text) | No, flag for manual review |
| 429 | Rate limited | Yes, honour Retry-After |
| 500 / 503 / 504 | AI service error or timeout | Yes |

Retry policy:
- Exponential backoff 1s, 2s, 4s with a small random jitter, maximum 3 attempts.
- Every POST carries an Idempotency-Key header so a retry never creates a duplicate job.
- After the last failed attempt the job goes to a dead-letter queue and the candidate is marked "needs manual review". It is never auto-rejected because of a system failure.
- Webhook delivery retries at 1 min, 5 min and 30 min, then falls back to polling.
- Circuit breaker: if an AI service fails 5 times in a row, the backend pauses calls for 60 seconds.
- Dropped call or poor audio handling follows the Day 31 safety framework.

## 6. Authentication and security

- Service to service: signed JWT or API key per calling service, rotated regularly, stored in a secrets manager and never in code or the repository.
- Roles: recruiter, admin and service roles. Recruiters see only their own company's candidates (multi-tenant isolation by company_id).
- Transport: HTTPS with TLS only.
- Webhooks: signed with an HMAC header, timestamp checked to prevent replay.
- Rate limits per client and per endpoint.
- Personal data: name, email, phone and similar fields are masked before scoring (Day 15). Logs never contain raw resume text or transcripts.
- Consent: the screening and interview APIs refuse to start unless a stored consent record exists (Day 43).
- Retention: transcripts and recordings are deleted on the retention schedule defined in Day 43.
- Audit: every score, decision and data access is logged with who, what, when and which model_version.

## 7. Model versioning
Every response includes model_version. A new model runs side by side
with the old one. Old scores stay traceable to the version that produced them.

## 8. Known limitations
- Only the ATS and HR APIs have working code stubs. The screening, technical interview and decision APIs are design only.
- No real queue, database or authentication is connected yet.
- Latency targets are design goals, not measured values.
- The demo data does not share candidate IDs across rounds (Day 41 note).

