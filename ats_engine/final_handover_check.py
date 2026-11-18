import json
import os
import re
import subprocess
import sys

FINAL_DOCS = ["README.md", "DOCUMENTATION_INDEX.md", "AI_ROADMAP.md",
              "INTERNSHIP_PORTFOLIO.md", "FINAL_INTERNSHIP_REPORT.md"]
HANDOVER_DOCS = ["KNOWLEDGE_TRANSFER_GUIDE.md", "KT_COMPLETION_RECORD.md",
                 "FINAL_DEMO_RUNBOOK_DAY70.md", "INTERNSHIP_EVALUATION_PREP.md"]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout + p.stderr, p.returncode


def module_count(module, pattern):
    out, _ = run([sys.executable, "-m", module])
    match = re.search(pattern, out)
    return int(match.group(1)) if match else None


def main():
    checks = []

    missing = [d for d in FINAL_DOCS + HANDOVER_DOCS if not os.path.exists(d)]
    checks.append(("All final and handover documents exist", not missing, f"missing: {missing}" if missing else "ok"))

    unfilled = {}
    for d in FINAL_DOCS:
        if os.path.exists(d):
            with open(d, "r", encoding="utf-8") as f:
                n = f.read().count("[ ]")
            if n:
                unfilled[d] = n
    checks.append(("No unfilled [ ] in final documents", not unfilled, str(unfilled) if unfilled else "ok"))

    out, code = run([sys.executable, "-m", "pytest", "tests", "-q"])
    last = [l for l in out.strip().splitlines() if l.strip()]
    checks.append(("All automated tests pass", code == 0, last[-1] if last else "no output"))

    problems = module_count("ats_engine.release_validator", r"TOTAL PROBLEMS: (\d+)")
    checks.append(("Release validator reports no problems", problems == 0, f"problems: {problems}"))

    failures = module_count("ats_engine.edge_case_probe", r"FAILURES: (\d+)")
    checks.append(("Edge-case probe reports no failures", failures == 0, f"failures: {failures}"))

    try:
        status, _ = run(["git", "status", "--porcelain"])
        log, _ = run(["git", "log", "-1", "--oneline"])
        checks.append(("Everything is committed", status.strip() == "",
                       "clean" if status.strip() == "" else f"{len(status.strip().splitlines())} uncommitted change(s)"))
        print("Last commit:", log.strip())
    except FileNotFoundError:
        checks.append(("Everything is committed", False, "git not found"))

    print()
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<46} {detail}")
    all_ok = all(ok for _, ok, _ in checks)
    print("\nHANDOVER CHECK:", "READY" if all_ok else "NOT READY")

    os.makedirs("data", exist_ok=True)
    with open("data/final_handover_check.json", "w", encoding="utf-8") as f:
        json.dump([{"check": n, "passed": ok, "detail": d} for n, ok, d in checks], f, indent=2)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())