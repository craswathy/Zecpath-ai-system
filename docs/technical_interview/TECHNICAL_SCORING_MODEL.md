# Technical Skill Scoring Model (Day 47)

## 1. Four scoring parameters (each 0 to 1)
| Parameter | How it is measured |
|---|---|
| Accuracy | Share of the question's key points the answer covers. For experience questions: 3 evidence checks (names own work, explains what it did, mentions a difficulty or result) |
| Depth | Enough length for the level, plus concrete detail: a number, an example, steps, or a contrast |
| Reasoning | Explaining why: because, so, therefore, if, however, trade-off |
| Real-world applicability | Own project, tools used, production use, real cases, examples |

## 2. Rubric per question type (weights)
| Type | Accuracy | Depth | Reasoning | Applicability | Why |
|---|---|---|---|---|---|
| Conceptual | 0.45 | 0.25 | 0.20 | 0.10 | Knowing the right answer matters most |
| Scenario | 0.25 | 0.20 | 0.30 | 0.25 | Reasoning and practical thinking matter most |
| Experience | 0.20 | 0.30 | 0.15 | 0.35 | Real work evidence matters most |

Answer score = sum of (parameter x weight).

## 3. Shallow vs deep answers
Depth index = average of depth and reasoning.
- 0.65 or above: deep
- 0.25 to below 0.65: moderate
- below 0.25: shallow
- Empty answer: no answer (score 0)

Keyword-listing flag: accuracy 0.6 or higher, but reasoning under 0.2 and depth
under 0.5. Means the answer names the right terms without explaining them.

## 4. Normalizing across difficulty levels
Harder questions count more when answers are combined.
| Level | Weight |
|---|---|
| L1 | 1.0 |
| L2 | 1.5 |
| L3 | 2.0 |

Skill score and overall score = level-weighted average. Each skill also reports
the highest level passed (an answer scoring 0.6 or more).

## 5. Overall result
- Overall score = level-weighted average x 100
- 75 and above: Strong. 50 and above: Adequate. Below 50: Below-expectation.
- A skill below 0.4 lowers the band one level (same idea as the HR component floor).
- Fewer than 5 scored answers: low reliability.

## 6. Technical evaluation report format
1. Summary: score, band, reliability, one-line reason
2. Skill-wise breakdown: score, label, highest level passed, shallow count per skill
3. Parameter averages: accuracy, depth, reasoning, applicability
4. Answer detail: each question with type, level, score, depth label, missed points
5. Note: rule-based decision support, a human recruiter decides

Saved as a readable .txt and a .json (with Day 7 metadata) per candidate in
data/technical_interview/results/.

## 7. Limits
- Accuracy is keyword matching. Correct answers in unexpected words can be missed.
- Reasoning and depth are pattern-based. A candidate who learns the patterns
  (adds "because" and "for example") can raise the score without real knowledge.
  Human review of Strong results is still needed.
- The existing semantic matcher is not used yet. It is the next improvement.
- All weights, thresholds and level weights are starting values, not tuned on real interviews.
- Demo answers were written to show the difference between shallow and deep.
  The results are not a validation of accuracy.