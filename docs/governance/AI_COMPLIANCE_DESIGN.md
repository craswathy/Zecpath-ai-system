# AI Compliance Design -- Zecpath Hiring Intelligence (Day 55)

Status: design, with a small tested reference module (ats_engine/governance_controls.py).
This is a design to support compliance. It is not a certification and not legal advice.
A lawyer and a data protection lead must review it before real candidates are used.

## 1. What the system does
Scores candidates across five rounds (ATS, screening, HR interview, technical interview,
machine test), recommends Selected, Hold / Review or Rejected with a confidence score and
an explanation, and produces a recruiter report. A human recruiter makes every final decision.

## 2. Regulatory picture (check current text before use)
| Area | Position | Design response |
|---|---|---|
| India, Digital Personal Data Protection Act 2023 and Rules 2025 | Notified 14 November 2025. Notice, consent, security safeguards, breach reporting and retention duties take effect in phases, with the core duties from mid-May 2027 | Consent-first design, plain notice, purpose-based retention, 72-hour breach plan, one-year minimum audit logs |
| EU AI Act | Recruitment and candidate evaluation are high-risk uses. High-risk obligations were delayed to 2 December 2027 by the Digital Omnibus. Inferring emotions in recruitment is prohibited | Human oversight, logging, transparency, accuracy and fairness checks, and no emotion inference (Day 48) |
| Other markets | Depends on where candidates live | Legal review per market before launch |

## 3. Principles and controls
| Principle | Control in this design | Status |
|---|---|---|
| Lawful use and consent | Consent per purpose, recorded and withdrawable (section 4) | Check built, notice screens designed |
| Purpose limitation | Data used only for the consented purposes | Consent check built |
| Data minimisation | IDs instead of names, no raw video, no audio stored, numbers only for behavior and integrity signals | Designed |
| Transparency | Plain notice that AI is used, what is scored, and that a human decides | Designed |
| Human oversight | Every output is a recommendation. Human review fields exist. Only Hold / Review can be forced by safety rules | Built (Days 52, 53) |
| Explainability | Every score and decision stores weights, rules, confidence and explanation | Built |
| Accuracy and robustness | Tests, error analysis against reference cases, thresholds reviewed (Day 54) | Built on simulated data |
| Fairness | No emotion inference. Behavioral and integrity signals never cause a rejection. Fairness testing plan (Days 48, 49) | Designed |
| Security | Security framework document | Designed |
| Accountability | Hash-chained audit log, named roles, review cadence | Log built, roles designed |
| Candidate rights | Access, correction, erasure, withdrawal and grievance process (section 5) | Designed |

## 4. Consent-based data usage
Purposes, each asked separately:
| Purpose | Needed for | Required to take part |
|---|---|---|
| interview_scoring | Scoring answers, tests and producing reports | Yes |
| video_behavior_analysis | Day 48 camera signals | No. Off by default. Declining has no penalty |
| integrity_monitoring | Day 49 browser and audio signals | Decide per role. If required, say so in the notice |

Rules:
1. Consent is asked before any interview data is collected, with a stand-alone notice in plain language.
2. The notice lists: what data is collected, each purpose, how long it is kept, who can see it, how to withdraw, how to complain, and who to contact.
3. Consent is a clear action by the candidate. No pre-ticked boxes.
4. Each consent record stores: candidate ID, purpose, granted time, notice version, withdrawn time.
5. Withdrawing is as easy as granting. After withdrawal the system stops using the data for that purpose and lists the related records for deletion review (find_withdrawal_deletions). The deletion itself is done by the data protection lead and logged.
6. The system checks consent on every access (check_access). No consent, no access, and the attempt is logged.
7. Candidates must be adults. Under-18 candidates need verified parental consent, which this design does not support. Block them at registration.
8. Data collected for hiring is not reused for another purpose (for example model training) without new consent.

## 5. Candidate rights
| Right | Process | Owner | Target time (starting value) |
|---|---|---|---|
| Know what is held | Provide a summary of stored data | Data protection lead | 30 days |
| Correct wrong data | Fix the record and log the change | Data protection lead | 30 days |
| Erase data | Delete, unless a legal hold or legal duty applies. Log the deletion | Data protection lead | 30 days |
| Withdraw consent | Same day stop of processing. Deletion review as above | Data protection lead | Same day |
| Ask for human review of a decision | A different reviewer re-checks the report | Hiring manager | 14 days |
| Complain | Acknowledge, investigate, answer in writing | Data protection lead | Within the legal limit. Check the exact limit |

## 6. Human oversight and contestability
- No automatic rejection or selection. The final decision is a named person's, recorded as a human_decision entry in the audit log.
- Reviewers see the explanation, the rules that fired, and the confidence.
- A candidate can ask for a human to re-check a result, and can see which kinds of factors were used.

## 7. Transparency to candidates
The notice and the interview start screen say:
1. An AI system scores your answers and produces a report. A person makes the final decision.
2. What is scored: answers, test results, and (only if you agree) camera and browser signals.
3. What is not done: no emotion reading, no face recognition, no lie detection.
4. How to ask questions, withdraw or complain.

## 8. Build status
| Item | Status |
|---|---|
| Role and scope access check, consent check, audit log with hash chain, retention and withdrawal lists | Built and tested (ats_engine/governance_controls.py) |
| Score and decision explanations, human review fields | Built (Days 51 to 54) |
| Real authentication and MFA, encrypted storage, consent screens, rights workflow, scheduled deletion job, external hash anchoring | Designed, not built |
| Legal review, data protection impact assessment, penetration test | Not done |

## 9. Checklist before any real candidate is used
1. Lawyer reviews this design for the target countries.
2. Data protection impact assessment completed.
3. Notice and consent screens written and tested with real users.
4. Retention periods approved.
5. Authentication, encrypted storage and backups in place.
6. Penetration test and access review done.
7. Fairness and accuracy checked on consented, recruiter-labelled data.
8. Named data protection lead and system owner.

## 10. Limits
- All retention periods, target times and thresholds are starting values.
- The reference module authorizes but does not authenticate. It trusts the user record it is given.
- The audit log is tamper-evident, not tamper-proof.
- Laws change. Dates and duties above must be checked against current text.