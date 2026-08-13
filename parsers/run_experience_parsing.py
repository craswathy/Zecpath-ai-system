import os
import json
from parsers.experience_parser import extract_experience_entries, compute_experience_summary
from parsers.experience_relevance import score_experience_relevance
from utils.logger import logger

INPUT_DIR = "data/extracted"
OUTPUT_DIR = "data/experience_parsed"

# Sample target job title used to demonstrate relevance scoring
SAMPLE_JOB_TITLE = "Data Analyst"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    logger.info(f"Found {len(files)} resumes for experience parsing")

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        entries = extract_experience_entries(text)
        summary = compute_experience_summary(entries)
        scored_entries = score_experience_relevance(entries, SAMPLE_JOB_TITLE)

        structured_experience = {
            "candidate_file": filename,
            "experience_entries": scored_entries,
            "total_experience_years": summary["total_experience_years"],
            "gaps": summary["gaps"],
            "overlaps": summary["overlaps"],
            "scored_against_job_title": SAMPLE_JOB_TITLE,
        }

        output_name = filename.replace("_extracted.txt", "_experience.json")
        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(structured_experience, f, indent=2)

        logger.info(f"Saved experience object: {output_path}")

    print(f"Done. Parsed experience for {len(files)} resumes. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()