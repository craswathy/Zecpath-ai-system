import json
import os

LOG_DIR = "data/observability"

# Alert rules: name, metric, comparison, threshold, severity
ALERT_RULES = [
    {"name": "High p95 latency", "metric": "p95_ms", "op": ">", "threshold": 2000, "severity": "warning"},
    {"name": "High failure rate", "metric": "failure_rate_pct", "op": ">", "threshold": 5, "severity": "critical"},
    {"name": "Score drift", "metric": "mean_score_shift", "op": ">", "threshold": 10, "severity": "warning"},
]


def read_jsonl(name):
    path = os.path.join(LOG_DIR, name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def compute_metrics(baseline_mean_score=None):
    api = read_jsonl("api_log.jsonl")
    models = read_jsonl("model_output_log.jsonl")
    decisions = read_jsonl("decision_audit_log.jsonl")

    durations = sorted(r["duration_ms"] for r in api)
    failures = [r for r in api if r["status_code"] >= 400]
    metrics = {
        "total_requests": len(api),
        "p50_ms": durations[len(durations) // 2] if durations else 0,
        "p95_ms": durations[max(int(len(durations) * 0.95) - 1, 0)] if durations else 0,
        "failure_rate_pct": round(100 * len(failures) / len(api), 1) if api else 0,
        "decision_counts": {},
    }
    for d in decisions:
        metrics["decision_counts"][d["decision"]] = metrics["decision_counts"].get(d["decision"], 0) + 1
    if models and baseline_mean_score is not None:
        mean_score = sum(m["score"] for m in models) / len(models)
        metrics["mean_score_shift"] = round(abs(mean_score - baseline_mean_score), 1)
    return metrics


def evaluate_alerts(metrics):
    fired = []
    for rule in ALERT_RULES:
        value = metrics.get(rule["metric"])
        if value is None:
            continue
        if rule["op"] == ">" and value > rule["threshold"]:
            fired.append({**rule, "value": value})
    return fired


if __name__ == "__main__":
    m = compute_metrics(baseline_mean_score=60.0)
    print(json.dumps(m, indent=2))
    alerts = evaluate_alerts(m)
    print("ALERTS:", json.dumps(alerts, indent=2) if alerts else "none")