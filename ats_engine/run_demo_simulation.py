import json
import os

from parsers.text_cleaner import clean_text
from parsers.section_classifier import classify_sections
from parsers.jd_parser import parse_jd
from parsers.skill_extractor import extract_skills
from parsers.experience_parser import extract_experience_entries, compute_experience_summary
from parsers.experience_relevance import score_experience_relevance
from parsers.education_parser import extract_education_entries
from parsers.education_relevance import score_education_relevance
from parsers.semantic_matcher import compare_resume_to_jd
from ats_engine.ats_scorer import compute_ats_score
from ats_engine.transcript_normalizer import normalize_transcript_text
from ats_engine.communication_scorer import score_communication
from ats_engine.confidence_analyzer import compute_confidence_indicator
from ats_engine.answer_extractor import is_vague_or_missing
from ats_engine.intent_classifier import is_off_topic
from ats_engine.hr_interview_scorer import compute_hr_interview_score
from ats_engine.unified_scorer import compute_unified_score
from ats_engine.hiring_fit_calculator import classify_hiring_fit

DIR = "demo_dataset_day63"
OUT = os.path.join(DIR, "simulation_results.json")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def required_degree(jd_text):
    return "Master's" if "Master" in jd_text else "Bachelor's"


def ats_stage(candidate_id, jd_id):
    resume = clean_text(read(os.path.join(DIR, "resumes", f"{candidate_id}.txt")))
    jd_text = read(os.path.join(DIR, "job_descriptions", f"{jd_id}.txt"))
    jd = parse_jd(jd_text, job_id=jd_id)
    sections = classify_sections(resume)

    skills = extract_skills(resume)
    entries = extract_experience_entries(resume)
    exp_summary = None
    if entries:
        scored = score_experience_relevance(entries, jd["title"])
        exp_summary = {"experience_entries": scored}
        total_years = compute_experience_summary(entries)["total_experience_years"]
    else:
        total_years = None
    edu_text = "\n".join(sections.get("EDUCATION", []))
    edu_rel = None
    if edu_text.strip():
        edu_rel = score_education_relevance(extract_education_entries(edu_text),
                                            required_degree(jd_text), "statistics")
    semantic = compare_resume_to_jd(sections, jd)
    result = compute_ats_score(
        {"skills": skills, "experience_summary": exp_summary,
         "education_relevance": edu_rel, "semantic_match": semantic},
        jd, "technical")
    return {"ats_score": result["final_score"], "missing": result["missing_components"],
            "sections_found": sorted(sections.keys()), "years": total_years,
            "skills_found": [s["skill"] for s in skills]}


def hr_stage(responses):
    turns = []
    for r in responses:
        raw = r["answer"]
        normalized = normalize_transcript_text(raw)
        comm = score_communication(raw, normalized)["communication_score"]
        conf = compute_confidence_indicator(raw, len(raw.split()), r["duration"],
                                            r["stt_confidence"])["confidence_score"]
        turns.append({"is_off_topic": is_off_topic(normalized, r["category"]),
                      "is_vague_or_missing": is_vague_or_missing(normalized),
                      "communication_score": comm,
                      "behavioral_confidence_score": round(conf * 100, 1)})
    hr = compute_hr_interview_score(turns, 0, "technical")
    return {"hr_score": hr["hr_interview_score"], "band": hr["performance_band"],
            "weak_components": hr["weak_components"]}


def run():
    with open(os.path.join(DIR, "test_candidate_profiles.json"), "r", encoding="utf-8") as f:
        profiles = json.load(f)
    results = []
    for p in profiles:
        ats = ats_stage(p["candidate_id"], p["job_id"])
        hr = hr_stage(p["responses"])
        unified = compute_unified_score(
            {"ats": ats["ats_score"], "screening": p["simulated_screening_score"],
             "hr_interview": hr["hr_score"]}, "technical")
        fit = classify_hiring_fit(unified)
        results.append({
            "candidate_id": p["candidate_id"], "job_id": p["job_id"], "quality": p["quality"],
            "ats": ats, "screening_score_simulated": p["simulated_screening_score"],
            "hr": hr, "hiring_fit_percentage": fit["hiring_fit_percentage"],
            "category": fit["fit_category"], "flags": fit["flags"],
            "expected": p["expected"], "matches_expected": fit["fit_category"] == p["expected"],
        })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"{'candidate':<12}{'ATS':>6}{'SCR':>6}{'HR':>6}{'FIT%':>7}  {'category':<14}{'expected':<14}match")
    for r in results:
        print(f"{r['candidate_id']:<12}{r['ats']['ats_score']:>6}{r['screening_score_simulated']:>6}"
              f"{r['hr']['hr_score']:>6}{r['hiring_fit_percentage']:>7}  {r['category']:<14}"
              f"{r['expected']:<14}{'yes' if r['matches_expected'] else 'NO'}")
    matched = sum(r["matches_expected"] for r in results)
    print(f"\n{matched}/{len(results)} matched the intended outcome. Full detail: {OUT}")


if __name__ == "__main__":
    run()