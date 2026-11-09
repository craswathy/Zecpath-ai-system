import json
from ats_engine.observability import (
    new_request_id, log_api_call, log_model_output, log_error, log_decision, timed_call,
)
from ats_engine.ats_scorer import compute_ats_score
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit

CANDIDATE = {
    "skills": [{"skill": "python", "confidence": 1.0}],
    "experience_summary": {"experience_entries": [{"relevance_score": 0.8}]},
    "education_relevance": {"relevance_score": 0.9},
    "semantic_match": {"overall_similarity": 0.7},
}
JD = {"required_skills": [{"name": "python", "mandatory": True}]}


def run():
    for i in range(1, 6):
        cid = f"demo_cand_{i}"
        rid = new_request_id()
        result, ms = timed_call(compute_ats_score, CANDIDATE, JD, "technical")
        log_api_call(rid, "POST /api/v1/scores", 200, ms, cid, "jd_data_analyst")
        log_model_output(rid, "ats_scorer", "ats_v1.0", result["final_score"], ms, cid)

        unified = compute_unified_score(
            {"ats": result["final_score"], "screening": 70.0, "hr_interview": 35.0 + i * 10},
            "technical")
        fit = classify_hiring_fit(unified)
        log_decision(rid, cid, "jd_data_analyst", fit["fit_category"],
                     fit["hiring_fit_percentage"], "unified_v1.0", fit["flags"])

    # one simulated failure so the error log has a real entry
    rid = new_request_id()
    log_api_call(rid, "POST /api/v1/resumes", 422, 12.0, "demo_cand_9")
    log_error(rid, "POST /api/v1/resumes", "RESUME_PARSE_FAILED",
              "No text layer (scanned PDF)", False, "demo_cand_9")
    print("Done. Check data/observability/")


if __name__ == "__main__":
    run()