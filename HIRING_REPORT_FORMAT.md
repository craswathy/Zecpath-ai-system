# Hiring Intelligence Report -- Format and Generator (Day 53)

## Purpose
Give recruiters one complete, readable candidate evaluation. The report combines the
Day 51 unified score object, the Day 52 decision object, and per-stage details.

## Report layout (recruiter-friendly)
| Part | Content |
|---|---|
| Header | Candidate, job, role profile, date, model version |
| At a glance | Recommendation badge, hiring fit %, decision confidence |
| Round scores | Score, weight and points for each of the five rounds, with a bar |
| Strengths, weaknesses, risk indicators | Three short lists, one line per finding |
| Details by stage | ATS summary, screening, HR insights, technical performance, machine test, behavioral and integrity flags |
| Final recommendation | Decision, what the score alone suggested, rules that changed it, next steps |
| Human review | Blank boxes for the final decision, reviewer, date and comment |
| Limits | Plain-language limits of the report |

The first screen answers "what is the recommendation and why", and the details follow below.

## How strengths, weaknesses and risks are chosen
All lists come from fixed rules on stored data. No text about the candidate is written
by AI.

| List | Rule |
|---|---|
| Strengths | Rounds scored 75 or above; HR components 0.8 or above; technical skills 0.75 or above; resume matching 3 or more required skills |
| Weaknesses | Rounds below 55; HR components below 0.5; technical skills below 0.5; 2 or more shallow technical answers; skills not found in the resume |
| Risk indicators | Integrity priority High (high) or Medium (medium); a round below 40; preliminary result; required round missing; low confidence; low-reliability rounds and missing rounds (info) |

Each list is limited to 6 items.

Behavioral labels are shown in their own section as context. They are never a weakness
or a risk, and they do not change the score or the recommendation.

## Export formats
| Format | Use |
|---|---|
| HTML (.html) | Main format. Self-contained, printable. In a browser: Print, then Save as PDF |
| Text (.txt) | Plain copy that opens anywhere |
| JSON (.json) | Machine-readable copy with every field, for other systems |

Files are saved as `<candidate_id>_report.<format>`.

## JSON fields
metadata, candidate, headline, round_scores, strengths, weaknesses, risk_indicators,
sections, final_recommendation, human_review, limitations.

## Inputs
- Unified score object (Day 51)
- Decision object (Day 52)
- Optional details per stage: ATS summary and skills, screening summary, HR components,
  technical skill scores, machine test summary. A missing stage shows "Not scored yet"
  or "No extra detail provided".

## Limits
- The demo uses simulated candidates and illustrative stage details.
- Thresholds for strengths and weaknesses are starting values, not tuned.
- Reports contain personal hiring data. Access control and retention rules are not built.
- The report is decision support. A human recruiter makes the final decision.