import re
from utils.logger import logger

FILLER_WORDS = [
    r"\bum+\b", r"\buh+\b", r"\ber+\b", r"\bhmm+\b", r"\blike\b(?=\s+I\s)",
    r"\byou know\b", r"\bi mean\b", r"\bsort of\b", r"\bkind of\b",
]


def count_filler_words(raw_answer_text):
    """
    Count filler word instances in the RAW transcript (before Day 23's
    normalization strips them) -- same extraction point as Day 27's
    hesitation marker counting, reused here for the communication score.
    """
    text_lower = raw_answer_text.lower()
    count = 0
    for pattern in FILLER_WORDS:
        count += len(re.findall(pattern, text_lower))
    return count


def measure_sentence_continuity(text):
    """
    Fluency proxy: checks how many sentences flow as complete thoughts
    (end with proper punctuation or a clear stopping point) versus
    trailing off or restarting mid-sentence -- a common speech-to-text
    artifact of disfluent speech.
    """
    if not text or not text.strip():
        return 0.0

    # split into rough sentence-like chunks
    chunks = re.split(r'[.!?]+', text)
    chunks = [c.strip() for c in chunks if c.strip()]

    if not chunks:
        return 0.0

    # a chunk under 3 words is likely a fragment/restart, not a complete thought
    complete_chunks = [c for c in chunks if len(c.split()) >= 3]
    continuity_score = len(complete_chunks) / len(chunks)

    return round(continuity_score, 2)


def measure_answer_structure(text):
    """
    Checks whether an answer has a recognizable shape: an opening
    statement, supporting detail, and (ideally) a concluding thought --
    a rough heuristic for structured vs. rambling responses.
    """
    if not text or not text.strip():
        return {"has_structure": False, "sentence_count": 0}

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences)

    # a well-structured answer typically has at least 2 sentences --
    # one stating the point, one supporting/explaining it
    has_structure = sentence_count >= 2

    return {"has_structure": has_structure, "sentence_count": sentence_count}