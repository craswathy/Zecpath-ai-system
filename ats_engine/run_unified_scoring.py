import json
import os
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit
from utils.logger import logger

SIMULATED_PROFILES = {
    "balanced_strong": {"ats": 82.0, "screening": 78.0, "hr_interview": 85.0},
    "one_weak_round": {"ats": 90.0, "screening": 85.0, "hr_interview": 35.0},
    "missing_hr_round": {"ats": 80.0, "screening": 75.0, "hr_interview": None},
    "weak_across_rounds": {"ats": 40.0, "screening": 45.0, "hr_interview": 38.0},
    "floor_cap_demo": {"ats": 100.0, "screening": 100.0, "hr_interview": 39.0},
}


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    results = []

    # Real-data demo: top ATS candidate + demo screening + demo HR score
    ranked = load_json("data/rankings/ranked_candidates.json")
    screening = load_json("data/screening_score_result.json")
    hr = load_json("data/hr_score_reports/cand_00123_hr_score.json")

    if ranked and screening and hr:
        top = ranked[0]
        round_scores = {
            "ats": top["final_score"],
            "screening": screening["final_screening_score"]["final_screening_score"],
            "hr_interview": hr["hr_interview_score"],
        }
        unified = compute_unified_score(round_scores, role_category="technical")
        fit = classify_hiring_fit(unified)
        results.append({"profile": f"real_demo ({top['candidate']})", **unified, **fit})

    for name, scores in SIMULATED_PROFILES.items():
        unified = compute_unified_score(scores, role_category="technical")
        fit = classify_hiring_fit(unified)
        results.append({"profile": name, **unified, **fit})

    os.makedirs("data/unified_scores", exist_ok=True)
    with open("data/unified_scores/unified_scores.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Computed hiring-fit for {len(results)} profiles.")
    for r in results:
        print(f"  {r['profile']}: {r['hiring_fit_percentage']}% -> {r['fit_category']}")
    print("Check data/unified_scores/unified_scores.json")


if __name__ == "__main__":
    run()