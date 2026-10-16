import json
import os
from datetime import datetime
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.follow_up_state_tracker import FollowUpStateTracker
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from ats_engine.hr_interview_summary_builder import summarize_overall_hr_performance
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit
from utils.logger import logger

DATASET_PATH = "data/demo_dataset/hr_demo_candidates.json"
OUTPUT_DIR = "data/final_demo_results"
MODEL_VERSION = "hr_final_demo_v1.0"
MIN_RELIABLE_TURNS = 4  # same value as the reliability rule in hr_score_normalizer.py


def load_dataset(path=DATASET_PATH):
    """Load the simulated demo candidates."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["candidates"]


def is_vague(clean_text):
    """Answers under 3 words (or empty) count as vague, as in the architecture doc."""
    return len(clean_text.split()) < 3


def make_recommendation(fit_category, reliability):
    """Turn the fit category into a human-readable next step."""
    if reliability != "reliable":
        return "MANUAL REVIEW: too few answers for a reliable score."
    if fit_category == "Strong Fit":
        return "RECOMMEND: move forward to the final manager interview."
    if fit_category == "Moderate Fit":
        return "REVIEW: recruiter should check the weak areas before deciding."
    return "NOT RECOMMENDED on current evidence. A recruiter should confirm before closing."


def run_candidate(c):
    """Run one candidate through the full flow. Returns the results and a printable report."""
    tracker = FollowUpStateTracker()
    transcript = []
    per_turn = []

    for turn in c["turns"]:
        clean = normalize_transcript_text(turn["answer"])
        vague = is_vague(clean)
        decision = tracker.process_answer(
            turn["question_id"], clean, vague, turn.get("follow_up_eligible", True)
        )
        transcript.append({
            "question_text": turn["question_text"],
            "raw_answer": turn["answer"],
            "clean_answer": clean,
            "is_vague": vague,
            "is_off_topic": turn["is_off_topic"],
            "follow_up_action": decision["action"],
            "follow_up_reason": decision["reason"],
            "follow_up_text": decision.get("follow_up_text"),
        })
        per_turn.append({
            "is_off_topic": turn["is_off_topic"],
            "is_vague_or_missing": vague,
            "communication_score": turn.get("communication_score"),
            "behavioral_confidence_score": turn.get("behavioral_confidence_score"),
        })

    hr = compute_hr_interview_score(per_turn, c.get("contradiction_count", 0), c.get("role_category"))
    reliability = "reliable" if len(per_turn) >= MIN_RELIABLE_TURNS else "low_reliability"
    summary = summarize_overall_hr_performance(hr)

    round_scores = {
        "ats": c.get("ats_score"),
        "screening": c.get("screening_score"),
        "hr_interview": hr["hr_interview_score"],
    }
    unified = compute_unified_score(round_scores, role_category=c.get("role_category"))
    fit = classify_hiring_fit(unified)
    recommendation = make_recommendation(fit["fit_category"], reliability)
    follow_ups_asked = sum(1 for t in transcript if t["follow_up_action"] == "ask_follow_up")

    lines = []
    lines.append("=" * 66)
    lines.append(f"CANDIDATE: {c['candidate_id']} | job: {c['job_id']} | {c['seniority']} {c['role_type']}")
    lines.append("=" * 66)
    lines.append("1. INTERVIEW SIMULATION")
    for t in transcript:
        lines.append(f"  Q: {t['question_text']}")
        lines.append(f"  A (raw):   {t['raw_answer']}")
        lines.append(f"  A (clean): {t['clean_answer']}")
        lines.append(f"  Follow-up decision: {t['follow_up_action']} ({t['follow_up_reason']})")
        if t["follow_up_text"]:
            lines.append(f"  Follow-up asked: {t['follow_up_text']}")
        lines.append("")
    lines.append("2. SCORING BREAKDOWN")
    for name, value in hr["component_scores"].items():
        lines.append(f"  {name:<14} {value:<6} x weight {hr['weights_used'][name]}")
    lines.append(f"  HR interview score: {hr['hr_interview_score']}/100 | band: {hr['performance_band']}")
    if hr.get("band_adjusted_from"):
        lines.append(f"  Band adjusted down from {hr['band_adjusted_from']} (weak: {', '.join(hr['weak_components'])})")
    lines.append(f"  Reliability: {reliability} ({len(per_turn)} answers scored)")
    lines.append(f"  Summary: {summary}")
    lines.append("")
    lines.append("3. CROSS-ROUND SCORE")
    lines.append(f"  ATS {round_scores['ats']} | Screening {round_scores['screening']} | HR {round_scores['hr_interview']}")
    lines.append(f"  Weights used: {unified['weights_used']}")
    lines.append(f"  Hiring fit: {fit['hiring_fit_percentage']}% -> {fit['fit_category']}")
    for flag in fit["flags"]:
        lines.append(f"  Flag: {flag}")
    lines.append("")
    lines.append("4. FINAL HIRING RECOMMENDATION")
    lines.append(f"  {recommendation}")
    lines.append("  (Decision support only. The final decision belongs to a human recruiter.)")
    lines.append("")

    record = {
        "candidate_id": c["candidate_id"],
        "job_id": c["job_id"],
        "metadata": {
            "model_version": MODEL_VERSION,
            "timestamp": datetime.now().isoformat(),
            "stage": "final_demo",
            "status": "complete",
        },
        "hr_result": hr,
        "reliability": reliability,
        "unified": unified,
        "hiring_fit": fit,
        "recommendation": recommendation,
    }

    logger.info(f"Final demo for {c['candidate_id']}: {fit['fit_category']}")
    return {
        "hr": hr, "fit": fit, "unified": unified, "reliability": reliability,
        "recommendation": recommendation, "follow_ups_asked": follow_ups_asked,
        "report_lines": lines, "record": record,
    }


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []
    for c in load_dataset():
        result = run_candidate(c)
        for line in result["report_lines"]:
            print(line)
        base = f"{OUTPUT_DIR}/{c['candidate_id']}"
        with open(base + "_report.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(result["report_lines"]))
        with open(base + "_result.json", "w", encoding="utf-8") as f:
            json.dump(result["record"], f, indent=2)
        rows.append((c["candidate_id"], result))

    print("=" * 66)
    print("COMPARISON")
    print("=" * 66)
    print(f"{'Candidate':<22}{'HR':>6}  {'Band':<18}{'Fit %':>6}  {'Category':<14}")
    for name, r in rows:
        print(f"{name:<22}{r['hr']['hr_interview_score']:>6}  {r['hr']['performance_band']:<18}"
              f"{r['fit']['hiring_fit_percentage']:>6}  {r['fit']['fit_category']:<14}")
    print(f"\nSaved reports to {OUTPUT_DIR}/")


if __name__ == "__main__":
    run()