# Signal-to-Score Mapping Model (Day 48)

All numbers are starting values for design. Not tuned. Not implemented.

## 1. Raw signals (per video frame, computed on the candidate's device)
| Signal | Meaning |
|---|---|
| face_present | A face is detected with confidence 0.5 or higher |
| head_facing | Head angle within limits: yaw within 25 degrees and pitch within 20 degrees |
| gaze_on_screen | Gaze direction falls inside the calibrated screen region |
| motion_energy | Average speed of head and shoulder landmarks |

A frame is valid when face_present is true.
A frame is focused when face_present, head_facing and gaze_on_screen are all true.

## 2. Indicators
| Indicator | Definition | Score (0 to 1) |
|---|---|---|
| Focus level | focused frames divided by valid frames | the same value |
| Distraction frequency | away events per 10 minutes | 1 minus min(events / 6, 1) |
| Movement restlessness | motion_energy divided by the candidate's own baseline motion_energy | 1 minus min(max(ratio minus 1, 0) / 2, 1) |

Away event: a continuous period of 3 seconds or more where the frame is not
focused. Ignore the first 3 seconds after a question ends (thinking time).
Glances under 3 seconds are ignored.

Sub-signals shown to the recruiter but not scored: gaze stability (share of time
gaze is on screen) and head stability (share of time head is within limits).

## 3. Quality gate (checked first)
Produce a score only when both are true:
- valid frames are at least 60 percent of all frames
- at least 5 minutes of video were analysed

Otherwise the result is null with the explanation "insufficient video data".

## 4. Engagement context index
Index = (0.5 x focus + 0.3 x distraction score + 0.2 x movement score) x 100

| Index | Label |
|---|---|
| 75 or above | High observed engagement |
| 50 to below 75 | Moderate observed engagement |
| below 50 | Low observed engagement |

Weight of this index in the unified hiring-fit score: 0 by default (configurable
later, only after validation and fairness testing).
Label wording says "observed", because it describes camera signals, not the person.

## 5. Mapping signals to neutral insights
| Condition | Recruiter-facing statement |
|---|---|
| Focus 0.8 or above | Stayed oriented toward the screen for most of the interview |
| Focus 0.5 to 0.8 | Looked away from the screen at times |
| Focus below 0.5 | Spent a large share of the interview looking away from the screen. Check for a technical or environmental cause before drawing any conclusion |
| Distraction 0 to 2 events per 10 min | Few interruptions in attention |
| Distraction 6 or more per 10 min | Frequent breaks in attention. Check for interruptions at home or camera position |
| Movement ratio 1 or below | Movement similar to the candidate's own baseline |
| Movement ratio 3 or above | Much more movement than at the start |
| Quality gate failed | No behavioral result. Video quality was too low |

Never used in a statement: nervous, anxious, dishonest, uninterested,
unprofessional, confident, stressed.

## 6. Worked examples
Example A (normal interview): focus 0.82, 2 away events per 10 min, movement ratio 1.4.
- Distraction score = 1 minus 2/6 = 0.67
- Movement score = 1 minus (1.4 minus 1)/2 = 0.80
- Index = (0.5 x 0.82 + 0.3 x 0.67 + 0.2 x 0.80) x 100 = about 77, High observed engagement.

Example B (poor video): valid frames are 45 percent. Quality gate fails.
Result is null: "insufficient video data". No score, no penalty.

Example C (candidate reads from notes): focus 0.40, movement ratio 1.0.
Index is low, but the report says only that the candidate looked away often.
The recruiter decides whether that matters. It is not treated as misconduct.

## 7. Record format (follows Day 7 metadata)
```
{
  "candidate_id": "cand_00123",
  "interview_id": "hrint_0001",
  "metadata": {"model_version": "behavior_v0.1", "timestamp": "...", "stage": "behavior_scored", "status": "complete"},
  "quality": {"valid_frame_share": 0.91, "minutes_analysed": 18.5, "gate_passed": true},
  "indicators": {"focus": 0.82, "distraction_events_per_10min": 2, "movement_ratio": 1.4},
  "index": 77.0,
  "label": "High observed engagement",
  "weight_in_hiring_fit": 0.0,
  "explanation": "Focus 0.82 | distraction score 0.67 | movement score 0.80"
}
```
Only these numbers are stored. No video, no images.