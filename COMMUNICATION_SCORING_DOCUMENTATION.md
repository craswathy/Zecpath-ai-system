# Communication Scoring Formula Documentation -- Zecpath

## Formula
Final Communication Score (0-100) = 
  (Fluency x 0.30) + (Grammar x 0.25) + (Vocabulary x 0.20) + (Clarity x 0.25),
  scaled to 0-100.

## Component Definitions

### Fluency (30%)
Combines sentence continuity (are thoughts completed, not trailing off
mid-sentence) with filler-word penalty. Measured on the RAW transcript
(before Day 23's cleanup removes fillers), since cleanup would hide
exactly the signal this component needs.

### Grammar (25%)
Uses LanguageTool to count grammar issues, converted to an error-rate-based
score (fewer errors per word = higher score). Measured on normalized text.

### Vocabulary (20%)
Type-token ratio (unique words / total words) -- rewards varied word
choice over repetitive phrasing. Most reliable on longer answers.

### Clarity (25%)
Combines answer structure (does the response have at least an opening
and supporting statement) with filler-word density penalty.

## Bias Reduction Measures
1. **Score normalization** across a candidate pool (min-max), consistent
   with Day 15's fairness pattern -- prevents one strict/lenient scoring
   pass from skewing relative comparisons.
2. **Short-answer leniency flag** -- answers under 8 words are flagged
   as unreliable for grammar assessment (error rate per word is noisy
   at very short lengths) rather than penalized outright.
3. **No native-speaker assumption baked in** -- scoring is based on
   grammatical correctness and structure, not accent, vocabulary
   "sophistication," or native-speaker idiom use, to avoid penalizing
   non-native English speakers unfairly (ties to PRD's multilingual
   candidate base).

## Known Limitations
- LanguageTool is a rule-based grammar checker, not a trained language
  model -- may flag stylistic choices as "errors" or miss genuinely
  awkward phrasing that isn't a strict grammar violation.
- Vocabulary scoring (type-token ratio) is a simple proxy, not true
  semantic vocabulary sophistication assessment.
- All testing here uses Day 23's small demo transcript (3 turns) --
  needs validation against a larger, more diverse response set.