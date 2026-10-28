from datetime import datetime
from ats_engine.report_config import (
    MODEL_VERSION, ROUND_NAMES, ROUND_LABELS, STRENGTH_ROUND_SCORE, WEAKNESS_ROUND_SCORE, ROUND_FLOOR,
    HR_COMPONENT_STRONG, HR_COMPONENT_WEAK, SKILL_STRONG, SKILL_WEAK, SHALLOW_FLAG, MAX_ITEMS, LIMITATIONS,
)
from utils.logger import logger


def _round_score(unified, name):
    return unified["rounds"][name]["score"]


def _section(title, score, lines, available=True):
    return {"title": title, "score": score, "available": available, "lines": lines}


def _not_scored(title):
    return _section(title, None, ["Not scored yet."], available=False)


def build_sections(unified, details):
    """One section per evaluation stage, written as short lines a recruiter can scan."""
    sections = {}

    ats = details.get("ats", {})
    if _round_score(unified, "ats") is None:
        sections["ats"] = _not_scored("ATS summary")
    else:
        lines = [ats["summary"]] if ats.get("summary") else []
        if ats.get("matched_skills"):
            lines.append("Matched skills: " + ", ".join(ats["matched_skills"]))
        if ats.get("missing_skills"):
            lines.append("Skills not found: " + ", ".join(ats["missing_skills"]))
        sections["ats"] = _section("ATS summary", _round_score(unified, "ats"), lines or ["No extra detail provided."])

    scr = details.get("screening", {})
    if _round_score(unified, "screening") is None:
        sections["screening"] = _not_scored("Screening results")
    else:
        sections["screening"] = _section("Screening results", _round_score(unified, "screening"),
                                         [scr["summary"]] if scr.get("summary") else ["No extra detail provided."])

    hr = details.get("hr_interview", {})
    if _round_score(unified, "hr_interview") is None:
        sections["hr_interview"] = _not_scored("HR interview insights")
    else:
        lines = []
        if hr.get("band"):
            lines.append(f"Performance band: {hr['band']}" + (f" (reliability: {hr['reliability']})" if hr.get("reliability") else ""))
        if hr.get("component_scores"):
            lines.append("Components (0 to 1): " + ", ".join(f"{k} {v}" for k, v in hr["component_scores"].items()))
        if hr.get("weak_components"):
            lines.append("Weak components: " + ", ".join(hr["weak_components"]))
        if hr.get("summary"):
            lines.append(hr["summary"])
        sections["hr_interview"] = _section("HR interview insights", _round_score(unified, "hr_interview"),
                                            lines or ["No extra detail provided."])

    tech = details.get("technical_interview", {})
    if _round_score(unified, "technical_interview") is None:
        sections["technical_interview"] = _not_scored("Technical performance")
    else:
        lines = []
        if tech.get("band"):
            lines.append(f"Performance band: {tech['band']}")
        for skill, s in tech.get("skills", {}).items():
            top = s.get("highest_level_passed") or "none"
            lines.append(f"Skill {skill}: {s['score']} ({s['label']}), highest level passed: {top}")
        if tech.get("shallow_answers") is not None:
            lines.append(f"Shallow answers: {tech['shallow_answers']}")
        sections["technical_interview"] = _section("Technical performance", _round_score(unified, "technical_interview"),
                                                   lines or ["No extra detail provided."])

    mt = details.get("machine_test", {})
    if _round_score(unified, "machine_test") is None:
        sections["machine_test"] = _not_scored("Machine test")
    else:
        sections["machine_test"] = _section("Machine test", _round_score(unified, "machine_test"),
                                            [mt["summary"]] if mt.get("summary") else ["No extra detail provided."])

    context = unified.get("context_not_scored", {})
    lines = [
        "Behavioral label: " + context.get("behavioral_label", "not available")
        + " (context only. It does not change the score or the recommendation.)",
        "Integrity review priority: " + context.get("integrity_review_priority", "not available")
        + " (a reason to look, not proof of misconduct)",
    ]
    sections["behavioral_flags"] = _section("Behavioral and integrity flags", None, lines)
    return sections


def collect_strengths(unified, details):
    items = []
    strong_rounds = [f"{ROUND_LABELS[n]} {_round_score(unified, n)}" for n in ROUND_NAMES
                     if _round_score(unified, n) is not None and _round_score(unified, n) >= STRENGTH_ROUND_SCORE]
    if strong_rounds:
        items.append(f"Rounds scored {STRENGTH_ROUND_SCORE} or above: " + ", ".join(strong_rounds))
    hr_strong = [f"{c} {v}" for c, v in details.get("hr_interview", {}).get("component_scores", {}).items()
                 if v >= HR_COMPONENT_STRONG]
    if hr_strong:
        items.append(f"HR interview components at {HR_COMPONENT_STRONG} or above: " + ", ".join(hr_strong))
    skills_strong = [f"{k} {s['score']} (highest level passed: {s.get('highest_level_passed') or 'none'})"
                     for k, s in details.get("technical_interview", {}).get("skills", {}).items()
                     if s["score"] >= SKILL_STRONG]
    if skills_strong:
        items.append(f"Technical skills at {SKILL_STRONG} or above: " + ", ".join(skills_strong))
    matched = details.get("ats", {}).get("matched_skills", [])
    if len(matched) >= 3:
        items.append(f"Resume matches {len(matched)} required skills")
    return items[:MAX_ITEMS] or ["No standout strengths found in the available data."]


def collect_weaknesses(unified, details):
    items = []
    weak_rounds = [f"{ROUND_LABELS[n]} {_round_score(unified, n)}" for n in ROUND_NAMES
                   if _round_score(unified, n) is not None and _round_score(unified, n) < WEAKNESS_ROUND_SCORE]
    if weak_rounds:
        items.append(f"Rounds scored below {WEAKNESS_ROUND_SCORE}: " + ", ".join(weak_rounds))
    hr_weak = [f"{c} {v}" for c, v in details.get("hr_interview", {}).get("component_scores", {}).items()
               if v < HR_COMPONENT_WEAK]
    if hr_weak:
        items.append(f"HR interview components below {HR_COMPONENT_WEAK}: " + ", ".join(hr_weak))
    skills_weak = [f"{k} {s['score']}" for k, s in details.get("technical_interview", {}).get("skills", {}).items()
                   if s["score"] < SKILL_WEAK]
    if skills_weak:
        items.append(f"Technical skills below {SKILL_WEAK}: " + ", ".join(skills_weak))
    shallow = details.get("technical_interview", {}).get("shallow_answers") or 0
    if shallow >= SHALLOW_FLAG:
        items.append(f"{shallow} technical answers named terms without explaining them")
    missing = details.get("ats", {}).get("missing_skills", [])
    if missing:
        items.append("Skills not found in the resume: " + ", ".join(missing))
    return items[:MAX_ITEMS] or ["No clear weaknesses found in the available data."]


def collect_risks(unified, decision):
    """Risk indicators: integrity, weak rounds, thin evidence. Behavioral labels are not risks."""
    risks = []
    integrity = unified.get("context_not_scored", {}).get("integrity_review_priority")
    if integrity == "High":
        risks.append({"level": "high", "text": "Integrity review priority is High. Review the integrity timeline before deciding. This is not proof of misconduct."})
    elif integrity == "Medium":
        risks.append({"level": "medium", "text": "Integrity review priority is Medium. Consider a verification follow-up question."})

    weak = [ROUND_LABELS[n] for n in ROUND_NAMES
            if _round_score(unified, n) is not None and _round_score(unified, n) < ROUND_FLOOR]
    if weak:
        risks.append({"level": "medium", "text": f"A round scored below {ROUND_FLOOR}: {', '.join(weak)}."})

    status = unified["hiring_fit"]["result_status"]
    if status != "final":
        risks.append({"level": "medium", "text": f"The result is {status}. Not enough rounds are scored yet."})
    missing_required = [r["reason"] for r in decision["rules_triggered"] if r["id"] == "REQUIRED_ROUND_MISSING"]
    for reason in missing_required:
        risks.append({"level": "medium", "text": reason + "."})

    not_scored = [ROUND_LABELS[n] for n in ROUND_NAMES if _round_score(unified, n) is None]
    if not_scored and status == "final":
        risks.append({"level": "info", "text": f"Not scored: {', '.join(not_scored)}. The weight of a missing round is shared among the other rounds."})

    low_rel = [ROUND_LABELS[n] for n in ROUND_NAMES if unified["rounds"][n]["low_reliability"]]
    if low_rel:
        risks.append({"level": "info", "text": f"Low-reliability round counted at half weight: {', '.join(low_rel)}."})

    if decision["confidence"]["band"] == "low":
        risks.append({"level": "medium", "text": f"Decision confidence is low ({decision['confidence']['score']})."})

    return risks or [{"level": "info", "text": "No risk indicators found."}]


def build_report(unified, decision, details=None):
    """
    Combine the Day 51 unified score object, the Day 52 decision object and optional
    per-round details into one recruiter report.
    """
    details = details or {}
    fit = unified["hiring_fit"]
    rounds = []
    for name in ROUND_NAMES:
        r = unified["rounds"][name]
        rounds.append({"round": name, "label": ROUND_LABELS[name], "score": r["score"],
                       "weight": r["weight_used"], "points": r["points_contributed"],
                       "low_reliability": r["low_reliability"]})

    report = {
        "report_id": f"report_{unified['candidate_id']}",
        "metadata": {"model_version": MODEL_VERSION, "timestamp": datetime.now().isoformat(),
                     "stage": "report", "status": "generated"},
        "candidate": {"candidate_id": unified["candidate_id"], "job_id": unified["job_id"],
                      "role_category": unified["role_category"]},
        "headline": {
            "decision": decision["decision"], "recommendation": decision["recommendation"],
            "hiring_fit_percentage": fit["percentage"], "fit_category": fit["category"],
            "result_status": fit["result_status"],
            "confidence_score": decision["confidence"]["score"], "confidence_band": decision["confidence"]["band"],
        },
        "round_scores": rounds,
        "strengths": collect_strengths(unified, details),
        "weaknesses": collect_weaknesses(unified, details),
        "risk_indicators": collect_risks(unified, decision),
        "sections": build_sections(unified, details),
        "final_recommendation": {
            "decision": decision["decision"], "recommendation": decision["recommendation"],
            "score_based_decision": decision["score_based_decision"],
            "rules_triggered": [{"id": r["id"], "reason": r["reason"], "moved_to_hold": r["moves_to_hold"]}
                                for r in decision["rules_triggered"]],
            "next_steps": decision["next_steps"], "explanation": decision["explanation"],
        },
        "human_review": {"required": True, "final_decision": None, "reviewed_by": None, "date": None, "comment": None},
        "limitations": LIMITATIONS,
    }
    logger.info(f"Built hiring report for {unified['candidate_id']}: {decision['decision']}")
    return report