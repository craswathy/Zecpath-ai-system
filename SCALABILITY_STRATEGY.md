# Scalability Strategy -- Zecpath AI Services (Day 60)

## 1. Starting point
Every AI service is currently a single process. The semantic model loads
once per process, which is a fixed cost. Resume extraction and scoring run
inside the request. There is no queue, load balancer or shared cache yet.

## 2. Bottlenecks (from the Day 60 benchmark)
| Bottleneck | Evidence | Fix |
|---|---|---|
| Re-encoding the same text | Pairwise matching encodes each resume once per JD | Cache plus batched matrix (implemented) |
| Model load time | model_load_seconds in the benchmark | Load once at service start, keep it warm |
| CPU-bound scoring does not scale with threads | Flat requests per second in the load test | Scale with processes and instances |
| Slow work inside the request | Resume parsing and calls take seconds to minutes | Async queue (Day 59 design) |

## 3. Optimizations implemented
- Embedding cache plus batch encoding (ats_engine/perf_optimizations.py).
- Batched similarity matrix replacing per-pair encoding.
- Parallel resume extraction with a process pool. Measure first: for small
  batches the pool start-up cost can outweigh the gain.

## 4. Horizontal scaling plan

### Load balancing
- A load balancer in front of each AI service, round-robin or least-connections.
- Health check endpoint per service. Unhealthy instances leave rotation.
- Services are stateless, so any instance can serve any request.
  State lives in the databases and the queue, not in memory.

### Microservice scaling
Each Day 2 service scales on its own:
| Service | Scales on | Notes |
|---|---|---|
| Resume Parsing | Queue length | Workers pull jobs. CPU-heavy, so one process per core. |
| ATS Scoring | Request rate | Light compute. Many small instances. |
| Screening AI | Concurrent calls | Limited by telephony and speech-to-text capacity. |
| Interview AI | Concurrent interviews | Needs low latency. Keep a warm pool of instances. |
| Decision AI | Request rate | Light compute. Reads stored scores. |

### Queue and workers
- Resume processing and screening calls go through a queue.
- Worker count follows queue depth: add workers when the queue grows,
  remove them when it drains.
- Failed jobs go to a dead-letter queue (Day 59).

### Caching
- In-process embedding cache for the current batch (implemented).
- Shared cache (for example Redis) so all instances reuse embeddings.
  Key by a hash of the text plus model_version, so a model upgrade
  never serves stale vectors.

### Database
- Read replicas for dashboards and analytics.
- Index candidate_id, job_id and stage, the fields used in every query.
- Archive old transcripts and recordings per the retention policy.

## 5. Capacity planning method
1. Measure requests per second per instance (load test).
2. Divide expected peak traffic by that number and add 30 to 50 percent headroom.
3. Repeat on real hardware, because laptop numbers do not transfer.

## 6. Limitations
- The benchmark and load test ran on one laptop, so the absolute numbers do not predict production performance.
- The load test is a function-level simulation, not real HTTP traffic through a gateway.
- No real queue, load balancer or shared cache has been deployed. This document is a plan.
- The strategy should be validated with a real load tool such as Locust or k6 against deployed services.