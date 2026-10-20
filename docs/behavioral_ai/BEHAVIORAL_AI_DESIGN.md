# Behavioral AI Design -- Research and Approach (Day 48)

Status: research and design only. Nothing here is implemented.
Related: SIGNAL_TO_SCORE_MAPPING.md, BEHAVIORAL_ANALYSIS_FRAMEWORK.md.

## 1. Purpose
Understand how a candidate engages during a video interview using observable
signals, and give the recruiter neutral context. The system never judges
character, honesty or emotion.

## 2. Design principles
1. Observable only: measure what a camera can see (head direction, gaze direction,
   movement amount). Do not infer emotions, personality, honesty or stress.
2. Context, not decision: behavioral results are shown to the recruiter. Their
   weight in the unified hiring-fit score is 0 by default.
3. Opt-in and no penalty: the candidate can decline, and the interview continues
   without video analysis.
4. Privacy by design: video is processed on the candidate's device. Only numbers
   leave the device. No video or images are stored.
5. Own baseline: compare the candidate with their own first minute, not with a
   population norm.
6. No data is better than bad data: poor lighting or video gives "insufficient
   data", never a score.
7. Human in the loop: a recruiter reviews. No automatic rejection from these signals.

## 3. Signal research
| Signal | How it can be measured | What it can show | What it cannot show | Main confounds |
|---|---|---|---|---|
| Eye movement and gaze stability | Face landmarks with iris tracking (e.g. MediaPipe Face Mesh with iris); gaze direction relative to the screen | Share of time looking at the screen; how often gaze shifts | Honesty, lying, interest | Camera position, glasses, reading notes, eye conditions, cultural norms about eye contact |
| Head movement | Head pose from face landmarks (yaw, pitch, roll) | Facing the screen; turning away; head motion amount | Attitude or confidence | Camera angle, seating, neck conditions, head coverings affecting landmarks |
| Facial engagement | Face presence in frame and face orientation toward the camera. No expression classes | Candidate is present and facing the screen | Emotion, enthusiasm, anxiety | Lighting, skin-tone detection accuracy, bandwidth, face partly hidden |
| Attention patterns | Combine gaze, head pose and response latency (time from question end to answer start) | When the candidate looked away or paused | Why they looked away | Thinking pauses, interruptions at home, hearing or processing differences |
| Movement (gestures) | Pose landmarks; motion amount of head, shoulders and hands compared with own baseline | Amount of movement | Nervousness, stress | Habits, disability, chair, camera framing |

## 4. What is deliberately excluded
- Facial expression or emotion classification (happy, angry, anxious).
- Personality, honesty or "lie detection" claims.
- Face recognition or identity matching.
- Storing video or images.
- Any use as an automatic reject rule.

Reasons:
- The EU AI Act (Article 5(1)(f)) prohibits inferring emotions in the workplace,
  and the Commission's guidelines include recruitment. Recruitment AI is also a
  high-risk category (Annex III). Check the current text and dates before any
  deployment.
- Evidence that gaze or head movement predicts job performance is weak.
- Many harmless differences change these signals: disability, neurodivergence,
  culture, religious head covering, glasses, camera quality, slow internet.

## 5. Non-invasive scoring approach (summary)
1. Candidate consents and can opt out with no penalty.
2. A 60-second calibration records the candidate's own resting posture and movement.
3. Features are computed in the browser from the video, then the video is discarded.
4. Features are grouped into 30-second windows of numbers only.
5. A quality gate rejects poor data.
6. Indicators (focus, distraction, movement) are computed and mapped to neutral
   statements such as "stayed on screen for most of the interview".
7. The recruiter sees a context report. Details: SIGNAL_TO_SCORE_MAPPING.md.

## 6. Fit with the existing system
| Existing practice | Behavioral AI follows it |
|---|---|
| Null means no data, never a fake value | Insufficient data returns null |
| Explanation stored with every score | Every indicator stores a plain explanation |
| Day 7 metadata (model_version, timestamp, stage, status) | Same fields on the record |
| Speech-to-text confidence kept out of the score (Day 43) | Behavioral index kept out of hiring fit by default |
| Human makes the final decision | Same |

## 7. Limitations and open questions
1. Not built. All thresholds are starting values chosen for design, not tuned.
2. No validation yet that these signals relate to anything useful for hiring.
3. Fairness has not been tested. The plan is in BEHAVIORAL_ANALYSIS_FRAMEWORK.md.
4. Legal position differs by country. This is not legal advice.
5. Open decision: whether behavioral results should ever feed the hiring-fit score.
   Default answer in this design: no, until validated and tested for fairness.

