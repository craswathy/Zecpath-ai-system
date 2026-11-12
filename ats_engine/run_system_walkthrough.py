import json
import os
import time

from ats_engine.run_demo_simulation import run as run_simulation

RESULTS = os.path.join("demo_dataset_day63", "simulation_results.json")
OUT = os.path.join("demo_dataset_day63", "walkthrough_findings.json")


def observe(r):
    notes = []
    ats = r["ats"]
    if "EXPERIENCE" not in ats["sections_found"]:
        notes.append("ATS: no EXPERIENCE section detected")
    if "SKILLS" not in ats["sections_found"]:
        notes.append("ATS: no SKILLS section detected")
    if ats["missing"]:
        notes.append("ATS: components missing -> " + ", ".join(ats["missing"]))
    if ats["years"] is None:
        notes.append("ATS: total experience could not be computed")
    notes.append("Screening: score is simulated, not from a real call")
    if r["hr"]["weak_components"]:
        notes.append("HR: weak components -> " + ", ".join(r["hr"]["weak_components"]))
    notes.append("Technical: not part of this simulation")
    if r["flags"]:
        notes.append("Decision flags: " + "; ".join(r["flags"]))
    if not r["matches_expected"]:
        notes.append(f"Decision: got {r['category']}, intended {r['expected']} -> investigate")
    return notes


def run():
    start = time.perf_counter()
    run_simulation()
    seconds = round(time.perf_counter() - start, 1)

    with open(RESULTS, "r", encoding="utf-8") as f:
        results = json.load(f)

    findings = {"total_seconds": seconds, "candidates": []}
    for r in results:
        findings["candidates"].append({
            "candidate_id": r["candidate_id"], "quality": r["quality"],
            "category": r["category"], "expected": r["expected"],
            "observations": observe(r),
        })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    print(f"\nWalkthrough finished in {seconds}s (includes model load)")
    for c in findings["candidates"]:
        print(f"\n{c['candidate_id']} ({c['quality']}): {c['category']}")
        for n in c["observations"]:
            print("   -", n)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    run()