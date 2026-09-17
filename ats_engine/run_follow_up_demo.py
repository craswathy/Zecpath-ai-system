import json
from ats_engine.follow_up_state_tracker import FollowUpStateTracker
from utils.logger import logger

DEMO_ANSWERS = [
    {"question_id": "hr_strengths_01", "answer_text": "good", "is_vague_or_missing": False, "follow_up_eligible": True},
    {"question_id": "hr_strengths_01", "answer_text": "I'm good at solving problems.", "is_vague_or_missing": False, "follow_up_eligible": True},
    {"question_id": "hr_journey_01", "answer_text": "I led a team of five and specifically redesigned our onboarding pipeline, for example cutting setup time by half.", "is_vague_or_missing": False, "follow_up_eligible": True},
    {"question_id": "hr_avail_01", "answer_text": "yes", "is_vague_or_missing": False, "follow_up_eligible": False},
    {"question_id": "hr_team_01", "answer_text": "", "is_vague_or_missing": True, "follow_up_eligible": True},
]

def run():
    tracker = FollowUpStateTracker()
    results = []

    for entry in DEMO_ANSWERS:
        decision = tracker.process_answer(
            entry["question_id"], entry["answer_text"], entry["is_vague_or_missing"], entry["follow_up_eligible"]
        )
        results.append({
            "question_id": entry["question_id"],
            "answer_text": entry["answer_text"],
            "decision": decision,
        })

    output_path = "data/follow_up_demo_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Done. Processed {len(results)} answers through the follow-up engine.")
    for r in results:
        print(f"  [{r['question_id']}] '{r['answer_text'][:40]}' -> {r['decision']['action']} ({r['decision']['reason']})")
    print(f"Full detail: {output_path}")

if __name__ == "__main__":
    run()