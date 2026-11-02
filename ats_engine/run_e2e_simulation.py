import csv
import json
import os
import time
from statistics import mean
from ats_engine.e2e_stages import parse_resume, run_ats, run_screening, run_hr, run_technical
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.refined_decision_logic import decide_refined, batch_mode
from ats_engine.governance_controls import AuditLog, log_score, log_decision
from ats_engine.cross_round_aggregation_engine import ROUND_LABELS
from utils.logger import logger

DATA_PATH = "data/e2e/e2e_candidates.json"
QUESTIONS_PATH = "data/technical_interview/question_hierarchy.json"
REAL_REVIEWS = "data/e2e/human_reviews.csv"
SIM_REVIEWS = "data/e2e/human_reviews_simulated.csv"
OUT_DIR = "data/e2e"
STAGES = ["resume_upload", "ats", "screening", "hr_interview", "technical_interview", "machine_test", "final_decision"]
ROUNDS = ["ats", "screening", "hr_interview", "technical_interview", "machine_test"]
FIRM = ("Selected", "Rejected")


def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        h = json.load(f)
    return {q["id"]: q for d in h["domains"] for t in d["topics"] for q in t["questions"]}


def run_pipeline(cand, data, questions, audit=None, behavior=None):
    """One candidate through every stage. A failing stage is recorded and the journey continues."""
    job, banks = data["job"], data["banks"]
    role = job["role_category"]
    timings, errors, stages = {}, [], {}

    def timed(name, fn, *args):
        start = time.perf_counter()
        try:
            out = fn(*args)
        except Exception as exc:                      # graceful degradation: record, then carry on
            errors.append(f"{name}: {exc}")
            out = {"score": None}
        timings[name] = (time.perf_counter() - start) * 1000
        return out

    parsed = timed("resume_upload", parse_resume, banks["resume"][cand["resume"]] if cand.get("resume") else "")
    stages["resume_upload"] = {"score": None, "status": parsed.get("status", "error")}
    stages["ats"] = timed("ats", run_ats, parsed, job) if "skills" in parsed else {"score": None}
    stages["screening"] = timed("screening", run_screening, banks["screening"][cand["screening"]]) if cand.get("screening") else {"score": None}
    stages["hr_interview"] = timed("hr_interview", run_hr, banks["hr"][cand["hr"]], role) if cand.get("hr") else {"score": None}
    stages["technical_interview"] = (timed("technical_interview", run_technical, banks["tech"][cand["tech"]], questions)
                                     if cand.get("tech") else {"score": None})
    stages["machine_test"] = {"score": cand.get("machine")}

    scores = {r: stages[r]["score"] for r in ROUNDS}
    context = {"integrity_review_priority": cand.get("integrity", "No concern"),
               "behavioral_label": behavior or cand.get("behavior", "not available")}
    start = time.perf_counter()
    unified = build_unified_score_object(cand["id"], job["job_id"], scores, role, cand.get("low_reliability"), context)
    decision = decide_refined(unified)
    timings["final_decision"] = (time.perf_counter() - start) * 1000
    if audit is not None:
        log_score(audit, unified)
        log_decision(audit, decision)
    return {"candidate_id": cand["id"], "note": cand["note"], "stages": stages, "scores": scores,
            "unified": unified, "decision": decision, "errors": errors, "timings_ms": timings}


def check_invariants(journeys, data, questions, audit):
    """Rules that must hold for every candidate, whatever the scores are."""
    results = []

    def check(name, ok, detail=""):
        results.append({"check": name, "passed": bool(ok), "detail": detail})

    for key, test in [
        ("Weights add up to 1.0", lambda j: abs(sum(j["unified"]["weights_used"].values()) - 1) < 0.01),
        ("Round points add up to the hiring fit", lambda j: abs(sum(r["points_contributed"] or 0 for r in j["unified"]["rounds"].values()) - j["unified"]["hiring_fit"]["percentage"]) < 0.2),
        ("Confidence is between 0 and 1", lambda j: 0 <= j["decision"]["confidence"]["score"] <= 1),
        ("Stage scores are 0 to 100 or empty", lambda j: all(s is None or 0 <= s <= 100 for s in j["scores"].values())),
        ("Human review required and still empty", lambda j: j["decision"]["human_review"]["required"] and j["decision"]["human_review"]["final_decision"] is None),
        ("Integrity High never leads to Rejected", lambda j: not (j["unified"]["context_not_scored"].get("integrity_review_priority") == "High" and j["decision"]["decision"] == "Rejected")),
        ("Missing required round gives Hold / Review", lambda j: j["unified"]["rounds"]["technical_interview"]["score"] is not None or j["decision"]["decision"] == "Hold / Review"),
        ("Preliminary result gives Hold / Review", lambda j: j["unified"]["hiring_fit"]["result_status"] == "final" or j["decision"]["decision"] == "Hold / Review"),
        ("No stage raised an error", lambda j: not j["errors"]),
    ]:
        bad = [j["candidate_id"] for j in journeys if not test(j)]
        check(key, not bad, f"failed for {', '.join(bad)}" if bad else f"{len(journeys)} of {len(journeys)} candidates")

    cands = {c["id"]: c for c in data["candidates"]}
    flagged = sum(j["stages"]["hr_interview"].get("flagged_without_follow_up", 0) for j in journeys)
    check("Every vague or off-topic HR answer got a follow-up", flagged == 0, f"{flagged} missed")

    repeat = [run_pipeline(cands[j["candidate_id"]], data, questions) for j in journeys]
    same = all(a["decision"]["decision"] == b["decision"]["decision"] and a["unified"]["hiring_fit"]["percentage"] == b["unified"]["hiring_fit"]["percentage"]
               for a, b in zip(journeys, repeat))
    check("Same input gives the same result (deterministic)", same)

    other = [run_pipeline(cands[j["candidate_id"]], data, questions, behavior="Low observed engagement") for j in journeys]
    check("Behavioral label never changes a decision", all(a["decision"]["decision"] == b["decision"]["decision"] for a, b in zip(journeys, other)))

    ok, bad_seq = audit.verify()
    check("Audit log chain is intact", ok, "" if ok else f"broken at entry {bad_seq}")
    return results


def find_inconsistencies(journeys):
    """Patterns across stages that a recruiter would want to look at."""
    found = []
    for j in journeys:
        s = {k: v for k, v in j["scores"].items() if v is not None}
        cid = j["candidate_id"]
        if j["stages"]["resume_upload"]["status"] == "unreadable":
            found.append((cid, "Resume upload failed", "Scored without the ATS round. The weight was shared among other rounds."))
        if len(s) >= 2 and max(s.values()) - min(s.values()) >= 40:
            found.append((cid, "Stage scores disagree", f"best {max(s.values())}, worst {min(s.values())}"))
        ats, hr, tech, mach = (j["scores"].get(k) for k in ("ats", "hr_interview", "technical_interview", "machine_test"))
        later = [v for v in (hr, tech, mach) if v is not None]
        if ats is not None and later and ats - mean(later) >= 30:
            found.append((cid, "Resume score far above later rounds", f"ATS {ats}, later rounds average {round(mean(later), 1)} (possible keyword inflation)"))
        if ats is not None and later and mean(later) - ats >= 30:
            found.append((cid, "Later rounds far above resume score", f"ATS {ats}, later rounds average {round(mean(later), 1)}"))
        if hr is not None and tech is not None and hr - tech >= 25:
            found.append((cid, "HR interview far above technical interview", f"HR {hr}, technical {tech}"))
    return found


def load_reviews():
    path = REAL_REVIEWS if os.path.exists(REAL_REVIEWS) else SIM_REVIEWS
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows, ("real reviewers" if path == REAL_REVIEWS else "SIMULATED reviewer (author-written placeholder)")


def compare_with_humans(journeys, rows):
    """Majority human decision per candidate against the AI decision."""
    votes = {}
    for r in rows:
        votes.setdefault(r["candidate_id"], []).append(r["decision"].strip())
    out = []
    for j in journeys:
        v = votes.get(j["candidate_id"])
        if not v:
            continue
        human = max(set(v), key=lambda d: (v.count(d), d == "Hold / Review"))
        ai = j["decision"]["decision"]
        if ai == human:
            kind = "match"
        elif {ai, human} == {"Selected", "Rejected"}:
            kind = "opposite"
        elif ai == "Hold / Review":
            kind = "AI deferred to a person"
        else:
            kind = "AI firmer than the human"
        out.append({"candidate_id": j["candidate_id"], "ai": ai, "human": human, "kind": kind, "split": len(set(v)) > 1})
    return out


def measure_performance(cands, data, questions, repeats=20):
    totals = {s: [] for s in STAGES}
    whole = []
    with batch_mode():
        for _ in range(repeats):
            for c in cands:
                start = time.perf_counter()
                j = run_pipeline(c, data, questions)
                whole.append((time.perf_counter() - start) * 1000)
                for s, ms in j["timings_ms"].items():
                    totals[s].append(ms)
    per_stage = {s: round(mean(v), 3) for s, v in totals.items() if v}
    return {"runs": len(whole), "per_stage_ms": per_stage, "per_candidate_ms": round(mean(whole), 3),
            "candidates_per_second": round(1000 / mean(whole), 1)}


def write_review_packet(data):
    """Everything a human reviewer needs. No AI scores or decisions are shown, so they cannot bias the review."""
    b = data["banks"]
    lines = ["REVIEW PACKET (simulated candidates)", "",
             "For each candidate write one decision: Selected, Hold / Review or Rejected, and a short reason.",
             "Use the file data/e2e/human_reviews.csv with the columns candidate_id,reviewer,decision,reason", ""]
    for c in data["candidates"]:
        lines.append("=" * 60)
        lines.append(f"CANDIDATE {c['id']}  (job: {data['job']['job_id']})")
        lines.append("Resume: " + (b["resume"][c["resume"]] or "(upload failed: no readable text)"))
        if c.get("screening"):
            lines.append("Screening answers:")
            lines += [f"  {i}. {t}" for i, t in enumerate(b["screening"][c["screening"]], 1)]
        if c.get("hr"):
            lines.append("HR interview answers:")
            lines += [f"  {i}. {a['text']}" for i, a in enumerate(b["hr"][c["hr"]], 1)]
        if c.get("tech"):
            lines.append("Technical interview answers:")
            lines += [f"  {q}: {t}" for q, t in b["tech"][c["tech"]].items()]
        lines.append("Machine test score (0 to 100): " + ("not taken" if c.get("machine") is None else str(c["machine"])))
        lines.append("Integrity review priority: " + c.get("integrity", "No concern"))
        lines.append("")
    with open(f"{OUT_DIR}/REVIEW_PACKET.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_reports(journeys, invariants, inconsistencies, comparison, source, perf):
    pass_n = sum(1 for c in invariants if c["passed"])
    lines = ["# End-to-End AI Test Report -- Day 56", "",
             "Simulated candidates only. Stand-ins are used for resume parsing, ATS, screening and the per-answer communication and confidence estimates (see e2e_stages.py).", "",
             "## 1. Pipeline results", "",
             "| Candidate | ATS | Screening | HR | Technical | Machine | Fit % | AI decision | Confidence |", "|---|---|---|---|---|---|---|---|---|"]
    for j in journeys:
        sc = ["-" if j["scores"][r] is None else str(j["scores"][r]) for r in ROUNDS]
        lines.append(f"| {j['candidate_id']} | " + " | ".join(sc) + f" | {j['unified']['hiring_fit']['percentage']} | {j['decision']['decision']} | {j['decision']['confidence']['score']} |")
    lines += ["", f"## 2. Consistency checks ({pass_n} of {len(invariants)} passed)", "", "| Check | Result | Detail |", "|---|---|---|"]
    lines += [f"| {c['check']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in invariants]
    lines += ["", "## 3. Inconsistencies found across stages", "", "| Candidate | Finding | Detail |", "|---|---|---|"]
    lines += [f"| {c} | {t} | {d} |" for c, t, d in inconsistencies] or ["| - | none | - |"]
    exact = sum(1 for c in comparison if c["kind"] == "match")
    lines += ["", f"## 4. AI compared with human judgment (source: {source})", "",
              f"Exact agreement: {exact} of {len(comparison)}", "", "| Candidate | AI | Human | Result |", "|---|---|---|---|"]
    lines += [f"| {c['candidate_id']} | {c['ai']} | {c['human']} | {c['kind']} |" for c in comparison]
    with open(f"{OUT_DIR}/E2E_TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    p = ["# System Performance Analysis -- Day 56", "",
         "Timings are for the code in this test only. Stand-ins are fast. The real ATS and model loading (Whisper, sentence-transformers) are not included.", "",
         f"Runs timed: {perf['runs']} (all candidates, repeated, with logging in batch mode)", "",
         "| Stage | Average milliseconds |", "|---|---|"]
    p += [f"| {s} | {ms} |" for s, ms in perf["per_stage_ms"].items()]
    p += ["", f"Whole journey per candidate: {perf['per_candidate_ms']} ms", f"Throughput: about {perf['candidates_per_second']} candidates per second on this machine"]
    with open(f"{OUT_DIR}/SYSTEM_PERFORMANCE_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    with open(f"{OUT_DIR}/performance.json", "w", encoding="utf-8") as f:
        json.dump(perf, f, indent=2)


def run():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = load_questions()
    audit = AuditLog()

    with batch_mode():
        journeys = [run_pipeline(c, data, questions, audit) for c in data["candidates"]]
        invariants = check_invariants(journeys, data, questions, audit)
    inconsistencies = find_inconsistencies(journeys)
    rows, source = load_reviews()
    comparison = compare_with_humans(journeys, rows)
    perf = measure_performance(data["candidates"], data, questions)
    write_reports(journeys, invariants, inconsistencies, comparison, source, perf)
    write_review_packet(data)

    print("PART 1: PIPELINE RESULTS")
    print(f"{'Candidate':<9}{'ATS':>6}{'Scr':>6}{'HR':>6}{'Tech':>6}{'Mach':>6}{'Fit %':>7}  {'AI decision':<15}{'Conf.':>6}")
    for j in journeys:
        sc = ["-" if j["scores"][r] is None else j["scores"][r] for r in ROUNDS]
        print(f"{j['candidate_id']:<9}" + "".join(f"{v:>6}" for v in sc)
              + f"{j['unified']['hiring_fit']['percentage']:>7}  {j['decision']['decision']:<15}{j['decision']['confidence']['score']:>6}")

    print("\nPART 2: CONSISTENCY CHECKS")
    for c in invariants:
        print(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['check']}" + (f"  ({c['detail']})" if not c["passed"] else ""))
    print(f"  {sum(1 for c in invariants if c['passed'])} of {len(invariants)} passed")

    print("\nPART 3: INCONSISTENCIES ACROSS STAGES")
    for cid, title, detail in inconsistencies:
        print(f"  {cid}: {title} - {detail}")

    print(f"\nPART 4: AI VS HUMAN JUDGMENT (source: {source})")
    exact = sum(1 for c in comparison if c["kind"] == "match")
    print(f"  Exact agreement: {exact} of {len(comparison)}")
    for c in comparison:
        if c["kind"] != "match":
            print(f"  {c['candidate_id']}: AI {c['ai']}, human {c['human']} -> {c['kind']}")

    print("\nPART 5: PERFORMANCE")
    for s, ms in perf["per_stage_ms"].items():
        print(f"  {s:<22}{ms:>8} ms")
    print(f"  Whole journey: {perf['per_candidate_ms']} ms per candidate, about {perf['candidates_per_second']} candidates per second")
    print(f"\nWrote {OUT_DIR}/E2E_TEST_REPORT.md, SYSTEM_PERFORMANCE_ANALYSIS.md, performance.json and REVIEW_PACKET.txt")
    logger.info("End-to-end simulation finished")


if __name__ == "__main__":
    run()