import sys
sys.path.append(".")
from ats_engine import observability
from ats_engine.monitoring_metrics import evaluate_alerts


def test_forbidden_fields_never_logged(tmp_path, monkeypatch):
    monkeypatch.setattr(observability, "LOG_DIR", str(tmp_path))
    observability._write("t.jsonl", {"request_id": "r1", "email": "a@b.com", "answer_text": "secret"})
    content = (tmp_path / "t.jsonl").read_text()
    assert "a@b.com" not in content and "secret" not in content
    assert "r1" in content


def test_request_ids_are_unique():
    assert observability.new_request_id() != observability.new_request_id()


def test_alert_fires_on_high_failure_rate():
    fired = evaluate_alerts({"failure_rate_pct": 20, "p95_ms": 100})
    assert [a["name"] for a in fired] == ["High failure rate"]


def test_no_alert_when_healthy():
    assert evaluate_alerts({"failure_rate_pct": 1, "p95_ms": 100}) == []