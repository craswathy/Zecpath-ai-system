# Fallback/clarifying questions used when the state machine (Day 29)
# detects silence, off-topic answers, or vague responses (Day 25 detection).

FALLBACK_QUESTIONS = {
    "silence": "Sorry, I didn't catch that. Could you please repeat your answer?",
    "off_topic": "I want to make sure I understand correctly -- could you tell me specifically about {category_topic}?",
    "vague_answer": "Could you give me a bit more detail on that, please?",
    "low_confidence_transcription": "I'm having trouble hearing you clearly -- could you say that again?",
}

CATEGORY_TOPIC_HINTS = {
    "Skills": "the specific tools or technologies you've worked with",
    "Experience": "how many years of relevant experience you have",
    "Location": "your current location or willingness to relocate",
    "Salary": "your salary expectations",
    "Notice Period": "your notice period or availability to join",
    "Education": "your highest qualification",
}


def get_fallback_question(reason, question_category=None):
    """Return the appropriate fallback/clarifying question text for a given failure reason."""
    template = FALLBACK_QUESTIONS.get(reason, "Could you please clarify your answer?")
    if "{category_topic}" in template:
        topic = CATEGORY_TOPIC_HINTS.get(question_category, "that topic")
        return template.format(category_topic=topic)
    return template


def get_polite_closing_message(reason="normal_completion"):
    """Return an appropriate closing message based on how the call ended."""
    messages = {
        "normal_completion": "Thank you for your time today. Our team will review your responses and get back to you soon.",
        "max_retries_exceeded": "Thank you for your patience. We'll follow up with you via email regarding next steps.",
        "call_dropped": "It seems we lost connection. Someone from our team will reach out to reschedule.",
    }
    return messages.get(reason, messages["normal_completion"])