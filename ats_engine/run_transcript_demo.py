import json
from datetime import datetime, timedelta
from ats_engine.transcript_schema import build_empty_transcript
from ats_engine.transcript_normalizer import normalize_transcript_text, extract_numeric_answer
from utils.logger import logger

def build_demo_transcript():
    """
    Build a realistic-looking demo transcript to validate the schema end
    to end -- simulates what a real AI voice call (PRD Phase 5) would produce.
    """
    transcript = build_empty_transcript("call_00001", "cand_00123", "job_00045")

    now = datetime.now()
    transcript["call_metadata"]["start_timestamp"] = now.isoformat()
    transcript["call_metadata"]["language"] = "en"
    transcript["call_metadata"]["voice_profile"] = "female_en"
    transcript["call_metadata"]["call_status"] = "completed"

    demo_turns = [
        ("q_intro_01", "Introduction", "Can you briefly introduce yourself?",
         "uh yeah so I am um a data analyst with three years of experience", 0.89),
        ("q_exp_01", "Experience", "How many years of relevant work experience do you have?",
         "about three years", 0.94),
        ("q_loc_01", "Location", "Are you open to relocating?",
         "yes definitely", 0.97),
    ]

    for i, (qid, category, spoken, raw_response, confidence) in enumerate(demo_turns):
        normalized = normalize_transcript_text(raw_response)
        turn_time = now + timedelta(seconds=i * 30)
        transcript["turns"].append({
            "turn_id": f"turn_{i+1}",
            "question_id": qid,
            "question_category": category,
            "question_text_spoken": spoken,
            "candidate_response_raw": raw_response,
            "candidate_response_normalized": normalized,
            "response_confidence": confidence,
            "timestamp": turn_time.isoformat(),
            "response_duration_seconds": 4.5,
        })

    transcript["call_metadata"]["end_timestamp"] = (now + timedelta(seconds=90)).isoformat()
    transcript["call_metadata"]["duration_seconds"] = 90

    transcript["call_summary"]["questions_asked"] = len(transcript["turns"])
    transcript["call_summary"]["mandatory_questions_answered"] = len(transcript["turns"])
    transcript["call_summary"]["mandatory_questions_total"] = len(transcript["turns"])
    avg_confidence = sum(t["response_confidence"] for t in transcript["turns"]) / len(transcript["turns"])
    transcript["call_summary"]["average_response_confidence"] = round(avg_confidence, 2)

    return transcript


def run():
    transcript = build_demo_transcript()
    output_path = "data/demo_transcript.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2)

    logger.info(f"Demo transcript saved to {output_path}")
    print(f"Done. Demo transcript saved to {output_path}")
    print(f"Sample normalization: 'uh yeah so I am um a data analyst with three years of experience'")
    print(f"  -> '{transcript['turns'][0]['candidate_response_normalized']}'")

if __name__ == "__main__":
    run()