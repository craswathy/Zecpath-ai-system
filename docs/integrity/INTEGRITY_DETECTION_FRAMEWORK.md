# Integrity Detection Framework (Day 49)

Status: design only. Nothing here is implemented.
Related: MALPRACTICE_DETECTION_LOGIC.md, RISK_FLAGGING_SYSTEM_DESIGN.md,
and the Day 48 documents in docs/behavioral_ai/.

## 1. Purpose
Detect signs of possible external help during an interview and give the recruiter
a prioritised list to review. The system flags. A human decides.

## 2. Principles
1. Flag for review, never accuse. A flag is not proof of cheating.
2. No automatic rejection, no automatic interview end.
3. Minimal data: record event types, times and durations. Not screens, not typing,
   not browsing history, not room video.
4. Tell the candidate before the interview what is monitored and why.
5. No data is better than bad data: weak signals become null, not guesses.
6. Every flag stores a plain explanation and can be reviewed and contested.
7. Same design rules as the HR module: null means no data, explanation with every
   result, human makes the final decision.

## 3. Malpractice signals
| Signal | How it can be detected | What it may indicate | Innocent causes |
|---|---|---|---|
| Tab switching frequency | Browser visibility events: interview tab becomes hidden | Looking something up in another tab | Accidental click, notification, system pop-up, phone call on mobile, device sleep |
| Loss of screen focus | Window loses focus while the tab stays visible; fullscreen exited | Using another app or window | Chat or system pop-up, second monitor click, screen reader or assistive tool |
| External voice detection | Voice activity plus speaker change detection on the audio. A second distinct voice while the candidate answers | Being prompted by another person | TV, family member, street noise, an interpreter or assistant the candidate has arranged, echo |
| Repeated looking away | Day 48 away events: head or gaze off screen for 3 seconds or more | Reading from another source | Thinking, notes allowed by the interviewer, camera position, glasses, habit, cultural norms |

## 4. Signals deliberately not used
- Screen recording, screenshots, browsing history, keystroke logging.
- Room scans or 360 degree video.
- Face recognition or identity matching beyond what the platform already does.
- AI-written-text detectors on answers (unreliable, and known to misflag
  non-native English writing).
- Emotion or "nervousness" inference (see Day 48).
- Network or device fingerprinting beyond normal security.

## 5. What this system cannot see
- A second device (phone, tablet) in the room.
- A person who stays silent, or whispers below detection.
- Notes placed next to the camera line of sight, if the candidate reads without a clear head turn.
- Any content of other applications.
So a "Clear" tag means "no signals seen", never "no help was used".

## 6. Detection flow
```
Consent and notice (what is monitored, what is not)
   v
Capture event data during the interview
   - browser: tab hidden, window blur, fullscreen exit (timestamps)
   - audio: voice activity and speaker-change events (timestamps, no extra recording)
   - video: Day 48 away events (only if the candidate consented to video analysis)
   v
Quality checks per signal (low quality -> null)
   v
Event filtering (ignore very short events)
   v
Threshold severity per signal (0 to 3)
   v
Pattern checks (co-occurrence, timing after questions, prompting)
   v
Risk points -> review priority tag
   v
Alerts (candidate reminder, recruiter alert at high priority)
   v
Recruiter review, decision, audit log
```

## 7. Integration with behavioral signals (Day 48)
| Point | Rule |
|---|---|
| Shared signal | Day 48 away events feed the "repeated looking away" signal. They are not counted twice |
| Quality gate | Video signals are used only when the Day 48 quality gate passed. Otherwise that signal is null |
| Engagement index | The Day 48 engagement context index is NOT used for integrity. Only away events and their timing are |
| Consent | One notice covers both. A candidate who declines video analysis still has browser and audio signals, if they accepted those |
| Hiring fit | Neither integrity tags nor behavioral results change the unified hiring-fit score by default |

## 8. Fit with the rest of the system
| Existing practice | Used here |
|---|---|
| Null means no data | Unavailable signals are null |
| Explanation stored with every result | Every flag stores why |
| Day 7 metadata | Same fields on the integrity record |
| Follow-up engine | Suggests verification follow-up questions for flagged interviews |
| Technical scoring depth detector (Day 47) | Helps the recruiter see whether answers hold up in follow-ups |

## 9. Limits and open decisions
1. Not built. Thresholds are untuned starting values.
2. Fairness and false-positive rates are unknown until tested (see the risk flagging document).
3. Legal position differs by country. Recruitment AI is regulated in some places, so
   get a legal check before any deployment. This is not legal advice.
4. Open decision: may integrity monitoring be required for certain roles, or must an
   alternative (for example an in-person interview) always be offered?

