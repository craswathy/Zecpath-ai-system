import os
import json
from parsers.education_parser import extract_education_entries, extract_certifications
from parsers.education_relevance import score_education_relevance
from utils.logger import logger

INPUT_DIR = "data/labeled_sections"
OUTPUT_DIR = "data/education_parsed"

SAMPLE_REQUIRED_DEGREE = "Master's"
SAMPLE_REQUIRED_FIELD = "statistics"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    logger.info(f"Found {len(files)} labeled resumes for education parsing")

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            sections = json.load(f)

        education_text = " ".join(sections.get("EDUCATION", []))
        cert_text = " ".join(sections.get("CERTIFICATIONS", []))

        education_entries = extract_education_entries(education_text)
        certifications = extract_certifications(cert_text) if cert_text else []
        relevance = score_education_relevance(education_entries, SAMPLE_REQUIRED_DEGREE, SAMPLE_REQUIRED_FIELD)

        academic_profile = {
            "candidate_file": filename,
            "education": education_entries,
            "certifications": certifications,
            "education_relevance": relevance,
        }

        output_name = filename.replace("_labeled.json", "_academic.json")
        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(academic_profile, f, indent=2)

        logger.info(f"Saved academic profile: {output_path}")

    print(f"Done. Parsed education for {len(files)} resumes. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()