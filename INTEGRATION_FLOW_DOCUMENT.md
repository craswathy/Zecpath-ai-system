# ATS API Integration Flow -- Zecpath

## Flow: Resume Upload to Shortlist

1. **Backend** calls `POST /api/v1/resumes` with the candidate's file.
2. **ATS API** returns `202 Accepted` immediately (`status: processing`) --
   does not block, per Day 2's async design for slow operations.
3. Internally, the extraction pipeline runs (Day 5 extraction, Day 8
   section classification, Days 9-11 skill/experience/education parsing).
4. Once complete, **Backend** either polls `GET /api/v1/resumes/{id}`
   or receives a webhook callback (if `webhook_url` was supplied).
5. **Backend** calls `POST /api/v1/scores` with `candidate_id` + `job_id` --
   this is synchronous, since Day 13's scoring is pure computation on
   already-parsed data.
6. **Recruiter Dashboard** calls `GET /api/v1/jobs/{job_id}/shortlist` at
   any time to fetch the current ranked list (Day 14's output), grouped
   into Shortlisted / Needs Review / Auto-Rejected.

## Error Handling in the Flow
- If resume parsing fails (e.g. scanned PDF, Day 5's known limitation),
  `stage` stays at `uploaded` and a `422` is returned on status check,
  with `error.code: RESUME_PARSE_FAILED`.
- If scoring is requested before parsing completes, `POST /scores`
  returns `400` with a clear message rather than silently scoring
  incomplete data (ties to Day 13's missing-data handling).

## Consistency with Earlier Days
- Endpoint responses reuse the exact field names from Day 4's schemas
  (`candidate_id`, `job_id`) and Day 7's metadata standard (`stage`, `status`).
- Async/sync split matches Day 2's architecture decision exactly:
  slow AI work (extraction, parsing) is async; fast computation (scoring)
  is sync.