# Transcript Metadata Standards -- Zecpath

## Purpose
Extends the Day 7 platform-wide metadata standard (candidate_id, job_id,
model_version, timestamp, stage, status) specifically for voice screening
interactions, adding fields unique to conversational data.

## Call-Level Metadata
| Field | Type | Description |
|---|---|---|
| call_id | string | Unique identifier for this screening call |
| candidate_id | string | Links to the candidate (Day 7 standard) |
| job_id | string | Links to the job posting (Day 7 standard) |
| start_timestamp / end_timestamp | ISO 8601 | Call duration boundaries |
| language | string | Language code used for the call (en, ml, hi, ta) |
| voice_profile | string | AI voice used (gender + language combination) |
| call_status | string | completed \| dropped \| no_answer \| retried |

## Turn-Level Metadata (per question-answer exchange)
| Field | Type | Description |
|---|---|---|
| turn_id | string | Unique identifier within the call |
| question_id | string | References the question bank (Day 22) |
| question_category | string | Introduction, Experience, Skills, etc. (Day 22) |
| response_confidence | number (0-1) | Speech-to-text engine's confidence in transcription accuracy |
| timestamp | ISO 8601 | When this specific turn occurred |

## Why Confidence Level Matters
`response_confidence` is critical for downstream reliability -- a low-confidence
transcription (e.g. 0.4) means the speech-to-text engine struggled (background
noise, accent, unclear audio), and any answer extraction (numeric, yes/no)
from that turn should be flagged for human review rather than trusted
outright by the eligibility engine (Day 21).

## Normalization Rules Applied
1. Filler words/disfluencies removed (um, uh, er, "you know")
2. Spoken numbers converted to digits (e.g. "three" -> "3")
3. Whitespace collapsed, first letter capitalized
4. Type-specific extraction applied based on the question's expected_answer_type
   (Day 22): numeric extraction for numeric questions, yes/no classification
   for yes_no questions, raw normalized text kept for free_text questions.

## Storage Layer Mapping (per Day 7's storage design)
- Full transcript JSON -> Document DB (nested, variable-length turns array)
- Audio recording file -> Object Storage, referenced by call_id
- Call summary (aggregate stats) -> could be denormalized into Relational DB
  for fast dashboard queries, per Day 7's pattern for ATS scores