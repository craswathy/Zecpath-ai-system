import re
from utils.logger import logger


def check_grammar_quality(text):
    """
    Lightweight rule-based grammar heuristic (no Java dependency needed).
    Checks basic patterns: double spaces, repeated words, lowercase
    standalone "i" instead of "I" -- a simpler substitute for a full
    grammar-checking engine like LanguageTool.
    """
    if not text or not text.strip():
        return {"grammar_score": 0.0, "error_count": 0}

    issues = 0
    issues += len(re.findall(r'\s{2,}', text))  # double spaces
    issues += len(re.findall(r'\b(\w+)\s+\1\b', text.lower()))  # repeated words
    issues += len(re.findall(r'\bi\b', text))  # lowercase "i" instead of "I"

    word_count = len(text.split())
    error_rate = issues / word_count if word_count else 1.0
    grammar_score = round(max(0.0, 1.0 - min(1.0, error_rate * 5)), 2)

    logger.info(f"Grammar check: {issues} issues in {word_count} words, score={grammar_score}")

    return {"grammar_score": grammar_score, "error_count": issues}


def measure_vocabulary_range(text):
    """
    Vocabulary range proxy: ratio of unique words to total words
    (type-token ratio) -- a candidate repeating the same few words
    scores lower than one using varied vocabulary.
    """
    if not text or not text.strip():
        return {"vocabulary_score": 0.0, "unique_word_count": 0, "total_word_count": 0}

    words = [w.lower().strip(".,!?") for w in text.split()]
    words = [w for w in words if w]

    if not words:
        return {"vocabulary_score": 0.0, "unique_word_count": 0, "total_word_count": 0}

    unique_words = set(words)
    ttr = len(unique_words) / len(words)

    # very short answers naturally have high TTR (few repeated words by chance),
    # so this is most meaningful for answers with 10+ words
    vocabulary_score = round(min(1.0, ttr * 1.3), 2)

    return {
        "vocabulary_score": vocabulary_score,
        "unique_word_count": len(unique_words),
        "total_word_count": len(words),
    }