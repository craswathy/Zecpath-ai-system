# HR Interview Flow Design -- Zecpath

## Conversation Phases

1. **Introduction** -- Self-introduction question(s) only, warm-up phase.
2. **Core HR Questions** -- Career journey, strengths & weaknesses,
   teamwork & culture fit -- the bulk of the interview.
3. **Role-Based Evaluation** -- Career goals, availability & commitment --
   role/seniority-specific closing assessment questions.
4. **Closing** -- Wrap-up, thank candidate, explain next steps.

## Role-Based Question Branching
- **Fresher vs Experienced**: Career Journey questions differ entirely
  (project/coursework focus for freshers, transition/growth focus for
  experienced candidates). Availability questions about notice period
  only apply to experienced candidates.
- **Technical vs Non-Technical**: An extra Teamwork question specific to
  cross-functional collaboration (with designers/PMs) is added for
  technical roles only.

## Interview State Structure
Each interview session tracks:
- `question_id` -- links back to the question bank
- `response_text` -- captured answer (post Day 24 STT + Day 23 normalization)
- `is_follow_up` -- whether this response was to a dynamic follow-up
  rather than the original scripted question
- `follow_up_eligible` -- a per-question flag; not every question invites
  adaptive follow-up (PRD Phase 15) -- factual questions like "notice
  period" don't need follow-up, open-ended ones like "self-introduction" do.

## Relationship to Day 22/29 Screening System
This HR interview stage is a distinct, later round from Day 22's initial
screening call -- reuses the same architectural patterns (question bank
+ state machine) established there, but with its own phase structure and
role-based branching logic, since HR interview questions are deeper and
more conversational than initial screening's fact-gathering questions.