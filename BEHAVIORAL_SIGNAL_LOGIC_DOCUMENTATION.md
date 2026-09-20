# Behavioral Signal Logic Documentation -- Zecpath

## Relationship to Day 27
This extends Day 27's confidence/sentiment analysis rather than
replacing it. Day 27 already covers: hesitation markers (um, uh, "I
think"), speaking pace, explicit uncertainty phrases, and VADER-based
sentiment. Day 36 adds three new signals not previously captured:
long-pause estimation, literal word-repetition (stuttering), and
cross-answer contradiction detection.

## New Signals

### Long Pause Detection
Estimated by comparing a turn's actual duration against the expected
duration for that word count at a normal speaking rate (2 words/second).
**Limitation**: this is a turn-level proxy, not true pause detection --
Whisper's basic transcription (Day 24) doesn't provide word-level
timestamps, which would be needed for precise pause localization.

### Repeated Words (Stutter Pattern)
Detects literal word repetition (e.g. "I I I have") via regex, distinct
from Day 27's filler-word detection -- this catches speech restarts,
not filler insertions.

### Contradiction Detection
Generalizes Day 26's single-purpose experience-consistency check into a
reusable scan across a candidate's full answer history for any
extracted field, checking all pairs of answers (not just adjacent ones)
for numeric or categorical conflicts.

## Stress Score Formula
Stress Score (0-1) = weighted combination of:
hesitation (25%) + long pause (20%) + repetition (20%) +
negative sentiment (15%) + contradiction (20%)

## Behavioral Confidence Score
Final Score (0-100) = Day 27's base confidence, reduced proportionally
by the stress score. A candidate can have clear, correct content but
still show elevated stress signals -- this is surfaced as a separate
data point for human review, not used to penalize the ATS/screening
score directly.

## Important Caveat
Stress and hesitation signals should NOT be treated as indicators of
poor candidate quality on their own -- nervousness during an AI-conducted
interview is common and not necessarily predictive of job performance.
These signals are intended to give recruiters additional context, not
to auto-reject or auto-penalize candidates (consistent with Day 15's
fairness principle: flag for review, don't auto-decide).