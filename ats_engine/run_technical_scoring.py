import json
import os
from datetime import datetime
from ats_engine.technical_scoring_engine import score_answer, score_technical_interview, build_text_report
from utils.logger import logger

QUESTIONS_PATH = "data/technical_interview/question_hierarchy.json"
ANSWERS_PATH = "data/technical_interview/tech_demo_answers.json"
OUTPUT_DIR = "data/technical_interview/results"
MODEL_VERSION = "tech_scoring_v1.0"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_question_index(hierarchy):
    """Map question id to its question. Skill name = second part of the id (react, node, docker)."""
    index = {}
    for domain in hierarchy["domains"]:
        for topic in domain["topics"]:
            for q in topic["questions"]:
                index[q["id"]] = q
    return index


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    questions = build_question_index(load_json(QUESTIONS_PATH))
    data = load_json(ANSWERS_PATH)
    domain = data["domain"]
    summary = []

    for cand in data["candidates"]:
        scored = []
        for q_id, answer in cand["answers"].items():
            if q_id not in questions:
                print(f"  Skipped unknown question id: {q_id}")
                continue
            skill = q_id.split("_")[1]
            scored.append(score_answer(questions[q_id], answer, skill))

        result = score_technical_interview(scored)
        report = build_text_report(cand["candidate_id"], domain, scored, result)
        print(report)
        print()

        base = f"{OUTPUT_DIR}/{cand['candidate_id']}"
        with open(base + "_tech_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        record = {
            "candidate_id": cand["candidate_id"],
            "metadata": {"model_version": MODEL_VERSION, "timestamp": datetime.now().isoformat(),
                         "stage": "technical_scored", "status": "complete"},
            "result": result,
            "answers": scored,
        }
        with open(base + "_tech_result.json", "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        summary.append((cand["candidate_id"], result))
        logger.info(f"Technical scoring done for {cand['candidate_id']}")

    print("COMPARISON")
    print(f"{'Candidate':<16}{'Score':>7}  {'Band':<18}{'Shallow':>8}")
    for name, r in summary:
        print(f"{name:<16}{r['technical_score']:>7}  {r['band']:<18}{r['shallow_answers']:>8}")
    print(f"\nSaved reports to {OUTPUT_DIR}/")


if __name__ == "__main__":
    run()