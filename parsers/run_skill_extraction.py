import os
import json
from parsers.skill_extractor import extract_skills
from utils.logger import logger

INPUT_DIR = "data/extracted"
OUTPUT_DIR = "data/skills_extracted"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    logger.info(f"Found {len(files)} resumes for skill extraction")

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        skills = extract_skills(text)

        output_name = filename.replace("_extracted.txt", "_skills.json")
        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=2)

        logger.info(f"Saved skills: {output_path}")

    print(f"Done. Extracted skills from {len(files)} resumes. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()