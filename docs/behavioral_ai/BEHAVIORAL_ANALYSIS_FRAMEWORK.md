# Behavioral Analysis Framework (Day 48)

## 1. Pipeline
```
Consent screen
   |  declined -> interview continues, no video analysis, no penalty
   v
60-second calibration (own resting posture, movement, screen region)
   v
Capture on candidate's device (browser)
   v
Feature extraction on device (face, head angle, gaze, motion)
   v
Video discarded. Only numbers leave the device
   v
30-second windows of numbers
   v
Quality gate (60 percent valid frames, 5 minutes)
   |  failed -> null result "insufficient video data"
   v
Indicators: focus, distraction, movement restlessness
   v
Neutral insight statements + engagement context index
   v
Recruiter context report (weight in hiring fit = 0 by default)
   v
Human review, then retention and deletion rules
```

## 2. Stage rules
| Stage | Rule |
|---|---|
| Consent | Clear plain-language notice: what is measured, what is not, how long numbers are kept. Opt-out has no penalty |
| Calibration | One minute at the start of the introduction. Used for baseline only |
| Capture | Processed in the browser. No upload of video |
| Quality gate | Valid frames below 60 percent or under 5 minutes gives null |
| Indicators | Formulas in SIGNAL_TO_SCORE_MAPPING.md |
| Report | Neutral wording only. Forbidden words listed in the mapping document |
| Review | Recruiter reads the report with the transcript and scores. No automatic decision |
| Retention | Numbers only. Deleted after the retention period set by policy (to be decided) |

## 3. Fairness testing plan (before any use)
Test the feature extraction and the indicators on varied simulated and consented test video:
- different skin tones and lighting levels
- glasses, head coverings, beards
- different camera heights and angles
- low-bandwidth and low-resolution video
- candidates reading notes versus not
- people with different movement and gaze habits

Checks:
1. Face detection rate is similar across groups. If not, the quality gate must treat
   this fairly. Otherwise the feature is not used.
2. Indicator distributions are compared across groups. A large gap means the signal
   is measuring something other than engagement.
3. Validity check: do the indicators relate to structured human ratings of
   interview quality? If there is no relationship, they stay as context only.

## 4. Human oversight
- Behavioral results are never the sole reason for any decision.
- The recruiter sees the explanation and the quality information.
- The recruiter can mark a result as unreliable. Those marks are logged and reviewed.

## 5. Rollout phases
| Phase | What happens |
|---|---|
| 1. Research (now) | This design |
| 2. Prototype | Compute indicators offline on consented test video, no scoring |
| 3. Fairness and validity testing | The tests in section 3 |
| 4. Pilot | Optional, opt-in, context report only, weight 0 |
| 5. Decide | Whether any use in scoring is justified |

If fairness or validity tests fail, the feature stays out of scoring or is removed.

## 6. Reuse of existing modules
| Need | Existing piece |
|---|---|
| Response latency | pause and repetition detector |
| Text-based hesitation signals | confidence and stress analyser |
| Score record and explanation style | HR scoring engine pattern |
| Metadata fields | Day 7 standard |
| API style | HR API pattern |

## 7. Limits
1. Design only. No code written.
2. Thresholds are untuned.
3. Legal review needed before any deployment.
4. Camera-based signals can reflect the environment, not the person.