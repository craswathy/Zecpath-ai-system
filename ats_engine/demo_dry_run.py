import json
import subprocess
import sys
import time

from ats_engine.polished_decision_service import safe_decide

STEPS = [
    ("1 Create dataset", [sys.executable, "-m", "ats_engine.create_demo_dataset"]),
    ("2 Run simulation", [sys.executable, "-m", "ats_engine.run_demo_simulation"]),
    ("3 Polished reports", [sys.executable, "-m", "ats_engine.polished_reports"]),
    ("5 Monitoring metrics", [sys.executable, "-m", "ats_engine.monitoring_metrics"]),
]


def run_step(name, cmd):
    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    seconds = round(time.perf_counter() - start, 1)
    tail = (proc.stdout.strip().splitlines() or ["(no output)"])[-1][:70]
    return {"step": name, "seconds": seconds, "ok": proc.returncode == 0, "last_line": tail}


def api_step():
    """Step 4 without a server: the same function the API endpoint calls."""
    start = time.perf_counter()
    good = safe_decide({"round_scores": {"ats": 80, "screening": 70, "hr_interview": 65},
                        "role_category": "technical"})
    bad = safe_decide({"round_scores": {"ats": 250}})
    seconds = round(time.perf_counter() - start, 2)
    ok = "error" not in good and bad["error"]["code"] == "SCORE_OUT_OF_RANGE"
    return {"step": "4 API valid + invalid", "seconds": seconds, "ok": ok,
            "last_line": f"valid -> {good.get('category')}, invalid -> {bad['error']['code']}"}


def run():
    results = [run_step(n, c) for n, c in STEPS]
    results.insert(3, api_step())
    total = round(sum(r["seconds"] for r in results), 1)
    for r in results:
        print(f"{r['step']:<24}{r['seconds']:>7}s  {'OK ' if r['ok'] else 'FAIL'}  {r['last_line']}")
    print(f"\nTotal live-demo run time: {total}s")
    with open("data/demo_dry_run.json", "w", encoding="utf-8") as f:
        json.dump({"total_seconds": total, "steps": results}, f, indent=2)
    return results


if __name__ == "__main__":
    run()