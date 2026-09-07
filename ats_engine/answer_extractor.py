import re
from utils.logger import logger

VAGUE_ANSWER_PATTERNS = [
    r"^\s*maybe\s*$", r"^\s*i (guess|think) so\s*$", r"^\s*not really\s*$",
    r"^\s*kind of\s*$", r"^\s*a bit\s*$",
]

MIN_WORDS_FOR_SUBSTANTIVE_ANSWER = 3


def extract_skills_mentioned(answer_text, known_skills_list):
    """Check which known skills (from Day 9's dictionary) appear in this answer."""
    text_lower = answer_text.lower()
    return [skill for skill in known_skills_list if skill.lower() in text_lower]


def extract_experience_years(answer_text):
    """Pull a numeric years-of-experience value from a spoken answer."""
    match = re.search(r"(\d+(\.\d+)?)\s*(years?|yrs?)", answer_text.lower())
    return float(match.group(1)) if match else None


def extract_availability(answer_text):
    """Classify availability response into a simple category."""
    text_lower = answer_text.lower()
    if any(w in text_lower for w in ["immediately", "right away", "asap"]):
        return "immediate"
    match = re.search(r"(\d+)\s*(days?|weeks?|months?)", text_lower)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return "unspecified"


def extract_salary_expectation(answer_text):
    """Pull a numeric salary figure (in lakhs, common in Indian context) from an answer."""
    match = re.search(r"(\d+(\.\d+)?)\s*(lakh|lpa|l\b)", answer_text.lower())
    return float(match.group(1)) if match else None


def is_vague_or_missing(answer_text):
    """Detect vague, non-committal, or too-short answers that need follow-up."""
    if not answer_text or not answer_text.strip():
        return True
    text_stripped = answer_text.strip()
    for pattern in VAGUE_ANSWER_PATTERNS:
        if re.match(pattern, text_stripped, re.IGNORECASE):
            return True
    word_count = len(text_stripped.split())
    return word_count < MIN_WORDS_FOR_SUBSTANTIVE_ANSWER


def build_structured_answer(question_category, answer_text, known_skills_list=None):
    """
    Convert a raw normalized answer (Day 23/24 output) into a structured
    semantic object, extracting the relevant field based on question type.
    """
    structured = {
        "category": question_category,
        "raw_answer": answer_text,
        "is_vague_or_missing": is_vague_or_missing(answer_text),
        "extracted_value": None,
        "extraction_type": None,
    }

    if is_vague_or_missing(answer_text):
        logger.info(f"Vague or missing answer detected for category '{question_category}'")
        return structured

    if question_category == "Skills":
        structured["extracted_value"] = extract_skills_mentioned(answer_text, known_skills_list or [])
        structured["extraction_type"] = "skill_list"
    elif question_category == "Experience":
        structured["extracted_value"] = extract_experience_years(answer_text)
        structured["extraction_type"] = "years_numeric"
    elif question_category in ("Location", "Notice Period"):
        structured["extracted_value"] = extract_availability(answer_text)
        structured["extraction_type"] = "availability_category"
    elif question_category == "Salary":
        structured["extracted_value"] = extract_salary_expectation(answer_text)
        structured["extraction_type"] = "salary_lakhs"
    else:
        structured["extracted_value"] = answer_text
        structured["extraction_type"] = "free_text"

    return structured