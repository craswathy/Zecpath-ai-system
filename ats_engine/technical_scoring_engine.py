import re
from ats_engine.technical_scoring_config import (
    PARAMETER_WEIGHTS, LEVEL_WEIGHTS, TARGET_WORDS, PASS_SCORE, SKILL_FLOOR,
    MIN_RELIABLE_ANSWERS, BAND_STRONG, BAND_ADEQUATE,
)
from utils.logger import logger

BAND_ORDER = ["Below-expectation", "Adequate", "Strong"]

STOPWORDS = {
    "that", "this", "with", "from", "when", "what", "into", "each", "your", "have", "been",
    "were", "will", "than", "then", "them", "they", "their", "there", "about", "which",
    "names", "name", "explains", "explain", "mentions", "mention", "describes", "describe",
    "gives", "give", "used", "uses", "using", "does", "also", "make", "makes",
}

DETAIL_PATTERNS = {
    "number": re.compile(r"\d"),
    "example": re.compile(r"\bfor example\b|\bfor instance\b|\bsuch as\b|\be\.g\.", re.I),
    "steps": re.compile(r"\bfirst\b|\bthen\b|\bnext\b|\bfinally\b|\bafter that\b", re.I),
    "contrast": re.compile(r"\bwhereas\b|\binstead\b|\bcompared\b|\bversus\b|\brather than\b|\bunlike\b", re.I),
}

REASONING_PATTERN = re.compile(
    r"\bbecause\b|\bsince\b|\bso\b|\btherefore\b|\bhence\b|\bwhich means\b|\bas a result\b"
    r"|\botherwise\b|\bwhich is why\b|\bthat is why\b|\bif\b|\btrade-?offs?\b|\bhowever\b"
    r"|\bbut\b|\bdownside\b|\bdepends\b|\bwhereas\b|\bthen\b",
    re.I,
)

APPLICABILITY_PATTERN = re.compile(
    r"\bmy (?:\w+ ){0,2}(?:project|experience|work|team)\b|\bi (?:used|built|made|worked|fixed|led|designed|deployed|handled)\b"
    r"|\bin production\b|\bat work\b|\bin practice\b|\breal[- ]world\b"
    r"|\bwe (?:used|built|deployed|fixed)\b|\bfor example\b|\bfor instance\b|\bsuch as\b",
    re.I,
)


def _stems(text):
    """Meaningful words cut to 5 letters, so 'memoize' and 'memoization' match."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w[:5] for w in words if len(w) > 3 and w not in STOPWORDS}


def score_accuracy(answer_text, key_points):
    """Share of the question's key points the answer covers (0-1)."""
    answer_stems = _stems(answer_text)
    matched, missed = [], []
    for point in key_points:
        point_stems = _stems(point)
        if point_stems and len(point_stems & answer_stems) / len(point_stems) >= 0.5:
            matched.append(point)
        else:
            missed.append(point)
    accuracy = len(matched) / len(key_points) if key_points else 0.0
    return round(accuracy, 2), matched, missed


EXPERIENCE_OWN_WORK = re.compile(
    r"\bi (?:built|made|created|developed|designed|worked|led|wrote|used|handled)\b"
    r"|\bmy (?:\w+ ){0,2}(?:project|component|work|team)\b",
    re.I,
)
EXPERIENCE_DIFFICULTY = re.compile(
    r"hardest|hard part|difficult|challeng|problem|issue|struggl|bug|learn|result|reduc|improv|\d", re.I
)


def score_experience_evidence(answer_text):
    """
    Experience questions have no single right answer, so accuracy is a 3-part evidence check:
    names own work, explains what it did (enough words), mentions a difficulty or result.
    """
    checks = [
        ("names own work", bool(EXPERIENCE_OWN_WORK.search(answer_text))),
        ("explains what it did", len(answer_text.split()) >= 15),
        ("mentions a difficulty or result", bool(EXPERIENCE_DIFFICULTY.search(answer_text))),
    ]
    matched = [name for name, ok in checks if ok]
    missed = [name for name, ok in checks if not ok]
    return round(len(matched) / len(checks), 2), matched, missed


def score_depth(answer_text, level):
    """Enough length for the level plus concrete detail (number, example, steps, contrast)."""
    words = len(answer_text.split())
    length_score = min(words / TARGET_WORDS[level], 1.0)
    detail_hits = sum(1 for p in DETAIL_PATTERNS.values() if p.search(answer_text))
    detail_score = min(detail_hits / 2, 1.0)
    return round(0.5 * length_score + 0.5 * detail_score, 2)


def score_reasoning(answer_text):
    """Because / therefore / if / trade-off style explanation (0-1)."""
    hits = len(REASONING_PATTERN.findall(answer_text))
    return round(min(hits / 2, 1.0), 2)


def score_applicability(answer_text):
    """Real-world use: own project, tools used, production, real cases (0-1)."""
    hits = len(APPLICABILITY_PATTERN.findall(answer_text))
    return round(min(hits / 2, 1.0), 2)


def classify_depth(accuracy, depth, reasoning):
    """Shallow vs deep. Also catches answers that list keywords without explaining."""
    depth_index = (depth + reasoning) / 2
    if depth_index >= 0.65:
        label = "deep"
    elif depth_index >= 0.25:
        label = "moderate"
    else:
        label = "shallow"
    keyword_listing = accuracy >= 0.6 and reasoning < 0.2 and depth < 0.5
    return label, keyword_listing


def score_answer(question, answer_text, topic):
    """Score one answer. question needs: id, type, level, key_points."""
    answer_text = (answer_text or "").strip()
    q_type, level = question["type"], question["level"]

    if not answer_text:
        return {
            "question_id": question["id"], "topic": topic, "type": q_type, "level": level,
            "parameters": {"accuracy": 0.0, "depth": 0.0, "reasoning": 0.0, "applicability": 0.0},
            "score": 0.0, "depth_label": "no answer", "keyword_listing": False,
            "matched_points": [], "missed_points": list(question["key_points"]),
            "explanation": "No answer given.",
        }

    if q_type == "experience":
        accuracy, matched, missed = score_experience_evidence(answer_text)
        total_points = 3
    else:
        accuracy, matched, missed = score_accuracy(answer_text, question["key_points"])
        total_points = len(question["key_points"])
    parameters = {
        "accuracy": accuracy,
        "depth": score_depth(answer_text, level),
        "reasoning": score_reasoning(answer_text),
        "applicability": score_applicability(answer_text),
    }
    weights = PARAMETER_WEIGHTS[q_type]
    score = round(sum(parameters[p] * weights[p] for p in parameters), 2)
    label, keyword_listing = classify_depth(accuracy, parameters["depth"], parameters["reasoning"])

    explanation = (
        f"{q_type} {level}: covered {len(matched)} of {total_points} {'evidence checks' if q_type == 'experience' else 'key points'} | "
        + " | ".join(f"{p} {v} (weight {weights[p]})" for p, v in parameters.items())
        + f" | answer is {label}"
    )
    if keyword_listing:
        explanation += " | lists key points with little explanation"

    logger.info(f"Technical answer {question['id']}: {score} ({label})")
    return {
        "question_id": question["id"], "topic": topic, "type": q_type, "level": level,
        "parameters": parameters, "score": score, "depth_label": label,
        "keyword_listing": keyword_listing, "matched_points": matched,
        "missed_points": missed, "explanation": explanation,
    }


def _weighted_average(answers):
    total_weight = sum(LEVEL_WEIGHTS[a["level"]] for a in answers)
    return sum(a["score"] * LEVEL_WEIGHTS[a["level"]] for a in answers) / total_weight


def _skill_label(score):
    if score >= 0.75:
        return "Strong"
    if score >= 0.5:
        return "Adequate"
    return "Weak"


def score_technical_interview(scored_answers):
    """
    Combine answer scores into a skill-wise breakdown and one overall score.
    Harder levels count more (LEVEL_WEIGHTS), so scores are comparable across levels.
    """
    if not scored_answers:
        return {"technical_score": 0.0, "band": "No data", "skills": {}, "explanation": "No answers to score."}

    skills = {}
    for topic in sorted({a["topic"] for a in scored_answers}):
        topic_answers = [a for a in scored_answers if a["topic"] == topic]
        passed = [a["level"] for a in topic_answers if a["score"] >= PASS_SCORE]
        skills[topic] = {
            "score": round(_weighted_average(topic_answers), 2),
            "answers": len(topic_answers),
            "highest_level_passed": max(passed) if passed else None,
            "shallow_answers": sum(1 for a in topic_answers if a["depth_label"] in ("shallow", "no answer")),
        }
        skills[topic]["label"] = _skill_label(skills[topic]["score"])

    parameter_averages = {
        p: round(sum(a["parameters"][p] for a in scored_answers) / len(scored_answers), 2)
        for p in ("accuracy", "depth", "reasoning", "applicability")
    }

    overall = round(_weighted_average(scored_answers) * 100, 1)
    if overall >= BAND_STRONG:
        base_band = "Strong"
    elif overall >= BAND_ADEQUATE:
        base_band = "Adequate"
    else:
        base_band = "Below-expectation"

    weak_skills = [t for t, s in skills.items() if s["score"] < SKILL_FLOOR]
    band, adjusted_from = base_band, None
    if weak_skills and base_band != "Below-expectation":
        band = BAND_ORDER[BAND_ORDER.index(base_band) - 1]
        adjusted_from = base_band

    reliability = "reliable" if len(scored_answers) >= MIN_RELIABLE_ANSWERS else "low_reliability"
    shallow = sum(1 for a in scored_answers if a["depth_label"] in ("shallow", "no answer"))
    listing = sum(1 for a in scored_answers if a["keyword_listing"])

    explanation = (
        f"Level-weighted average of {len(scored_answers)} answers = {overall}"
        + (f" | band lowered from {adjusted_from}: weak skill {', '.join(weak_skills)}" if adjusted_from else "")
        + (f" | {shallow} shallow answer(s)" if shallow else "")
        + (f" | {listing} answer(s) list keywords without explaining" if listing else "")
    )

    return {
        "technical_score": overall, "band": band, "band_adjusted_from": adjusted_from,
        "skills": skills, "weak_skills": weak_skills, "parameter_averages": parameter_averages,
        "answers_scored": len(scored_answers), "reliability": reliability,
        "shallow_answers": shallow, "keyword_listing_answers": listing,
        "explanation": explanation,
    }


def build_text_report(candidate_id, domain, scored_answers, result):
    """Plain-text technical evaluation report (format in TECHNICAL_SCORING_MODEL.md)."""
    lines = ["=" * 64, "TECHNICAL EVALUATION REPORT", "=" * 64]
    lines.append(f"Candidate: {candidate_id} | Domain: {domain}")
    lines.append("")
    lines.append("1. SUMMARY")
    lines.append(f"  Technical score: {result['technical_score']}/100 | Band: {result['band']}")
    if result.get("band_adjusted_from"):
        lines.append(f"  Band lowered from {result['band_adjusted_from']} (weak skill: {', '.join(result['weak_skills'])})")
    lines.append(f"  Reliability: {result['reliability']} ({result['answers_scored']} answers scored)")
    lines.append(f"  Why: {result['explanation']}")
    lines.append("")
    lines.append("2. SKILL-WISE BREAKDOWN")
    for topic, s in result["skills"].items():
        top = s["highest_level_passed"] or "none"
        lines.append(f"  {topic:<14} {s['score']:<5} {s['label']:<9} highest level passed: {top} | answers: {s['answers']} | shallow: {s['shallow_answers']}")
    lines.append("")
    lines.append("3. PARAMETER AVERAGES")
    for p, v in result["parameter_averages"].items():
        lines.append(f"  {p:<14} {v}")
    lines.append("")
    lines.append("4. ANSWER DETAIL")
    for a in scored_answers:
        lines.append(f"  {a['question_id']} ({a['type']}, {a['level']}): score {a['score']} | {a['depth_label']}")
        if a["missed_points"]:
            lines.append(f"    Missed: {'; '.join(a['missed_points'])}")
    lines.append("")
    lines.append("5. NOTE")
    lines.append("  Rule-based decision support. A human recruiter makes the final decision.")
    return "\n".join(lines)