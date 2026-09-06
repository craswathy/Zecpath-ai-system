import whisper
from utils.logger import logger

_model = None

def get_whisper_model():
    """Load Whisper model once, cache it (same pattern as Day 12's embedding model)."""
    global _model
    if _model is None:
        logger.info("Loading Whisper model (first call only)...")
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(file_path):
    """
    Convert an audio file into raw text using Whisper STT.
    Returns the transcribed text and a confidence estimate.
    """
    model = get_whisper_model()
    try:
        result = model.transcribe(file_path)
        text = result.get("text", "").strip()

        # Whisper doesn't give a single confidence score directly;
        # approximate using average segment-level log probability
        segments = result.get("segments", [])
        if segments:
            avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
            confidence = round(max(0.0, min(1.0, 1 + avg_logprob)), 2)
        else:
            confidence = 0.0

        logger.info(f"Transcribed {file_path}: confidence={confidence}")
        return {"text": text, "confidence": confidence, "language_detected": result.get("language")}
    except Exception as e:
        logger.error(f"Failed to transcribe {file_path}: {e}")
        return {"text": "", "confidence": 0.0, "language_detected": None, "error": str(e)}