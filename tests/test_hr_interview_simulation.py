import sys
sys.path.append(".")
from ats_engine.hr_interview_scorer import compute_hr_interview_score

def test_confident_profile_scores_higher_than_hesitant():
    confident_turns = [
        {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 90, "behavioral_confidence_score": 90},
    ]
    hesitant_turns = [
        {"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": True, "communication_score": 40, "behavioral_confidence_score": 45},
    ]
    confident_result = compute_hr_interview_score(confident_turns, 0)
    hesitant_result = compute_hr_interview_score(hesitant_turns, 0)
    assert confident_result["hr_interview_score"] > hesitant_result["hr_interview_score"]

def test_contradiction_lowers_consistency_component():
    no_contradiction = compute_hr_interview_score(
        [{"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 80, "behavioral_confidence_score": 80}], 0
    )
    with_contradiction = compute_hr_interview_score(
        [{"turn_id": "t1", "is_off_topic": False, "is_vague_or_missing": False, "communication_score": 80, "behavioral_confidence_score": 80}], 2
    )
    assert with_contradiction["component_scores"]["consistency"] < no_contradiction["component_scores"]["consistency"]