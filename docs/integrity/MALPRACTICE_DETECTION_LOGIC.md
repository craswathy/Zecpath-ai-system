# Malpractice Detection Logic (Day 49)

All numbers are starting values for design. Not tuned. Not implemented.

## 1. Event definitions
| Event | Definition | Ignored when |
|---|---|---|
| Tab event | Interview tab hidden | Shorter than 2 seconds |
| Focus-loss event | Window loses focus while the tab stays visible, or fullscreen is exited | Shorter than 2 seconds. Also not counted if it overlaps a tab event within 1 second (counted once, as a tab event) |
| Voice event | A second distinct voice is detected while the candidate's mic is open | System audio such as the interview's own question audio. Speaker-separation confidence below 0.7 |
| Away event | Day 48 away event: not focused for 3 seconds or more | First 3 seconds after a question ends (thinking time) |

## 2. Threshold-based flags (severity 0 to 3)
| Signal | Measure | 0 none | 1 low | 2 medium | 3 high |
|---|---|---|---|---|---|
| Tab switching | tab events per 10 minutes | below 0.5 | 0.5 to below 1.5 | 1.5 to below 3 | 3 or more |
| Loss of focus | share of interview with window unfocused | below 2% | 2% to below 5% | 5% to below 10% | 10% or more |
| External voice | seconds with a second voice during answers | below 3 s | 3 to below 10 s | 10 to below 30 s | 30 s or more, or 3 or more separate episodes |
| Looking away | away events per 10 minutes | below 2 | 2 to below 4 | 4 to below 6 | 6 or more |

## 3. Pattern recognition
Patterns need a minimum of 3 questions answered. They add risk points because
combined signs are more informative than a single one.

| Pattern | Rule | Why it matters | Bonus |
|---|---|---|---|
| P1 Co-occurrence | 2 or more different signals with severity 1 or more fall inside the same 60-second window | A lookup usually shows up in more than one signal at once | +2 |
| P2 Question-linked timing | A tab, focus-loss or away event starts within 5 seconds after a question ends, for at least half of the questions | Looking something up right after each question, instead of random interruptions | +2 |
| P3 Prompting | A second voice is heard, then the candidate starts answering within 10 seconds, on 2 or more questions | Possible prompting | +3 |

## 4. Risk points and review priority
Risk points = sum of the four severities + pattern bonuses.

| Points | Review priority |
|---|---|
| 0 to 1 | No concern |
| 2 to 3 | Low |
| 4 to 6 | Medium |
| 7 or more | High |

Extra rule: any single signal at severity 3 sets the priority to at least Medium.

## 5. Quality gate and missing data
- Interview shorter than 5 minutes: rates are not computed. Result is "insufficient data".
- A signal with low quality or no consent is null, not 0.
- If fewer than 2 of the 4 signals have data: result is "insufficient data".
- If 2 or 3 signals have data: priority is computed from those, and the record says
  which signals were missing. Maximum possible points shrink, so say so in the explanation.

## 6. Worked examples
Example A (18-minute interview): 3 tab events (1.67 per 10 minutes, severity 2),
focus loss 1% (0), no second voice (0), 3 away events per 10 minutes (1).
Points = 3. No pattern. Priority: Low.

Example B (18-minute interview): 5 tab events (2.8 per 10 min, severity 2),
second voice for 12 seconds (2), 4.5 away events per 10 minutes (2), focus loss 1% (0).
Events start within 5 seconds after the question ends on 5 of 8 questions (P2, +2).
Points = 2 + 2 + 2 + 0 + 2 = 8. Priority: High. Recruiter gets a review alert.

Example C (notification pop-ups): 4 pop-ups lasting 1 second each. All are shorter
than 2 seconds, so they are ignored. Priority: No concern.

Example D (camera blocked): video gate fails, so looking away is null. Tab and
focus are 0, voice is 0. Three signals have data, so priority is No concern, with the
note "looking-away signal unavailable". It does not mean "no help was used".

## 7. Record format (Day 7 metadata)
```
{
  "candidate_id": "cand_00123",
  "interview_id": "hrint_0001",
  "metadata": {"model_version": "integrity_v0.1", "timestamp": "...", "stage": "integrity_scored", "status": "complete"},
  "signals": {
    "tab_switching": {"severity": 2, "value": 2.8, "unit": "events_per_10min"},
    "focus_loss": {"severity": 0, "value": 0.01, "unit": "share_of_interview"},
    "external_voice": {"severity": 2, "value": 12, "unit": "seconds"},
    "looking_away": {"severity": 2, "value": 4.5, "unit": "events_per_10min"}
  },
  "patterns": ["P2"],
  "risk_points": 8,
  "review_priority": "High",
  "missing_signals": [],
  "weight_in_hiring_fit": 0.0,
  "explanation": "Tab 2 | focus 0 | voice 2 | away 2 | P2 +2 = 8"
}
```
Stored: event types, times, durations, severities. Not screens, not typed text,
not extra recordings.