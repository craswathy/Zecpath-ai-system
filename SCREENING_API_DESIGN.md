# Screening API Design -- Zecpath

## Overview
Extends the Day 16 ATS API pattern (REST for sync, Queue+Webhook for
async) to expose the screening pipeline (Days 22-31) to backend systems.

## Endpoints

### 1. Start Screening Call
`POST /api/v1/screening/calls`
Triggers an AI voice call (async -- PRD Phase 4 pattern).
```json
{ "candidate_id": "cand_00123", "job_id": "job_00045" }
```
Response: `202 Accepted`, `{"call_id": "call_001", "status": "processing"}`

### 2. Get Call Transcript
`GET /api/v1/screening/calls/{call_id}/transcript`
Returns the structured transcript (Day 23 schema) once the call completes.

### 3. Get Screening Report
`GET /api/v1/screening/calls/{call_id}/report`
Returns the recruiter-ready report (Day 28) -- score, strengths, risks,
missing data, highlights.

## Async Design Rationale
Voice calls take minutes and depend on an external telephony/STT
pipeline -- exactly the kind of slow operation Day 2's architecture
designates for Queue+Webhook rather than a blocking REST call. The
backend enqueues the call request and gets notified (or polls) once
`data/screening_reports/{candidate_id}_screening_report.json` is ready.

## Error Handling
Reuses Day 16's error shape, with screening-specific codes:
- `CALL_DROPPED` (422) -- ties to Day 31's call_technical_failure handling
- `INSUFFICIENT_ANSWERS` (422) -- too many questions unanswered (Day 31's escalate_to_human_review)