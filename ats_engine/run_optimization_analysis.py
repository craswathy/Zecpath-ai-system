import json
from ats_engine.unified_candidate_score_object import build_unified_score_object
from ats_engine.decision_engine import decide
from ats_engine.decision_config import SELECTED, HOLD, REJECTED
from ats_engine.refined_decision_logic import decide_refined, batch_mode, CRITICAL_FLOOR, SPREAD_LIMIT
from ats_engine.follow_up_trigger_detector import classify_follow_up_need
from ats_engine.refined_intent import classify_follow_up_refined

CANDIDATES_PATH = "data/optimization/labeled_candidates.json"
ANSWERS_PATH = "data/optimization/labeled_answers.json"
ROUND_ORDER = ["ats", "screening", "hr_interview", "technical_interview", "machine_test"]
KEY_ROUNDS = {"technical": ["technical_interview", "machine_test"], "senior": ["technical_interview"]}
REQUIRED = {"technical": "technical_interview", "senior": "technical_interview"}


def reference_decision(s):
    """
    Written rubric, simulated recruiter judgement. It does NOT use the engine's weights.
    1. Integrity High -> Hold.
    2. Fewer than 3 rounds scored, or the required round missing -> Hold.
    3. Selected: mean of scored rounds 75 or above, every round 60 or above,
       key rounds for the role 65 or above.
    4. Rejected: mean below 50, or two or more rounds below 45.
    5. Otherwise Hold.
    """
    scores = {n: v for n, v in s["scores"].items() if v is not None}
    if s["integrity"] == "High":
        return HOLD
    if len(scores) < 3 or (REQUIRED.get(s["role"]) and REQUIRED[s["role"]] not in scores):
        return HOLD
    mean = sum(scores.values()) / len(scores)
    key_ok = all(scores[n] >= 65 for n in KEY_ROUNDS.get(s["role"], []) if n in scores)
    if mean >= 75 and min(scores.values()) >= 60 and key_ok:
        return SELECTED
    if mean < 50 or sum(1 for v in scores.values() if v < 45) >= 2:
        return REJECTED
    return HOLD


def engine_decision(s, refined, floor=CRITICAL_FLOOR, spread=SPREAD_LIMIT):
    context = {"integrity_review_priority": s["integrity"]}
    unified = build_unified_score_object(s["id"], "jd_opt", s["scores"], s["role"], s["low_reliability"], context)
    d = decide_refined(unified, floor, spread) if refined else decide(unified)
    return d["decision"]


def score_set(scenarios, refined, floor=CRITICAL_FLOOR, spread=SPREAD_LIMIT):
    fp = fn = review = correct = 0
    wrong = []
    for s in scenarios:
        ref, got = reference_decision(s), engine_decision(s, refined, floor, spread)
        correct += ref == got
        if got == SELECTED and ref != SELECTED:
            fp += 1
            wrong.append((s["id"], "FALSE POSITIVE", ref, got, s["why"]))
        elif got == REJECTED and ref != REJECTED:
            fn += 1
            wrong.append((s["id"], "FALSE NEGATIVE", ref, got, s["why"]))
        elif got == HOLD and ref != HOLD:
            review += 1
            wrong.append((s["id"], "EXTRA REVIEW", ref, got, s["why"]))
    return {"n": len(scenarios), "correct": correct, "fp": fp, "fn": fn, "extra_review": review, "wrong": wrong}


def show(label, r):
    print(f"  {label:<10} agree {r['correct']}/{r['n']} | false positives {r['fp']} | false negatives {r['fn']} | extra review {r['extra_review']}")


def intent_metrics(answers, refined):
    tp = fp = fn = tn = 0
    misses = []
    for a in answers:
        is_vague = len(a["text"].split()) < 3
        if refined:
            result = classify_follow_up_refined(a["text"], is_vague, a["is_off_topic"])
        else:
            result = classify_follow_up_need(a["text"], is_vague)
        asked = result in ("clarification", "deepening")
        if asked and a["needs_follow_up"]:
            tp += 1
        elif asked and not a["needs_follow_up"]:
            fp += 1
            misses.append(("UNNEEDED FOLLOW-UP", a["text"]))
        elif not asked and a["needs_follow_up"]:
            fn += 1
            misses.append(("MISSED FOLLOW-UP", a["text"]))
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": round(precision, 2),
            "recall": round(recall, 2), "misses": misses}


def run():
    with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
        cand = json.load(f)
    with open(ANSWERS_PATH, "r", encoding="utf-8") as f:
        ans = json.load(f)

    with batch_mode():
        print("=" * 70)
        print("PART 1: DECISION ERRORS (reference = written rubric, simulated)")
        print("=" * 70)
        before_dev = score_set(cand["dev"], False)
        print("Development set (used for choosing thresholds)")
        show("before", before_dev)
        for w in before_dev["wrong"]:
            print(f"    {w[0]}: {w[1]} - reference {w[2]}, engine {w[3]} ({w[4]})")

        print()
        print("PART 2: THRESHOLD SWEEP on the development set")
        print(f"  {'key-round floor':<17}{'spread limit':<14}{'errors (FP+FN)':<16}{'extra review':<13}")
        results = {}
        for floor in (40, 50, 60, 65, 70):
            for spread in (30, 40, 50, 999):
                r = score_set(cand["dev"], True, floor, spread)
                results[(floor, spread)] = (r["fp"] + r["fn"], r["extra_review"])
                print(f"  {floor:<17}{'none' if spread == 999 else spread:<14}{r['fp'] + r['fn']:<16}{r['extra_review']:<13}")
        # Best score = fewest errors, then least extra review. Among the settings that reach it,
        # choose the least intrusive one: the highest spread limit, then the lowest key-round floor.
        best_score = min(v for (f, sp), v in results.items() if sp != 999)
        plateau = [k for k, v in results.items() if v == best_score and k[1] != 999]
        chosen_floor, chosen_spread = max(plateau, key=lambda k: (k[1], -k[0]))
        print(f"  Best score on development set: {best_score[0]} errors, {best_score[1]} extra review")
        print(f"  Settings that reach it: {len(plateau)}. Chosen: key-round floor {chosen_floor}, spread limit {chosen_spread}")
        print(f"  Values in refined_decision_logic.py: floor {CRITICAL_FLOOR}, spread {SPREAD_LIMIT}"
              + ("  (match)" if (chosen_floor, chosen_spread) == (CRITICAL_FLOOR, SPREAD_LIMIT) else "  (DIFFERENT: update the file)"))

        print()
        print("PART 3: BEFORE AND AFTER")
        after_dev = score_set(cand["dev"], True)
        before_hold = score_set(cand["holdout"], False)
        after_hold = score_set(cand["holdout"], True)
        print("Development set")
        show("before", before_dev)
        show("after", after_dev)
        print("Holdout set (not used for choosing thresholds)")
        show("before", before_hold)
        show("after", after_hold)
        for w in after_hold["wrong"]:
            print(f"    still wrong, {w[0]}: {w[1]} - reference {w[2]}, engine {w[3]} ({w[4]})")

        print()
        print("=" * 70)
        print("PART 4: INTENT DETECTION (needs a follow-up?)")
        print("=" * 70)
        for part in ("dev", "holdout"):
            b, a = intent_metrics(ans[part], False), intent_metrics(ans[part], True)
            print(f"{part:<8} before: precision {b['precision']}, recall {b['recall']} (missed {b['fn']}, unneeded {b['fp']})")
            print(f"{part:<8} after:  precision {a['precision']}, recall {a['recall']} (missed {a['fn']}, unneeded {a['fp']})")
            for kind, text in a["misses"]:
                print(f"    after, {kind}: {text}")


if __name__ == "__main__":
    run()