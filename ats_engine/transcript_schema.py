# Voice Transcript Schema -- Zecpath
# Defines the structure for one screening call's full transcript, built on
# top of Day 22's question bank and Day 7's metadata standard.

TRANSCRIPT_SCHEMA = {
    "call_id": "string",
    "candidate_id": "string",
    "job_id": "string",
    "call_metadata": {
        "start_timestamp": "string (ISO 8601)",
        "end_timestamp": "string (ISO 8601)",
        "duration_seconds": "number",
        "language": "string (e.g. en, ml, hi, ta)",
        "voice_profile": "string (e.g. male_en, female_ml)",
        "call_status": "string (completed | dropped | no_answer | retried)",
    },
    "turns": [
        {
            "turn_id": "string",
            "question_id": "string (references hr_question_bank.py, Day 22)",
            "question_category": "string",
            "question_text_spoken": "string (the exact text-to-speech output)",
            "candidate_response_raw": "string (raw speech-to-text output)",
            "candidate_response_normalized": "string (cleaned/normalized, see normalization rules)",
            "response_confidence": "number (0-1, speech-to-text engine confidence)",
            "timestamp": "string (ISO 8601)",
            "response_duration_seconds": "number",
        }
    ],
    "call_summary": {
        "questions_asked": "number",
        "mandatory_questions_answered": "number",
        "mandatory_questions_total": "number",
        "average_response_confidence": "number (0-1)",
    },
}


def build_empty_transcript(call_id, candidate_id, job_id):
    """Return a blank transcript object matching the schema, ready to populate."""
    return {
        "call_id": call_id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "call_metadata": {
            "start_timestamp": None,
            "end_timestamp": None,
            "duration_seconds": None,
            "language": "en",
            "voice_profile": None,
            "call_status": "pending",
        },
        "turns": [],
        "call_summary": {
            "questions_asked": 0,
            "mandatory_questions_answered": 0,
            "mandatory_questions_total": 0,
            "average_response_confidence": None,
        },
    }