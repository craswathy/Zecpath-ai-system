import os
from parsers.resume_reader import extract_resume
from parsers.text_cleaner import clean_text
from utils.logger import logger

DATA_DIR = "data"
OUTPUT_DIR = "data/extracted"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    resume_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith((".pdf", ".docx"))]

    logger.info(f"Found {len(resume_files)} resume files to process")

    for filename in resume_files:
        file_path = os.path.join(DATA_DIR, filename)
        raw_text = extract_resume(file_path)
        cleaned = clean_text(raw_text)

        output_name = os.path.splitext(filename)[0] + "_extracted.txt"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        logger.info(f"Saved cleaned text: {output_path}")

    print(f"Done. Processed {len(resume_files)} resumes. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()