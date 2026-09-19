from ats_engine.fluency_analyzer import count_filler_words, measure_sentence_continuity, measure_answer_structure
from ats_engine.grammar_vocabulary_analyzer import check_grammar_quality, measure_vocabulary_range
from utils.logger import logger

# Weights sum to 1.0 -- each component contributes to the final 0-100 score
COMMUNICATION_WEIGHTS = {
    "fluency": 0.30,
    "grammar": 0.25,
    "vocabulary": 0.20,
    "clarity": 0.25,
}


def score_clarity(structure_result, filler_count, word_count):
    """
    Clarity combines structural completeness with filler-word density --
    a rambling, filler-heavy answer is less clear even if grammatically fine.
    """
    structure_score = 1.0 if structure_result["has_structure"] else 0.5
    filler_density = filler_count / word_count if word_count else 0
    filler_penalty = min(0.4, filler_density * 2)
    return round(max(0.0, structure_score - filler_penalty), 2)


def score_communication(raw_text, normalized_text):
    """
    Combine fluency, grammar, vocabulary, and clarity into one explainable
    0-100 communication score. Uses RAW text for filler detection (before
    Day 23's cleanup removes those signals) and normalized text for
    grammar/vocabulary analysis (cleaner input for those checks).
    """
    if not raw_text or not raw_text.strip():
        return {
            "communication_score": 0.0,
            "component_scores": {},
            "explanation": "No response captured.",
        }

    word_count = len(raw_text.split())
    filler_count = count_filler_words(raw_text)
    continuity = measure_sentence_continuity(normalized_text)
    structure = measure_answer_structure(normalized_text)
    grammar_result = check_grammar_quality(normalized_text)
    vocab_result = measure_vocabulary_range(normalized_text)
    clarity = score_clarity(structure, filler_count, word_count)

    fluency_score = round((continuity * 0.7) + (max(0, 1 - filler_count * 0.1) * 0.3), 2)

    component_scores = {
        "fluency": fluency_score,
        "grammar": grammar_result["grammar_score"],
        "vocabulary": vocab_result["vocabulary_score"],
        "clarity": clarity,
    }

    final_score = sum(
        component_scores[k] * COMMUNICATION_WEIGHTS[k] for k in COMMUNICATION_WEIGHTS
    )
    final_score = round(final_score * 100, 1)

    explanation = " | ".join(
        f"{k.title()}: {v} (weight {COMMUNICATION_WEIGHTS[k]})" for k, v in component_scores.items()
    )

    logger.info(f"Communication score: {final_score}/100")

    return {
        "communication_score": final_score,
        "component_scores": component_scores,
        "filler_word_count": filler_count,
        "grammar_error_count": grammar_result["error_count"],
        "explanation": explanation,
    }