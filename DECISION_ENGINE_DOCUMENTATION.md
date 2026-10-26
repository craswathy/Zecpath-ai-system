# Final Recommendation AI -- Documentation (Day 52)

## Purpose
Turn the unified candidate score object (Day 51) into a recommendation:
Selected, Hold / Review, or Rejected, with a confidence score and a full explanation.
It recommends. A human recruiter makes the final decision.

## Decision categories
| Decision | Meaning |
|---|---|
| Selected | Recommend moving the candidate to the next stage |
| Hold / Review | A recruiter should review before any decision |
| Rejected | Recommend not moving the candidate forward on current evidence |

## Recommendation logic (rule + score hybrid)
Step 1. Score gives the starting decision, from the Day 51 fit category:
Strong Fit gives Selected, Moderate Fit gives Hold / Review, Weak Fit gives Rejected.

Step 2. Safety rules can move the decision to Hold / Review. They can never move a
candidate toward Selected or Rejected.

| Rule | Triggers when | Effect |
|---|---|---|
| NOT_FINAL | Fewer than 3 rounds scored | Hold / Review |
| REQUIRED_ROUND_MISSING | A round required for the role is not scored (technical roles need the technical interview, others need the HR interview) | Hold / Review |
| INTEGRITY_HIGH | Integrity review priority is High | Hold / Review |
| BORDERLINE | Score within 3 points of the line at 75 (Selected) or 55 (Rejected) | Hold / Review |
| LOW_CONFIDENCE | Confidence below 0.6 for Selected or 0.7 for Rejected | Hold / Review |
| WEAK_ROUND | A round below 40 | Shown for the recruiter. The Day 51 floor already stops a Strong Fit |
| INTEGRITY_MEDIUM | Integrity review priority is Medium | Confidence lowered by 0.10, verification follow-up suggested |

Step 3. Confidence is calculated, and the explanation is written.

## Confidence score (0 to 1)
Confidence = 0.35 x completeness + 0.20 x reliability + 0.25 x agreement + 0.20 x margin
minus an integrity penalty (Medium 0.10, High 0.20).

| Part | Meaning |
|---|---|
| Completeness | Share of the five rounds that were scored |
| Reliability | Share of scored rounds not marked low reliability |
| Agreement | 1 minus (best round minus worst round) / 60, minimum 0 |
| Margin | Distance of the hiring fit from the nearest line (75 or 55), divided by 15, maximum 1 |

A preliminary result is capped at 0.4. Bands: 0.75 and above high, 0.5 to below 0.75 medium,
below 0.5 low.

Confidence shows how far to trust the evidence. It is not the probability that the
candidate is a good hire.

Worked example (demo_confident): completeness 1.0, reliability 1.0, agreement
1 - 16.5/60 = 0.725, margin 9.1/15 = 0.607.
0.35 + 0.20 + 0.181 + 0.121 = 0.85, high.

## Risk factors
| Factor | How it is used |
|---|---|
| Integrity (Day 49 review priority) | High moves the decision to Hold / Review. Medium lowers confidence. Never a reason for rejection |
| Behavioral (Day 48 label) | Shown as context. Never changes a decision or the confidence score |

## Candidate decision output format
```json
{
  "candidate_id": "demo_integrity_flag",
  "job_id": "jd_data_analyst",
  "role_category": "technical",
  "metadata": {"model_version": "decision_v1.0", "timestamp": "...", "stage": "decision", "status": "recommended"},
  "decision": "Hold / Review",
  "recommendation": "A recruiter should review this candidate before any decision.",
  "score_based_decision": "Selected",
  "hiring_fit": {"percentage": 88.6, "category": "Strong Fit", "result_status": "final"},
  "rules_triggered": [
    {"id": "INTEGRITY_HIGH", "reason": "Integrity review priority is High", "moves_to_hold": true}
  ],
  "confidence": {"score": 0.76, "band": "high",
                 "components": {"completeness": 1.0, "reliability": 1.0, "agreement": 0.93, "margin": 0.91}},
  "risk_factors": {
    "integrity": {"review_priority": "High", "effect": "moves decision to Hold / Review"},
    "behavioral": {"label": "Moderate observed engagement", "effect": "none (context only, never changes a decision)"}
  },
  "next_steps": ["Recruiter reviews the integrity timeline. Consider a short live follow-up interview."],
  "human_review": {"required": true, "final_decision": null, "reviewed_by": null},
  "explanation": "Hiring fit 88.6% (Strong Fit, final) suggests Selected. INTEGRITY_HIGH: ... -> moved to Hold / Review. Confidence 0.76 (high). Final recommendation: Hold / Review.",
  "note": "Recommendation only. A human recruiter makes the final decision."
}
```
Every field is stored, so a reviewer can see what the score said, which rules changed
it, how sure the system is, and what to do next.

## Limits
- All thresholds, the 3-point margin, and confidence weights are starting values, not tuned on real hiring outcomes.
- The demo uses simulated candidates.
- Confidence measures evidence quality, not whether the candidate is a good hire.
- The engine reads integrity tags and behavioral labels as given. Their own limits (Days 48 and 49) still apply.
- Not connected to any message or offer system. A recruiter acts on every recommendation.
- Legal and privacy rules for automated decisions differ by country and need a review before any deployment.