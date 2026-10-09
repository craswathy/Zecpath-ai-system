import json
import os
from ats_engine.unified_candidate_object import build_unified_candidate_object


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    os.makedirs("data/unified_candidate_objects", exist_ok=True)

    ranked = load_json("data/rankings/ranked_candidates.json")
    screening = load_json("data/screening_score_result.json")
    hr = load_json("data/hr_score_reports/cand_00123_hr_score.json")

    objects = []

    # Demo 1: top ATS candidate + demo screening + demo HR (all 3 rounds)
    if ranked:
        top = ranked[0]
        objects.append(build_unified_candidate_object(
            candidate_id=top["candidate"], job_id="jd_data_analyst",
            ats_result=top, screening_result=screening, hr_result=hr,
            role_category="technical",
        ))

    # Demo 2: second ATS candidate with no screening/HR yet (partial)
    if ranked and len(ranked) > 1:
        second = ranked[1]
        objects.append(build_unified_candidate_object(
            candidate_id=second["candidate"], job_id="jd_data_analyst",
            ats_result=second, role_category="technical",
        ))

    for obj in objects:
        path = f"data/unified_candidate_objects/{obj['candidate_id']}_unified.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    print(f"Done. Built {len(objects)} unified candidate objects.")
    for o in objects:
        print(f"  {o['candidate_id']}: {o['hiring_fit']['percentage']}% -> "
              f"{o['hiring_fit']['category']} (status: {o['metadata']['status']})")
    print("Check data/unified_candidate_objects/")


if __name__ == "__main__":
    run()