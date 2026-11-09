# Logging Structure -- Zecpath (Day 61)

All logs are JSON lines (one JSON object per line), written by
ats_engine/observability.py to data/observability/.

## Common fields (every log)
timestamp (ISO 8601), request_id (links one request across logs),
candidate_id and job_id where relevant.

## 1. API log (api_log.jsonl)
| Field | Example |
|---|---|
| endpoint | POST /api/v1/scores |
| status_code | 200 |
| duration_ms | 1.84 |

## 2. Model output log (model_output_log.jsonl)
| Field | Example |
|---|---|
| model_name | ats_scorer |
| model_version | ats_v1.0 |
| score | 72.4 |
| duration_ms | 1.2 |

## 3. Error log (error_log.jsonl)
| Field | Example |
|---|---|
| endpoint | POST /api/v1/resumes |
| error_code | RESUME_PARSE_FAILED |
| message | No text layer (scanned PDF) |
| retryable | false |

## 4. Decision audit log (decision_audit_log.jsonl)
| Field | Example |
|---|---|
| decision | Moderate Fit |
| hiring_fit_percentage | 68.5 |
| model_version | unified_v1.0 |
| flags | ["Weak round(s): hr_interview ..."] |

## Log levels (application logger from Day 3)
INFO for normal flow, WARNING for recoverable issues, ERROR for failures.

## Rules
1. Never log personal data (name, email, phone, resume text, transcripts, answers).
2. Every log line carries request_id.
3. Audit logs are append-only and kept longer than operational logs.
4. Every model output and decision includes model_version.