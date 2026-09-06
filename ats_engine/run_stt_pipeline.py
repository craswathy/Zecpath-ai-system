import os
import json
from ats_engine.speech_to_text import transcribe_audio
from ats_engine.speech_quality_checker import assess_response_quality
from ats_engine.transcript_normalizer import normalize_transcript_text
from utils.logger import logger

AUDIO_DIR = "data/audio_samples"
OUTPUT_DIR = "data/stt_results"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audio_files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith((".mp3", ".wav", ".m4a"))]

    logger.info(f"Processing {len(audio_files)} audio samples")

    all_results = []

    for filename in audio_files:
        file_path = os.path.join(AUDIO_DIR, filename)
        stt_result = transcribe_audio(file_path)
        quality_flag = assess_response_quality(stt_result)
        normalized = normalize_transcript_text(stt_result["text"])

        result = {
            "file": filename,
            "raw_transcription": stt_result["text"],
            "normalized_transcription": normalized,
            "confidence": stt_result["confidence"],
            "language_detected": stt_result.get("language_detected"),
            "quality_flag": quality_flag,
        }
        all_results.append(result)

        output_path = os.path.join(OUTPUT_DIR, f"{filename}_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    summary_path = os.path.join(OUTPUT_DIR, "stt_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"Done. Processed {len(audio_files)} audio samples. Check {OUTPUT_DIR}/")

if __name__ == "__main__":
    run()