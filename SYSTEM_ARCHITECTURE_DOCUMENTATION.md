# System Architecture Documentation -- Zecpath AI

## 1. Components

| Component | Responsibility |
|---|---|
| Backend / API gateway | Authentication, rate limits, routing, idempotency |
| Resume Parsing service | Extract, clean, segment and parse resumes and JDs |
| ATS Scoring service | Score, rank, shortlist, fairness checks |
| Screening AI service | Question flow, speech-to-text, answer scoring, report |
| Interview Intelligence service | HR interview questions, follow-ups, communication and confidence scoring |
| Behavior Analysis service | Hesitation, stress and integrity signals (text-level only here) |
| Decision and Scoring service | Unified hiring fit and recommendation |
| Storage | Object storage, document database, relational database |
| Queue and workers | Run slow jobs outside the request |
| Observability | Logs, metrics, alerts, audit |

## 2. System diagram

    [Recruiter dashboard / Candidate portal]
                     |  HTTPS + token
                     v
          [Backend / API gateway]
     |        |        |         |         |
     v        v        v         v         v
  Resume     ATS    Screening  Interview  Decision
  Parsing   Scoring    AI       AI         AI
     |        |        |         |         |
     +--------+--------+---------+---------+
              |  signed webhooks back to backend
              v
  [Object storage] [Document DB] [Relational DB + audit log]

## 3. Data pipeline

    Resume file --> text extraction --> cleaning --> section split
        --> skills / experience / education parsing
        --> semantic matching against the job
        --> ATS score --> ranking and zones --> fairness check
        --> eligibility --> screening call --> screening score
        --> HR interview --> HR score
        --> unified hiring fit --> recommendation and report

Every stage writes its output with the Day 7 metadata. Each stage reads
the previous stage's saved output, so a stage can be re-run alone.

## 4. Workflows

### Resume upload (async)
1. Backend stores the file and calls the Resume Parsing API.
2. The API returns 202 with a job_id.
3. A worker runs extraction, parsing and matching.
4. A signed webhook tells the backend the job is done, or the backend polls.

### Screening call (async)
1. Backend enqueues a call request, after checking consent.
2. The call runs. A state machine handles silence, off-topic answers and drops.
3. Speech is transcribed, answers are understood and scored.
4. A recruiter-ready report is stored and a webhook fires.

### Interview turn scoring (sync)
1. Backend sends one answer turn.
2. The service scores relevance, communication and confidence and picks a follow-up.
3. The result returns in the same request.

### Final decision (sync)
1. Backend sends the available round scores.
2. Missing rounds are excluded and their weight is redistributed.
3. The round floor rule applies, then the category and flags are returned.
4. The decision is written to the audit log.

## 5. Communication rules
- REST for anything the caller waits on.
- Queue plus webhook for slow work.
- Retries with backoff only for 429 and 5xx errors. Every POST has an idempotency key.
- Details: AI_INTEGRATION_DOCUMENT.md.

## 6. Design decisions
| Decision | Reason |
|---|---|
| Rule-based logic first | Explainable and needs no labelled data |
| ML only where rules cannot work | Meaning-based matching and speech need trained models |
| Weight redistribution for missing data | Avoids penalising or inventing values |
| Component floor and round floor | A strong part must not hide a weak one |
| Flag for human review, not auto-reject | Fairness and legal risk |
| Stateless services | Allows horizontal scaling |

## 7. Not yet built
Real queue, deployed database, authentication, telephony, video and
computer vision analysis, multilingual support, container deployment.