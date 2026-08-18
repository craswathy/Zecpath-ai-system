import os
import json
from ats_engine.ats_scorer import compute_ats_score
from utils.logger import logger

SKILLS_DIR = "data/skills_extracted"
EXPERIENCE_DIR = "data/experience_parsed"
EDUCATION_DIR = "data/education_parsed"
SEMANTIC_FILE = "data/semantic_matches/all_matches.json"
JD_DIR = "data/jd_parsed"
OUTPUT_DIR = "data/ats_scores"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    semantic_matches = load_json(SEMANTIC_FILE) or []
    resume_files = [f for f in os.listdir(SKILLS_DIR) if f.endswith(".json")]

    logger.info(f"Scoring {len(resume_files)} candidates")

    all_scores = []

    for skills_file in resume_files:
        base_name = skills_file.replace("_skills.json", "")

        skills = load_json(os.path.join(SKILLS_DIR, skills_file))
        experience_summary = load_json(os.path.join(EXPERIENCE_DIR, f"{base_name}_experience.json"))
        education_relevance_data = load_json(os.path.join(EDUCATION_DIR, f"{base_name}_labeled_academic.json"))
        education_relevance = education_relevance_data.get("education_relevance") if education_relevance_data else None

        # find this resume's semantic match against the first available JD (demo purposes)
        resume_matches = [m for m in semantic_matches if base_name in m.get("resume", "")]
        semantic_match = resume_matches[0] if resume_matches else None

        jd_files = os.listdir(JD_DIR)
        jd_data = load_json(os.path.join(JD_DIR, jd_files[0])) if jd_files else {}

        candidate_data = {
            "skills": skills,
            "experience_summary": experience_summary,
            "education_relevance": education_relevance,
            "semantic_match": semantic_match,
        }

        result = compute_ats_score(candidate_data, jd_data, role_category="technical")
        result["candidate"] = base_name

        all_scores.append(result)

        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_ats_score.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    summary_path = os.path.join(OUTPUT_DIR, "all_scores_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"candidate": s["candidate"], "final_score": s["final_score"]} for s in all_scores],
            f, indent=2
        )

    print(f"Done. Scored {len(all_scores)} candidates. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()