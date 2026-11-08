import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from ats_engine.ats_scorer import compute_ats_score
from utils.logger import logger

TOTAL_REQUESTS = 200
LEVELS = [1, 10, 50]

CANDIDATE = {
    "skills": [{"skill": "python", "confidence": 1.0}],
    "experience_summary": {"experience_entries": [{"relevance_score": 0.8}]},
    "education_relevance": {"relevance_score": 0.9},
    "semantic_match": {"overall_similarity": 0.7},
}
JD = {"required_skills": [{"name": "python", "mandatory": True}]}


def cpu_request():
    start = time.perf_counter()
    compute_ats_score(CANDIDATE, JD, "technical")
    return time.perf_counter() - start


def io_request():
    # Simulates a 50 ms database or network wait around the same scoring call
    start = time.perf_counter()
    time.sleep(0.05)
    compute_ats_score(CANDIDATE, JD, "technical")
    return time.perf_counter() - start


def run_level(request_fn, concurrency):
    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        latencies = sorted(pool.map(lambda _: request_fn(), range(TOTAL_REQUESTS)))
    wall = time.perf_counter() - wall_start
    return {
        "concurrency": concurrency,
        "requests_per_second": round(TOTAL_REQUESTS / wall, 1),
        "p50_ms": round(latencies[len(latencies) // 2] * 1000, 2),
        "p95_ms": round(latencies[int(len(latencies) * 0.95) - 1] * 1000, 2),
    }


def run():
    logger.setLevel(logging.WARNING)
    results = {
        "total_requests_per_level": TOTAL_REQUESTS,
        "note": "Function-level simulation inside one process, not real HTTP traffic.",
        "cpu_bound_scoring": [run_level(cpu_request, c) for c in LEVELS],
        "io_bound_simulated_50ms_wait": [run_level(io_request, c) for c in LEVELS],
    }
    with open("data/load_test_day60.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()