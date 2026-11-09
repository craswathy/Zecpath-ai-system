# AI Observability Plan -- Zecpath (Day 61)

## 1. Goal
Be able to answer three questions at any time: Is the system up and fast?
Are the AI outputs still good? Why did candidate X get decision Y?

## 2. Key metrics

| Group | Metric | How measured | Source |
|---|---|---|---|
| Response time | p50 and p95 latency per endpoint | duration_ms in api_log | Implemented |
| Failure rate | Percent of requests with status 400 or above, per endpoint | api_log, error_log | Implemented |
| Accuracy | Agreement between AI decision and recruiter's final decision | Recruiter feedback compared with decision audit log | Planned, needs real recruiter data |
| Accuracy | Precision and recall on a periodic labelled review set | Day 17 method, repeated monthly | Planned |
| Model health | Mean score versus baseline (drift) | model_output_log | Implemented |
| Model health | Share of Hold or Review decisions | decision_audit_log | Implemented |
| Quality | Speech-to-text confidence average, silent or dropped call rate | Screening logs | Planned |
| Throughput | Candidates processed per hour, queue depth | Queue metrics | Planned |

Accuracy cannot be measured from logs alone. It needs human-labelled outcomes.

## 3. Alerting rules

| Alert | Condition | Severity | Action |
|---|---|---|---|
| High latency | p95 above 2000 ms for 5 minutes | Warning | Check load, scale out |
| High failure rate | More than 5 percent failed requests over 5 minutes | Critical | Page on-call, check dependencies |
| Score drift | Mean score moves more than 10 points from baseline over a day | Warning | Review inputs and model version |
| Decision mix shift | Share of Rejected changes more than 15 points over a week | Warning | Fairness and calibration review |
| Queue backlog | Resume queue older than 15 minutes | Warning | Add workers |
| Dead-letter growth | More than 10 jobs in 1 hour | Critical | Investigate failing job type |
| Audit log write failure | Any failure | Critical | Stop automated decisions until fixed |

Thresholds are starting values. Tune them after observing real traffic.

## 4. Tools (suggested, not deployed)
- Logs: structured JSON lines shipped to a log store such as ELK or CloudWatch.
- Metrics and dashboards: Prometheus with Grafana, or a cloud equivalent.
- Alert delivery: email or chat for warnings, paging for critical.
- Request tracing: the request_id in every log line links one request across services.

## 5. Privacy rules for logs
- Never log names, emails, phone numbers, resume text, transcripts or answer text.
- Log only ids, scores, durations, versions and flags.
- The logger drops forbidden fields automatically (tested).
- Retention follows the Day 43 policy. Operational logs are kept shorter than audit logs.

## 6. Limitations
- Only the logging module, metrics calculation and alert checker are implemented, and they read local files.
- No log store, Prometheus, Grafana or paging is deployed.
- The demo logs hold 5 simulated candidates plus one simulated failure, so the numbers are examples.
- Accuracy monitoring depends on recruiter feedback that does not exist yet.