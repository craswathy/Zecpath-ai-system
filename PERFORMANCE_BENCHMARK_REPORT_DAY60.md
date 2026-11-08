# Performance Benchmarking Report -- Day 60

## Method
ats_engine/performance_day60.py and ats_engine/run_load_test.py on one laptop.  
Inputs: 10 resumes, 6 job descriptions, 10 PDF files.  
Model load time (one-time cost): 5.961 seconds.

## Results

| Test | Before | After | Change |
|---|---|---|---|
| Resume-vs-JD matching (all pairs) | 4.345 s pairwise | 0.519 s batched | 88.06% faster (8.37x speedup) |
| Embedding the same texts again | 0.306 s first call | 0.0 s cached | 100% faster (Instant lookup) |
| Extraction of 10 PDFs | 2.104 s sequential | 9.756 s parallel | 363.69% slower (Process overhead) |

Score difference between old and new matching: 0.0005 (should be near 0).

## Simulated load (200 requests per level)

| Workload | Concurrency | Requests/sec | p50 ms | p95 ms |
|---|---|---|---|---|
| CPU-bound scoring | 1 | 35811.5 | 0.01 | 0.02 |
| CPU-bound scoring | 10 | 22882.0 | 0.02 | 0.03 |
| CPU-bound scoring | 50 | 21378.7 | 0.01 | 0.03 |
| Simulated I/O-bound | 1 | 19.7 | 50.73 | 51.33 |
| Simulated I/O-bound | 10 | 195.7 | 50.73 | 51.58 |
| Simulated I/O-bound | 50 | 853.8 | 50.67 | 51.15 |

## Findings
- **Batching & Caching Efficiency:** Vector batching significantly optimized matrix operations, reducing matching time from 4.345s to 0.519s (~8.37x speedup) while maintaining near-zero score deviation (0.0005). Embedding caching eliminated redundant model encodings completely (0.0s lookup).
- **Process Pool Impact on Small Batches:** Parallel PDF extraction (9.756s) performed worse than sequential extraction (2.104s) for a small dataset of 10 PDFs due to process pool spawn overhead under Windows. Sequential parsing is faster for small batches, while process pooling should be reserved for high-volume batch processing.
- **Concurrency & Scaling Behavior:** For CPU-bound scoring, throughput decreased/plateaued as concurrency increased (from ~35.8k req/sec at concurrency 1 to ~21.3k req/sec at concurrency 50) due to Python GIL restrictions in a single-process thread pool. Conversely, I/O-bound throughput scaled near-linearly with concurrency (from 19.7 to 853.8 req/sec). This indicates that scaling CPU-heavy scoring requires multi-process instance scaling (horizontal pod autoscaling), whereas I/O-bound pipeline steps can effectively scale using async/threading.

## Limitations
- One laptop, small data (10 resumes), so results indicate direction, not production capacity.
- The load test is function-level inside one process, not real HTTP traffic.
- The 50 ms wait in the I/O-bound test is a simulated value.
- Single runs, with no repeats or averages.