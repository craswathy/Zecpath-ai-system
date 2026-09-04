import re
from utils.logger import logger

# Common speech-to-text disfluencies and filler words to clean out
FILLER_WORDS = [
    r"\bum+\b", r"\buh+\b", r"\ber+\b", r"\blike\b(?=\s+I\s)", r"\byou know\b",
]

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
}


def normalize_transcript_text(raw_text):
    """
    Clean raw speech-to-text output: remove filler words/disfluencies,
    normalize spoken numbers to digits, collapse whitespace.
    Mirrors Day 5's text_cleaner.py approach, adapted for spoken transcripts.
    """
    if not raw_text:
        return ""

    text = raw_text.strip()

    for filler_pattern in FILLER_WORDS:
        text = re.sub(filler_pattern, "", text, flags=re.IGNORECASE)

    for word, digit in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()
    text = text[0].upper() + text[1:] if text else text

    logger.info("Normalized transcript text")
    return text


def extract_numeric_answer(normalized_text):
    """
    Pull the first numeric value from a normalized response -- used for
    questions with expected_answer_type = 'numeric' (Day 22 question bank),
    e.g. 'I have about 3 years of experience' -> 3
    """
    match = re.search(r"\d+(\.\d+)?", normalized_text)
    return float(match.group()) if match else None


def extract_yes_no_answer(normalized_text):
    """Classify a response as yes/no/unclear for yes_no type questions."""
    text_lower = normalized_text.lower()
    if any(word in text_lower for word in ["yes", "yeah", "sure", "definitely", "of course"]):
        return "yes"
    elif any(word in text_lower for word in ["no", "not really", "unfortunately not"]):
        return "no"
    return "unclear"