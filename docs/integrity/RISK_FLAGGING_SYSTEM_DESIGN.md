# Risk Flagging System Design (Day 49)

## 1. Real-time alerts

### To the candidate (gentle, never accusing)
| Trigger | Message | Action |
|---|---|---|
| First tab or focus-loss event | "The interview window lost focus. Please stay on this window." | Notice only |
| Third tab or focus-loss event in 10 minutes | "Focus changes are being recorded for the recruiter to review." | Notice only |
| Second voice detected | "We heard another voice. If someone else is in the room, please ask them to step out." | Notice only |
| Any notice | Button: "That was a mistake or a technical issue", plus a short note | Logged with the timestamp and shown to the recruiter |

Rules: wording is neutral. No automatic end of the interview. No notice about
looking away, because that signal is too ambiguous to warn about in real time.

### To the recruiter (silent)
| Trigger | Alert |
|---|---|
| Risk points reach High during the interview | "Review recommended: [signals and times]". The AI interview continues |
| Candidate presses "mistake or technical issue" | Shown beside the matching event |

The recruiter can message the candidate, add a verification question, or only note it
for the final review.

## 2. Interview risk tagging
| Tag | Meaning | Suggested handling |
|---|---|---|
| No concern | No signals, or only ignorable events | Normal review |
| Low | A few weak signals | Read the timeline if time allows |
| Medium | Several signals or one strong signal | Review the timeline. Consider verification follow-up questions |
| High | Strong or combined signals | Review before any decision. Consider a short live follow-up interview |
| Insufficient data | Not enough usable signals | No conclusion. Say so |

The tag is "review priority". The words cheating, fraud or dishonest are never used.

## 3. Recruiter review screen (design)
1. Tag, risk points, and the plain explanation.
2. Timeline of events with time, type, duration, and the question being answered.
3. Candidate notes from the "mistake or technical issue" button.
4. Missing signals and data-quality notes.
5. Suggested verification follow-ups (see section 4).
6. Decision options: No concern, Ask verification question, Schedule short live follow-up,
   Escalate to a human panel. Every decision needs a written reason.

## 4. Verification follow-ups
For Medium and High tags, the follow-up engine suggests asking the candidate to
explain an earlier answer in their own words, or to apply it to a new case.
The technical depth detector (Day 47) helps the recruiter compare the first answer
with the follow-up. A gap is a reason to look closer, not proof.

## 5. Fairness and accessibility
| Risk | Mitigation |
|---|---|
| Assistive tools such as screen readers change window focus | Accommodation request. Details of any condition are not stored. Thresholds ignored for that candidate |
| Shared or noisy homes, an interpreter, a family member | Voice threshold has a margin. Recruiter can mark "approved assistance" |
| Poor internet, reconnects, device sleep | Short events ignored. Quality gate. Reconnect events are labelled as technical |
| Camera angle, lighting, glasses, head covering | Day 48 quality gate. Looking-away signal becomes null if video is poor |
| Culture and habits (gaze, thinking by looking away) | First 3 seconds after a question ignored. Looking away alone is never enough for High |
| Different false-flag rates between groups | Fairness test before any use (section 7) |

## 6. Candidate rights and audit
- Notice before the interview of what is monitored and what is not.
- The candidate can add an explanation during the interview, or contest afterwards.
- Every flag, alert, recruiter decision and reason is logged.
- A recruiter can mark a flag as wrong. Wrong flags are reviewed to improve thresholds.
- Retention: event records only, for a period set by policy (to be decided).

## 7. Testing before use
1. Simulated sessions: normal, notifications, noisy room, screen reader, real lookup behaviour.
2. Measure false-flag rate and missed-lookup rate per signal.
3. Compare false-flag rates across lighting, camera, accessibility and network conditions.
4. Check that thresholds do not push one group into higher tags without a valid reason.
5. If false flags are high, raise the thresholds or drop the signal.

## 8. Rollout phases
| Phase | What happens |
|---|---|
| 1. Design (now) | These documents |
| 2. Prototype | Record events only, no tags, no alerts |
| 3. Offline tagging | Compute tags on test sessions. Check false flags |
| 4. Pilot | Recruiter-only tags, no candidate alerts |
| 5. Candidate alerts | Only after the pilot shows low false flags |
| 6. Review | Decide whether to keep, tune or remove signals |

## 9. Limits
1. Design only. No code written.
2. Thresholds are untuned.
3. A second device or a silent helper is invisible to the system.
4. A tag is a reason to look, not evidence.
5. Legal check needed before deployment.