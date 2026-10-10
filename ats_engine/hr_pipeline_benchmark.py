import sys
import time
import json
import logging
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.follow_up_trigger_detector import classify_follow_up_need
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from utils.logger import logger

SAMPLE_TEXT = ("uh yeah so I am um a data analyst with three years of experience "
               "and I I have worked with python and sql you know")
SAMPLE_TURNS = [
    {"is_off_topic": False, "is_vague_or_missing": False,
     "communication_score": 85, "behavioral_confidence_score": 80}
] * 5
ITERATIONS = 3000


def per_call_microseconds(fn, n=ITERATIONS):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return round((time.perf_counter() - start) / n * 1_000_000, 1)


def run(label):
    # Silence per-call INFO logs so we time computation, not file writes
    logger.setLevel(logging.WARNING)
    results = {
        "label": label,
        "iterations_per_test": ITERATIONS,
        "microseconds_per_call": {
            "normalize_transcript_text": per_call_microseconds(
                lambda: normalize_transcript_text(SAMPLE_TEXT)),
            "classify_follow_up_need": per_call_microseconds(
                lambda: classify_follow_up_need("I like working there", False)),
            "compute_hr_interview_score": per_call_microseconds(
                lambda: compute_hr_interview_score(SAMPLE_TURNS, 0, "technical")),
        },
    }
    path = f"data/hr_performance_{label}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {path}")
    for name, us in results["microseconds_per_call"].items():
        print(f"  {name}: {us} microseconds per call")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "run")