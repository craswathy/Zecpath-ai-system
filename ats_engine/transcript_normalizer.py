import re
from utils.logger import logger

# One combined pattern: a single pass over the text instead of one pass per filler
FILLER_PATTERN = re.compile(
    r"\b(?:um+|uh+|er+|hmm+|you know)\b|\blike\b(?=\s+I\s)",
    re.IGNORECASE,
)

# Repeated word, e.g. "I I I have" -> "I have"
STUTTER_PATTERN = re.compile(r"\b(\w+)(?:\s+\1\b)+", re.IGNORECASE)

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15",
}

# Only convert a number word when a unit follows it, so "one of the projects"
# stays as written but "three years" becomes "3 years"
UNIT_WORDS = r"(?:years?|yrs?|months?|weeks?|days?|lakhs?|lpa|hours?|projects?|people|members|times|percent)"
NUMBER_PATTERN = re.compile(
    r"\b(" + "|".join(NUMBER_WORDS) + r")\b(?=\s+" + UNIT_WORDS + r"\b)",
    re.IGNORECASE,
)

YES_PATTERN = re.compile(r"\b(?:yes|yeah|yep|sure|definitely|of course|absolutely)\b", re.IGNORECASE)
NO_PATTERN = re.compile(r"\b(?:no|nope|not really|not at all|unfortunately not)\b", re.IGNORECASE)
UNSURE_PATTERN = re.compile(r"\b(?:not sure|maybe|i don'?t know|unsure)\b", re.IGNORECASE)


def normalize_transcript_text(raw_text):
    """
    Clean raw speech-to-text output: remove fillers and stutters, fix the
    punctuation they leave behind, convert spoken quantities to digits,
    collapse whitespace.
    """
    if not raw_text:
        return ""

    text = raw_text.strip()
    text = FILLER_PATTERN.sub("", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)          # "word ," -> "word,"
    text = re.sub(r"([,;:])(?:\s*[,;:])+", r"\1", text)   # ",," -> ","
    text = re.sub(r"^[\s,;:.]+", "", text)                # leading junk
    text = STUTTER_PATTERN.sub(r"\1", text)
    text = NUMBER_PATTERN.sub(lambda m: NUMBER_WORDS[m.group(1).lower()], text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text[0].upper() + text[1:] if text else text

    logger.info("Normalized transcript text")
    return text


def extract_numeric_answer(normalized_text):
    """Pull the first numeric value, e.g. 'about 3 years' -> 3."""
    match = re.search(r"\d+(\.\d+)?", normalized_text)
    return float(match.group()) if match else None


def extract_yes_no_answer(normalized_text):
    """
    Classify a response as yes / no / unclear using whole-word matching.
    Checked in order: unsure, no, yes. (Old version used substring checks,
    so "I know" matched "no" and "not sure" matched "sure".)
    """
    if UNSURE_PATTERN.search(normalized_text):
        return "unclear"
    if NO_PATTERN.search(normalized_text):
        return "no"
    if YES_PATTERN.search(normalized_text):
        return "yes"
    return "unclear"