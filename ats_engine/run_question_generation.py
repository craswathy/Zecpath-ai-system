import os
import json
from ats_engine.conversation_question_builder import build_conversation_questions
from utils.logger import logger

JD_DIR = "data/jd_parsed"
OUTPUT_DIR = "data/screening_questions"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".json")]

    logger.info(f"Generating screening questions for {len(jd_files)} job postings")

    for filename in jd_files:
        with open(os.path.join(JD_DIR, filename), "r", encoding="utf-8") as f:
            job_data = json.load(f)

        role_type = "technical" if filename in (
            "jd_data_scientist_parsed.json", "jd_data_analyst_parsed.json",
            "jd_software_engineer_parsed.json"
        ) else "all"

        questions = build_conversation_questions(job_data, role_type=role_type)

        output_name = filename.replace("_parsed.json", "_questions.json")
        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2)

    print(f"Done. Generated question sets for {len(jd_files)} jobs. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()