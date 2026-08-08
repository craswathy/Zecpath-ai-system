import re
from utils.logger import logger


def clean_text(raw_text):
    """Normalize and clean raw extracted resume text."""
    if not raw_text:
        return ""

    text = raw_text
    text = re.sub(r"[•●▪◦∙‣]\s+", "- ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\w\s\-.,:@()/&%+]", "", text)

    section_keywords = [
        "experience", "education", "skills", "certifications",
        "summary", "projects", "contact", "objective"
    ]
    for kw in section_keywords:
        pattern = re.compile(rf"^\s*{kw}\s*$", re.IGNORECASE | re.MULTILINE)
        text = pattern.sub(kw.upper(), text)

    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line != "")

    logger.info("Text cleaning complete")
    return text