import os
import json
from parsers.semantic_matcher import compare_resume_to_jd
from utils.logger import logger

SECTIONS_DIR = "data/labeled_sections"
JD_DIR = "data/jd_parsed"
OUTPUT_DIR = "data/semantic_matches"

SIMILARITY_THRESHOLD = 0.45  # tuned in Step 5 below

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    resume_files = [f for f in os.listdir(SECTIONS_DIR) if f.endswith(".json")]
    jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".json")]

    logger.info(f"Matching {len(resume_files)} resumes against {len(jd_files)} job descriptions")

    all_results = []

    for resume_file in resume_files:
        with open(os.path.join(SECTIONS_DIR, resume_file), "r", encoding="utf-8") as f:
            resume_sections = json.load(f)

        for jd_file in jd_files:
            with open(os.path.join(JD_DIR, jd_file), "r", encoding="utf-8") as f:
                jd_profile = json.load(f)

            scores = compare_resume_to_jd(resume_sections, jd_profile)
            result = {
                "resume": resume_file,
                "job": jd_file,
                "match": scores["overall_similarity"] >= SIMILARITY_THRESHOLD,
                **scores,
            }
            all_results.append(result)

    output_path = os.path.join(OUTPUT_DIR, "all_matches.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"Done. {len(all_results)} resume-JD comparisons saved to {output_path}")

if __name__ == "__main__":
    run()