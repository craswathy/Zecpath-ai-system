# Edge Case & Failure Handling Documentation -- Zecpath

## Overview
Extends Day 24 (STT quality) and Day 29 (conversation retry logic) to
handle messier real-world conditions: poor audio, language mixing,
missing answers, and technical call failures.

## Edge Cases Handled

### Poor Audio Quality
**Detection**: Low STT confidence (<0.4), empty transcription despite
audio signal, or excessive word repetition (a common Whisper artifact
on garbled/noisy audio).
**Response**: Ask the candidate to move to a quieter space and repeat.

### Language Mixing (Code-Switching)
**Detection**: Heuristic pattern matching for choppy, fragment-like text
that often results when a candidate mixes languages mid-answer and the
STT engine (tuned for one primary language) partially garbles the
non-English portions.
**Response**: Politely ask the candidate to continue in English.
**Limitation**: This is a heuristic, not true language identification --
a production system would benefit from per-word language detection.

### Missing Answers
**Detection**: No text captured at all (distinct from a vague/off-topic
answer, which Day 25 already handles -- this is total silence or
capture failure).
**Response**: Retry up to a configured limit, then mark unanswered
rather than looping indefinitely.

### Background Noise
**Detection**: Overlaps significantly with "poor audio quality" above --
background noise typically manifests as reduced STT confidence and
increased transcription artifacts, so it's handled by the same detection path.

### Call Technical Failures (Dropped Calls)
**Detection**: Explicit call_status signal.
**Response**: End the call gracefully and flag for reschedule, distinct
from a candidate simply not answering a question.

## Safety Fallback Priority
When multiple issues could apply to one turn, `diagnose_turn()` checks
them in a fixed priority order (technical failure > audio quality >
language mixing > missing answer > off-topic > vague) so the system
always reacts to the most severe underlying problem first, rather than
getting confused by overlapping symptoms.

## Retry Limits and Escalation
All fallback paths respect a shared retry limit. Once exhausted, the
system escalates to human review rather than either (a) looping forever
or (b) silently failing the candidate -- this directly extends Day 30's
"reduce false rejections" goal into the audio/language edge cases
specifically.

## Known Limitations
- Language mixing detection is heuristic/pattern-based, not validated
  against real multilingual audio samples (would need real Malayalam/
  Hindi/Tamil code-switched recordings to properly validate, per PRD
  Phase 4's multilingual requirement).
- All testing here uses simulated STT results, not live noisy audio --
  Day 24's 4 real test clips remain the only real-audio validation done.