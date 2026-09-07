import re
from utils.logger import logger

# Each intent has trigger patterns -- words/phrases that signal that
# kind of content is present in the answer, regardless of which
# question was asked (used to detect off-topic/mismatched responses).

INTENT_PATTERNS = {
    "skills_mention": [r"\bpython\b", r"\bsql\b", r"\bexcel\b", r"\bexperience with\b", r"\bskilled in\b", r"\bworked with\b"],
    "experience_mention": [r"\byears?\b", r"\bmonths?\b", r"\bcurrently work\b", r"\bpreviously\b", r"\bmy role\b"],
    "availability_mention": [r"\bnotice period\b", r"\bavailable\b", r"\bjoin\b", r"\bimmediately\b", r"\brelocat\w*\b"],
    "salary_mention": [r"\bctc\b", r"\bsalary\b", r"\blakh\w*\b", r"\bexpected\b.*\bpay\b", r"\bcompensation\b"],
    "education_mention": [r"\bdegree\b", r"\bgraduat\w*\b", r"\buniversity\b", r"\bcollege\b", r"\bbachelor\b", r"\bmaster\b"],
    "refusal_or_unclear": [r"\bi don'?t know\b", r"\bnot sure\b", r"\bcan you repeat\b", r"\bwhat do you mean\b"],
}

EXPECTED_INTENT_BY_CATEGORY = {
    "Skills": "skills_mention",
    "Experience": "experience_mention",
    "Location": "availability_mention",
    "Notice Period": "availability_mention",
    "Salary": "salary_mention",
    "Education": "education_mention",
}


def classify_intent(answer_text):
    """
    Detect which intent(s) are present in a candidate's answer.
    Returns a list of matched intents (an answer can match multiple,
    e.g. mentioning both skills and experience in one response).
    """
    text_lower = answer_text.lower()
    matched_intents = []

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matched_intents.append(intent)
                break

    return matched_intents if matched_intents else ["unclassified"]


def is_off_topic(answer_text, question_category):
    """
    Check if the detected intent(s) in the answer match what the question
    category expected. Returns True if the answer seems off-topic.
    """
    expected_intent = EXPECTED_INTENT_BY_CATEGORY.get(question_category)
    if not expected_intent:
        return False  # no strict expectation for this category (e.g. Introduction)

    matched_intents = classify_intent(answer_text)

    if "refusal_or_unclear" in matched_intents:
        return False  # this is flagged separately as vague/missing, not off-topic

    is_on_topic = expected_intent in matched_intents
    if not is_on_topic:
        logger.info(f"Off-topic answer detected for category '{question_category}': {matched_intents}")
    return not is_on_topic