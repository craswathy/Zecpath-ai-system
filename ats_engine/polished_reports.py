import json
import os

NEXT_ACTION = {
    "Strong Fit": "Move to the next round. A recruiter confirms the decision.",
    "Moderate Fit": "Recruiter review recommended before deciding.",
    "Weak Fit": "Review the reasons before rejecting. The AI result is a recommendation only.",
}


def reasons_for(r):
    """Turn one simulation result into short plain-language sentences."""
    ats, hr = r["ats"], r["hr"]
    out = [f"Resume match score is {ats['ats_score']} out of 100."]
    if "SKILLS" not in ats["sections_found"]:
        out.append("No clear Skills section was found, so the skill score may be understated.")
    if "EXPERIENCE" not in ats["sections_found"]:
        out.append("No Experience section was found, so experience could not be fully assessed.")
    if ats["years"] is not None:
        out.append(f"Calculated experience: {round(ats['years'], 1)} years.")
    if ats["missing"]:
        out.append("Some resume details were missing: " + ", ".join(ats["missing"]) + ". Their weight was shared across the other parts.")
    out.append(f"Screening score is {r['screening_score_simulated']} out of 100.")
    out.append(f"Interview score is {hr['hr_score']} out of 100 ({hr['band']}).")
    if hr["weak_components"]:
        out.append("Weak interview areas: " + ", ".join(hr["weak_components"]) + ".")
    for flag in r["flags"]:
        out.append("Note: " + flag + ".")
    return out


def render(r):
    lines = ["=" * 58, f"CANDIDATE: {r['candidate_id']}   JOB: {r['job_id']}", "=" * 58,
             f"Hiring fit: {r['hiring_fit_percentage']}%  ->  {r['category']}", "",
             "Why:"]
    lines += [f"  - {s}" for s in reasons_for(r)]
    lines += ["", "Suggested next step:", "  " + NEXT_ACTION[r["category"]], "",
              "This is an AI recommendation. A person makes the final decision.", ""]
    return "\n".join(lines)


def run(results_path="demo_dataset_day63/simulation_results.json", out_dir="data/polished_reports"):
    os.makedirs(out_dir, exist_ok=True)
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    ranked = sorted(results, key=lambda r: r["hiring_fit_percentage"], reverse=True)
    summary = ["RANKED CANDIDATES", "-" * 58]
    for i, r in enumerate(ranked, 1):
        with open(os.path.join(out_dir, f"{r['candidate_id']}.txt"), "w", encoding="utf-8") as f:
            f.write(render(r))
        summary.append(f"{i}. {r['candidate_id']:<12} {r['hiring_fit_percentage']:>5}%  {r['category']}")
    with open(os.path.join(out_dir, "ranked_summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary))
    print("\n".join(summary))
    print(f"\nReports saved in {out_dir}/")


if __name__ == "__main__":
    run()