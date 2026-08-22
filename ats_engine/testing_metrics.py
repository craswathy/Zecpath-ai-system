def compute_precision_recall(manual_reviews):
    """
    manual_reviews: list of dicts like
      {"ai_decision": "Shortlisted", "manual_decision": "Shortlist", "agrees": True}

    Precision = of all candidates AI shortlisted, how many manual review agreed with
    Recall = of all candidates manual review would shortlist, how many AI caught
    """
    ai_shortlisted = [r for r in manual_reviews if r["ai_decision"] == "Shortlisted"]
    manual_shortlist = [r for r in manual_reviews if r["manual_decision"] == "Shortlist"]

    true_positives = [r for r in manual_reviews if r["ai_decision"] == "Shortlisted" and r["manual_decision"] == "Shortlist"]

    precision = len(true_positives) / len(ai_shortlisted) if ai_shortlisted else None
    recall = len(true_positives) / len(manual_shortlist) if manual_shortlist else None

    mismatch_cases = [r for r in manual_reviews if not r["agrees"]]

    return {
        "precision": round(precision, 2) if precision is not None else "N/A (no AI shortlists)",
        "recall": round(recall, 2) if recall is not None else "N/A (no manual shortlists)",
        "total_cases": len(manual_reviews),
        "mismatch_count": len(mismatch_cases),
        "mismatch_cases": mismatch_cases,
    }


if __name__ == "__main__":
    # Fill this in with your real Step 2 manual review results
    sample_reviews = [
        {"resume": "da_resume_1", "ai_decision": "Shortlisted", "manual_decision": "Shortlist", "agrees": True},
        # add one entry per resume from your manual review
    ]
    import json
    result = compute_precision_recall(sample_reviews)
    print(json.dumps(result, indent=2))