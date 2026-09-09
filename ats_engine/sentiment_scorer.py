from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.logger import logger

_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def score_sentiment(answer_text):
    """
    Score the sentiment of a candidate's answer using VADER, which returns
    a compound score from -1 (very negative) to +1 (very positive).
    """
    if not answer_text or not answer_text.strip():
        return {"compound": 0.0, "label": "neutral"}

    analyzer = get_analyzer()
    scores = analyzer.polarity_scores(answer_text)
    compound = scores["compound"]

    if compound >= 0.3:
        label = "positive"
    elif compound <= -0.3:
        label = "negative"
    else:
        label = "neutral"

    logger.info(f"Sentiment: {label} (compound={compound})")

    return {
        "compound": round(compound, 3),
        "positive": round(scores["pos"], 3),
        "neutral": round(scores["neu"], 3),
        "negative": round(scores["neg"], 3),
        "label": label,
    }