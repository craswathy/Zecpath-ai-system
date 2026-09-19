from utils.logger import logger


def normalize_communication_scores(scores_list):
    """
    Min-max normalize communication scores across a candidate pool,
    same pattern as Day 15's normalize_score_distribution -- prevents
    one unusually strict or lenient scoring run from skewing comparisons.
    """
    if not scores_list:
        return []

    min_s, max_s = min(scores_list), max(scores_list)
    spread = max_s - min_s

    if spread == 0:
        return [50.0 for _ in scores_list]

    return [round((s - min_s) / spread * 100, 1) for s in scores_list]


def apply_grammar_leniency_flag(grammar_error_count, word_count):
    """
    Flag cases where grammar scoring should be interpreted leniently --
    e.g. very short answers naturally show a higher apparent error rate
    per word, which could unfairly penalize concise, correct responses.
    This doesn't change the score, but flags it for human awareness,
    consistent with Day 15's fairness-review-not-auto-decide principle.
    """
    if word_count < 8:
        return True  # too short to reliably assess grammar error rate
    return False