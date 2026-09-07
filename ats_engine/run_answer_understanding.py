import json
from ats_engine.intent_classifier import classify_intent, is_off_topic
from ats_engine.answer_extractor import build_structured_answer
from utils.logger import logger

KNOWN_SKILLS = ["python", "sql", "excel", "power bi", "machine learning", "java"]

def run():
    with open("data/demo_transcript.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)

    understood_answers = []

    for turn in transcript["turns"]:
        answer_text = turn["candidate_response_normalized"]
        category = turn["question_category"]

        intents = classify_intent(answer_text)
        off_topic = is_off_topic(answer_text, category)
        structured = build_structured_answer(category, answer_text, KNOWN_SKILLS)

        result = {
            "turn_id": turn["turn_id"],
            "question_category": category,
            "detected_intents": intents,
            "is_off_topic": off_topic,
            "structured_answer": structured,
        }
        understood_answers.append(result)
        logger.info(f"Processed turn {turn['turn_id']}: intents={intents}, off_topic={off_topic}")

    output_path = "data/answer_understanding_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(understood_answers, f, indent=2)

    print(f"Done. Processed {len(understood_answers)} answers. Check {output_path}")

if __name__ == "__main__":
    run()