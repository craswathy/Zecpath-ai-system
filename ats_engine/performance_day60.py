import glob
import json
import logging
import os
import time

from parsers.semantic_matcher import get_model, semantic_similarity
from ats_engine.perf_optimizations import (
    clear_cache, embed_texts_cached, similarity_matrix, extract_many,
)
from utils.logger import logger


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, round(time.perf_counter() - start, 3)


def load_texts(pattern):
    texts = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as f:
            texts.append(f.read()[:2000])
    return texts


def run():
    logger.setLevel(logging.WARNING)
    resumes = load_texts("data/extracted/*.txt")
    jds = load_texts("data/jd_*.txt")
    results = {"resumes": len(resumes), "jds": len(jds)}

    # Model load is a one-time cost, measured separately
    _, results["model_load_seconds"] = timed(get_model)

    # 1. Matching: old pairwise way vs batched matrix
    def old_way():
        return [[semantic_similarity(r, j) for j in jds] for r in resumes]

    clear_cache()
    old_scores, results["matching_pairwise_seconds"] = timed(old_way)
    clear_cache()
    new_scores, results["matching_batched_seconds"] = timed(lambda: similarity_matrix(resumes, jds))
    results["matching_max_score_difference"] = round(max(
        abs(a - b) for ro, rn in zip(old_scores, new_scores) for a, b in zip(ro, rn)), 4)

    # 2. Cache: first call vs repeat call on the same texts
    clear_cache()
    _, results["embed_cold_seconds"] = timed(lambda: embed_texts_cached(resumes))
    _, results["embed_cached_seconds"] = timed(lambda: embed_texts_cached(resumes))

    # 3. Resume extraction: sequential vs process pool
    pdfs = sorted(glob.glob("data/*.pdf"))
    results["pdf_count"] = len(pdfs)
    _, results["extract_sequential_seconds"] = timed(lambda: extract_many(pdfs, workers=1))
    _, results["extract_parallel_seconds"] = timed(lambda: extract_many(pdfs, workers=4))

    with open("data/performance_day60.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()