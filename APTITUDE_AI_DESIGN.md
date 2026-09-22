# Aptitude AI Design -- Zecpath

## Purpose
Adds cognitive and situational judgment evaluation to the HR interview
round (Day 33), distinct from personality/background questions --
this tests reasoning ability and judgment quality, not self-description.

## Question Types

### Logical Reasoning (definite correct answer)
Numerical reasoning, pattern recognition, and verbal/syllogistic
reasoning questions -- each has a known correct answer, scored by
extracting the candidate's stated answer and comparing directly.

### Situational Judgment Scenarios (open-ended)
Realistic workplace scenarios (a reporting error, a missed deadline,
an unsafe deadline pressure) with no single correct answer, but an
"ideal answer structure" -- key reasoning elements a strong response
would touch on.

## Scoring Approach

### Logical Reasoning
Numeric questions: exact-match scoring on the extracted final answer,
with partial credit for a reasoning attempt even if the final number
is wrong. Verbal reasoning: checks whether the candidate's stated
conclusion (yes/no) matches the logically correct one.

### Situational Judgment
Uses keyword-hint proxies mapped to each ideal-answer-structure element
to estimate coverage -- e.g. a response mentioning "risk," "concern," or
"flag" is counted as covering the "communicates the risk clearly" element.
This is a lightweight heuristic, not true semantic understanding of the
response's reasoning quality.

### Problem-Solving Clarity
Separately scored via structural language markers ("first," "then,"
"because," "therefore") -- a proxy for whether the candidate reasoned
through the problem in a structured way, rather than giving an
unstructured, single-statement answer.

## Known Limitations
- Situational judgment scoring is keyword-proxy based, not true semantic
  evaluation -- a well-reasoned answer using different vocabulary than
  the keyword hints could be under-scored. A production system would
  benefit from Day 12's semantic similarity approach applied here instead
  (comparing response embeddings against ideal-answer embeddings).
- Logical reasoning questions currently have a small, fixed bank (3
  questions) -- would need significant expansion and difficulty tiers
  for real production use, distinct per role and seniority (mirroring
  Day 33's branching pattern).
- No adaptive difficulty yet -- Day 34's follow-up engine could be
  extended to this question type in future work.