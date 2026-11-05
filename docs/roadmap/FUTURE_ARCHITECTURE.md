# Future Architecture Ideas (Day 58)

Status: proposal. Related: AI_ROADMAP.md, INNOVATION_PROPOSAL.md,
docs/governance/SECURITY_FRAMEWORK.md.

## 1. Today
```
Python modules in ats_engine/  (parsing, scoring, decision, report, governance)
        |
Demo runners and a FastAPI stub (interviews held in memory)
        |
JSON and text files as storage
```
Strengths: simple, rule-based, tested, explainable.
Limits: one process, no login, no persistence, no queues, no shared storage.

## 2. Target picture (a modular system, services split only when needed)
```
 Candidate web app    Recruiter console    Analytics dashboard    Practice (coaching) app
        \                   |                      |                     /
                    API gateway (login, limits, one error format)
                                   |
   +-------------+-----------+-----+------+-------------+--------------+
   | Interview   | Scoring   | Decision   | Report      | Coaching     |
   | service     | service   | service    | service     | service      |
   +-------------+-----------+-----+------+-------------+--------------+
        |  Consent and rights service  |  Audit service  |  Analytics service
                                   |
              Message queue (speech to text, code runs, report building)
                                   |
        Sandbox workers   Model workers (speech, semantic matching)
                                   |
   Relational database    Encrypted object store     Append-only audit store
   (sessions, scores,     (transcripts, reports)     (hash chain, hash saved
    decisions, consent)                                outside the system)
                                   |
   Config and model registry  |  Monitoring and tracing  |  Secret store
```
The coaching service uses its own data store, with no link to hiring data.

## 3. Components
| Component | Job | Starting point today | Change needed |
|---|---|---|---|
| API gateway | Login, rate limits, one error format | hr_api_server.py stub | Real authentication, MFA for staff |
| Interview service | Questions, phases, follow-ups | Interview state and follow-up modules | Save sessions in a database |
| Scoring service | HR, technical and machine test scoring | Scoring modules | Package as a library and a service |
| Decision service | Five-round score and decision | unified and decision modules | Same code, versioned |
| Report service | Recruiter report and exports | Report generator | Store reports encrypted |
| Coaching service | Practice interviews and feedback | Question and scoring modules | Separate data, separate consent |
| Consent and rights service | Consent records, access, erasure | governance_controls.py | Real service and workflow |
| Audit service | Append-only log | AuditLog class | Durable store, outside hash anchoring |
| Analytics service | Aggregates for the dashboard | Stored JSON | Event feed, aggregate tables, small-group hiding |
| Queue and workers | Slow jobs | None | Add queue, sandbox and model workers |
| Model registry and config | Versions of weights and thresholds | Config files | Registry with approval and rollback |

## 4. Main data flows
1. Interview flow: candidate answer, interview service, scoring service, decision service, report service. Each step writes an audit entry. Slow steps (speech, code runs) go through the queue.
2. Coaching flow: candidate, coaching service, coaching store. No path to the hiring stores.
3. Analytics flow: score and decision events go to an aggregate store. No transcript text. Dashboard reads only aggregates.
4. Rights flow: candidate request, rights service, deletion jobs across stores, deletion logged without content.

## 5. Scaling
- Keep API workers stateless behind a load balancer, so any worker can serve any request.
- Put slow work (speech to text, code runs, report building) on a queue and scale workers by queue length.
- Keep models loaded in long-running workers. Loading time, not scoring, is the real delay.
- Cache question banks and configuration.
- Index the database for lookups by candidate, job and time.
- Isolate each client (tenant) logically, and physically if needed.
- Measure first: set load targets after a real pilot, then test.

Start as a modular monolith (one deployable program with clear modules). Split into
services only when load, team size or isolation needs it.

## 6. AI layer
| Part | Technique | Rule |
|---|---|---|
| Scores and decisions | Rules and formulas | Always. Explainable and testable |
| Speech to text | Learned model (Whisper) | Confidence used only as a reliability flag |
| Semantic matching | Learned embeddings | Helps matching, never decides alone |
| Optional text generation (language model) | For phrasing feedback and drafting questions | Never scores, never decides, human review before use |

Guardrails for any language model:
1. Candidate text is untrusted input. It can try to give the model instructions (prompt injection). Keep it separate from instructions and treat the output as untrusted too.
2. No personal data beyond what the task needs.
3. Log prompts and outputs without personal content, with the model version.
4. Check outputs against rules (no scores, no thresholds, no emotion words) before showing.
5. A person reviews text sent to candidates in the hiring context.
6. Decide between a vendor and a self-hosted model on privacy, cost and legal grounds.

## 7. Privacy and security by design
- Video features, if ever built, run on the candidate's device. Only numbers leave it.
- Encryption at rest and in transit. Keys in a key management service.
- Consent checked by the consent service on every access.
- Retention jobs run on schedule and log each deletion.
- Access control moves from the reference module to a central service.
- The audit log hash is saved outside the system.

## 8. Evaluation and monitoring
- Keep reference sets with recruiter labels, and a holdout set that is never used for tuning.
- Run new model or threshold versions in shadow mode first (score, but do not use).
- Release gradually (canary), with one-step rollback.
- Watch for drift: score distributions, deferral rate, override rate, failure rate.
- Alert on sudden changes, and on checks that fail (audit chain, retention).

## 9. Migration path
| Step | Change | Roadmap phase |
|---|---|---|
| 1 | Save interviews in a database. Add real login | 0 |
| 2 | Encrypted stores, consent and rights workflow | 0 and 1 |
| 3 | Package scoring and decision as a library, keep the API thin | 1 |
| 4 | Analytics event feed and dashboard v1 | 1 and 2 |
| 5 | Coaching service with its own store | 2 |
| 6 | Queue and model workers, registry, shadow testing | 3 |
| 7 | Multi-tenant isolation, client API | 3 |
| 8 | Optional video features and language-model help, with guardrails | 4 |

## 10. Trade-offs and alternatives
| Choice | Option A | Option B | Suggested |
|---|---|---|---|
| Structure | Modular monolith | Many services | Monolith first |
| Scoring | Rules | Trained models | Rules. Trained models only if they beat rules on real data and stay explainable |
| Hosting of models | Vendor | Self-hosted | Decide with legal and cost input |
| Analytics | Live queries | Aggregate tables | Aggregates, for privacy and speed |

## 11. Risks and open questions
Risks: over-building before the pilot proves value, vendor lock-in, privacy mistakes in
analytics, drift going unnoticed.
Open questions:
1. Which cloud and which regions, given data location rules?
2. Who operates the system and who is on call?
3. What load should we plan for, after the pilot?