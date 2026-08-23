import time
import os
import json
from parsers.resume_reader import extract_resume
from parsers.text_cleaner import clean_text
from parsers.semantic_matcher import semantic_similarity, get_model
from utils.logger import logger

DATA_DIR = "data"


def time_it(label, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    logger.info(f"[BENCHMARK] {label}: {elapsed:.3f}s")
    return result, elapsed


def benchmark_extraction():
    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith((".pdf", ".docx"))]
    total_time = 0
    for f in files:
        _, elapsed = time_it(f"extract {f}", extract_resume, os.path.join(DATA_DIR, f))
        total_time += elapsed
    avg = total_time / len(files) if files else 0
    print(f"Extraction: {len(files)} files, total {total_time:.2f}s, avg {avg:.3f}s/file")
    return {"total_files": len(files), "total_time": round(total_time, 2), "avg_time": round(avg, 3)}


def benchmark_semantic_model():
    # first call includes model-loading time -- measure separately from actual inference
    _, load_time = time_it("model load (first call)", get_model)
    _, infer_time = time_it("single similarity comparison", semantic_similarity, "Python SQL machine learning", "Data analyst role requiring Python and SQL")
    print(f"Model load: {load_time:.2f}s (one-time cost) | Inference: {infer_time:.3f}s (per comparison)")
    return {"model_load_time": round(load_time, 2), "inference_time": round(infer_time, 3)}


def run():
    print("=== Zecpath ATS Performance Benchmark ===\n")
    extraction_stats = benchmark_extraction()
    print()
    semantic_stats = benchmark_semantic_model()

    report = {"extraction": extraction_stats, "semantic_model": semantic_stats}
    with open("data/performance_baseline.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\nBaseline saved to data/performance_baseline.json")

if __name__ == "__main__":
    run()