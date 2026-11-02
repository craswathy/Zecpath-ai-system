import re
from ats_engine.transcript_normalizer import normalize_transcript_text            # real (Day 42)
from ats_engine.refined_intent import classify_follow_up_refined, count_hedges, is_concrete   # real (Day 54)
from ats_engine.hr_interview_scorer import compute_hr_interview_score             # real (Day 42)
from ats_engine.technical_scoring_engine import score_answer, score_technical_interview  # real (Day 47)
from ats_engine.confidence_analyzer import compute_confidence_indicator           # real (Day 36)

# STAND-INS: simple, transparent versions of stages whose real code was not used in this test.
# To wire in your real modules, replace the body of parse_resume/run_ats (Days 5 to 13),
# run_screening (Day 26), and estimate_communication (Day 35).

SKILL_LIST = ["python", "sql", "statistics", "excel", "power bi", "tableau", "machine learning"]
FILLERS = re.compile(r"\b(?:um+|uh+|er+|you know)\b", re.IGNORECASE)


def parse_resume(text):
    """Stand-in resume parser: finds skills from a fixed list. Under 15 words counts as unreadable."""
    text = text or ""
    if len(text.split()) < 15:
        return {"status": "unreadable", "skills": []}
    lower = text.lower()
    skills = [s for s in SKILL_LIST if re.search(r"\b" + re.escape(s) + r"\b", lower)]
    return {"status": "ok", "skills": skills}


def run_ats(parsed, job):
    """Stand-in ATS: 70 percent required skills, 30 percent preferred skills. Keyword counting only."""
    if parsed["status"] != "ok":
        return {"score": None, "note": "resume unreadable"}
    req = sum(1 for s in job["required"] if s in parsed["skills"]) / len(job["required"])
    pref = sum(1 for s in job["preferred"] if s in parsed["skills"]) / len(job["preferred"])
    return {"score": round(100 * (0.7 * req + 0.3 * pref), 1), "skills": parsed["skills"]}


def run_screening(answers):
    """Stand-in screening: per answer 0.4 long enough, 0.4 concrete, 0.2 not hedged."""
    scores = []
    for text in answers:
        strong, _ = count_hedges(text)
        scores.append(0.4 * (len(text.split()) >= 12) + 0.4 * is_concrete(text) + 0.2 * (strong == 0))
    return {"score": round(100 * sum(scores) / len(scores), 1)}


def estimate_communication(raw, clean):
    """Stand-in for the Day 35 scorer: length and fillers only."""
    fillers = len(FILLERS.findall(raw))
    length = min(len(clean.split()) / 20, 1.0)
    return round(100 * (0.6 * length + 0.4 * max(0.0, 1 - 0.1 * fillers)))


def estimate_confidence(raw):
    """
    Wires real confidence_analyzer module from Day 36 into the E2E simulation.
    Uses compute_confidence_indicator to calculate score on a 0-100 scale.
    """
    words = len(raw.split())
    # Estimate speaking duration assuming average speed (~2.5 words/sec)
    estimated_duration = max(1.0, words / 2.5)
    
    result = compute_confidence_indicator(
        raw_answer_text=raw,
        word_count=words,
        duration_seconds=estimated_duration,
        stt_confidence=1.0
    )
    # Convert 0.0 - 1.0 score to 0 - 100 scale for HR interview evaluation
    return round(result["confidence_score"] * 100, 1)


def run_hr(answers, role):
    """Real cleanup, follow-up logic, HR scoring, and Day 36 confidence analyzer. Communication is a stand-in."""
    per_turn, follow_ups, missed = [], 0, 0
    for a in answers:
        raw, off_topic = a["text"], a.get("off_topic", False)
        clean = normalize_transcript_text(raw)
        vague = len(clean.split()) < 3
        follow = classify_follow_up_refined(clean, vague, off_topic)
        if follow in ("clarification", "deepening"):
            follow_ups += 1
        elif off_topic or vague:
            missed += 1                      # should never happen: a flagged answer without a follow-up
        per_turn.append({
            "is_off_topic": off_topic,
            "is_vague_or_missing": vague,
            "communication_score": estimate_communication(raw, clean),
            "behavioral_confidence_score": estimate_confidence(raw)
        })
    result = compute_hr_interview_score(per_turn, 0, role)
    return {
        "score": result["hr_interview_score"],
        "band": result["performance_band"],
        "weak_components": result["weak_components"],
        "follow_ups": follow_ups,
        "flagged_without_follow_up": missed
    }


def run_technical(answers, question_index):
    """Real technical scoring (Day 47)."""
    scored = []
    for q_id, text in answers.items():
        if q_id in question_index:
            scored.append(score_answer(question_index[q_id], text, q_id.split("_")[1]))
    result = score_technical_interview(scored)
    return {
        "score": result["technical_score"],
        "band": result["band"],
        "weak_skills": result["weak_skills"],
        "shallow_answers": result["shallow_answers"]
    }