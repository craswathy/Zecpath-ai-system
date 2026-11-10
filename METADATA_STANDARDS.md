# Metadata Standards -- Zecpath AI

Every record produced by an AI module carries these fields so that any
result can be traced back to a candidate, a job, a model and a moment.

| Field | Type | Description |
|---|---|---|
| candidate_id | string | Unique candidate identifier |
| job_id | string | Unique job posting identifier |
| model_version | string | Version of the model that produced the result, for example ats_v1.0 |
| timestamp | ISO 8601 string | When the record was created |
| stage | string | Pipeline stage, for example parsed, ats_scored, screening_complete, unified_scored |
| status | string | pending, processing, complete or failed |

## Rules
1. Every score, report and decision includes model_version.
2. Timestamps use ISO 8601.
3. Old records are never overwritten when a model changes. The new
   version writes a new record, so old scores stay traceable.
4. Metadata fields never contain personal data such as names, emails or phone numbers.

## Where it is used
- Request and response schemas: api_schemas_day59.json
- Unified candidate score object: ats_engine/unified_candidate_object.py
- Logs and decision audit trail: LOGGING_STRUCTURE.md
- Transcript metadata extends this standard: TRANSCRIPT_METADATA_STANDARDS.md