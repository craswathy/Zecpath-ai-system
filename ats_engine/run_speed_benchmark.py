import json
import time
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.refined_decision_logic import decide_refined, batch_mode

SAMPLE = {"ats": 82.0, "screening": 78.0, "hr_interview": 94.5, "technical_interview": 81.7, "machine_test": 85.0}
ITERATIONS = 500


def score_one():
    unified = build_unified_score_object("bench", "jd_bench", SAMPLE, "technical", None,
                                         {"integrity_review_priority": "No concern"})
    return decide_refined(unified)


def microseconds_per_candidate(n=ITERATIONS):
    start = time.perf_counter()
    for _ in range(n):
        score_one()
    return round((time.perf_counter() - start) / n * 1_000_000, 1)


def run(label="run"):
    normal = microseconds_per_candidate()      # normal logging: every step writes a log line
    with batch_mode():
        quiet = microseconds_per_candidate()   # batch mode: log lines silenced
    saved = round((1 - quiet / normal) * 100, 1) if normal else 0.0
    result = {"label": label, "iterations": ITERATIONS, "normal_logging_us": normal,
              "batch_mode_us": quiet, "percent_faster": saved}
    with open(f"data/optimization/speed_{label}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Scoring one candidate, normal logging: {normal} microseconds")
    print(f"Scoring one candidate, batch mode:     {quiet} microseconds")
    print(f"Batch mode is {saved}% faster. Saved data/optimization/speed_{label}.json")


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "run")