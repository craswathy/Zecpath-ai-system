import sys
sys.path.append(".")
from ats_engine.candidate_ranker import classify_candidate, rank_candidates

def test_classify_shortlisted():
    assert classify_candidate(80) == "Shortlisted"

def test_classify_review_zone():
    assert classify_candidate(60) == "Needs Review"

def test_classify_auto_rejected():
    assert classify_candidate(30) == "Auto-Rejected"

def test_rank_candidates_sorted_descending():
    candidates = [{"candidate": "a", "final_score": 40}, {"candidate": "b", "final_score": 90}]
    ranked = rank_candidates(candidates)
    assert ranked[0]["candidate"] == "b"
    assert ranked[0]["rank"] == 1