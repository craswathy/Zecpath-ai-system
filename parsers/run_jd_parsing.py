import os
import json
from parsers.jd_parser import parse_jd
from utils.logger import logger

DATA_DIR = "data"
OUTPUT_DIR = "data/jd_parsed"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    jd_files = [f for f in os.listdir(DATA_DIR) if f.startswith("jd_") and f.endswith(".txt")]

    logger.info(f"Found {len(jd_files)} JD files to process")

    for filename in jd_files:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        job_id = os.path.splitext(filename)[0]
        jd_profile = parse_jd(text, job_id=job_id)

        output_path = os.path.join(OUTPUT_DIR, f"{job_id}_parsed.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(jd_profile, f, indent=2)

        logger.info(f"Saved parsed JD: {output_path}")

    print(f"Done. Processed {len(jd_files)} job descriptions. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()