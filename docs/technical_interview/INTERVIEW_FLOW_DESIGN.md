# Interview Flow Design (Day 46)

## States
```
SETUP
  |
INTRODUCTION
  |
EXPERIENCE QUESTIONS
  |
CONCEPTUAL QUESTIONS
  |
SCENARIO PROBLEMS
  |
CLOSING
  |
SCORING
  |
REPORT READY
  |
ENDED

Any question phase --(timeout or candidate left)--> ABANDONED --> SCORING (partial, low reliability)
```

## Question loop inside each phase
```
Pick question --> Ask --> Get answer --> Clean text --> Score answer
      ^                                                      |
      |                              good: level up, weak: level down, else same
      |                                                      |
      |                                          Follow-up allowed? yes --> ask follow-up
      |                                                      | no
      +---------- more questions in phase? yes <-------------+
                                          no --> next phase
```

## Transitions
| From | To | When |
|---|---|---|
| SETUP | INTRODUCTION | profile loaded, consent confirmed |
| INTRODUCTION | EXPERIENCE | introduction answered |
| EXPERIENCE | CONCEPTUAL | experience question quota done |
| CONCEPTUAL | SCENARIO | conceptual quota done |
| SCENARIO | CLOSING | scenario quota done |
| CLOSING | SCORING | wrap-up done |
| SCORING | REPORT READY | scores computed |
| REPORT READY | ENDED | sent to recruiter |
| any question phase | ABANDONED | timeout or candidate left |

## Rules
1. Phases only move forward.
2. Max 2 follow-ups per question, 6 per interview.
3. Never repeat a question.
4. Partial interview still scored, flagged low reliability.