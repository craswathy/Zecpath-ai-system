import itertools

from ats_engine.polished_decision_service import safe_decide

ROUNDS = ["ats", "screening", "hr_interview"]
GRID = [20, 40, 60, 80, 100]


def decide(scores, role="technical"):
    return safe_decide({"round_scores": scores, "role_category": role})


def check_deterministic():
    scores = {"ats": 73.4, "screening": 61.0, "hr_interview": 55.5}
    return decide(scores) == decide(dict(reversed(list(scores.items()))))


def check_monotonic():
    """Raising one round score must never lower the hiring-fit percentage."""
    bad = []
    for combo in itertools.product(GRID, repeat=3):
        base = dict(zip(ROUNDS, combo))
        base_fit = decide(base)["hiring_fit_percentage"]
        for r in ROUNDS:
            if base[r] <= 90:
                up = dict(base, **{r: base[r] + 10})
                if decide(up)["hiring_fit_percentage"] < base_fit:
                    bad.append((base, r))
    return bad


def check_range():
    return [c for c in itertools.product(GRID, repeat=3)
            if not 0 <= decide(dict(zip(ROUNDS, c)))["hiring_fit_percentage"] <= 100]


def check_boundaries():
    """All rounds equal means fit equals that score. Test around the thresholds."""
    expected = {80: "Strong Fit", 75: "Strong Fit", 74: "Moderate Fit",
                55: "Moderate Fit", 54: "Weak Fit"}
    return {s: (decide({r: s for r in ROUNDS})["category"], want)
            for s, want in expected.items()
            if decide({r: s for r in ROUNDS})["category"] != want}


def run():
    report = {
        "deterministic": check_deterministic(),
        "monotonic_violations": len(check_monotonic()),
        "out_of_range": len(check_range()),
        "boundary_mismatches": check_boundaries(),
    }
    for k, v in report.items():
        print(f"{k:<24} {v}")
    return report


if __name__ == "__main__":
    run()