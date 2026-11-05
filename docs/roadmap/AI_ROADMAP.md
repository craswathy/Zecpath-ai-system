# AI Roadmap -- Zecpath Hiring Intelligence (Day 58)

Status: proposal. Dates are indicative and assume a small team. Targets are proposals to
agree with the project owner. Legal points need a lawyer's review.
Related: INNOVATION_PROPOSAL.md, FUTURE_ARCHITECTURE.md.

## 1. Where the system is today (Days 1 to 57)
| Area | State |
|---|---|
| Resume and job description parsing, ATS, screening | Built (Days 5 to 26) |
| HR interview AI (questions, follow-ups, scoring, summary) | Built, tested on simulated data |
| Technical interview scoring (depth, reasoning, skills) | Built (Day 47). Interview design and machine test are designs (Days 46, 50) |
| Five-round score, decision with confidence, recruiter report | Built (Days 51 to 53) |
| Error analysis, governance controls, end-to-end test, stabilization | Built (Days 54 to 57) |
| Behavioral and integrity signals | Designed only (Days 48, 49) |

Honest gaps:
1. All testing uses simulated candidates. No real hiring outcomes.
2. Thresholds and weights are starting values, not tuned.
3. The end-to-end test used stand-ins for ATS, screening and the communication and confidence estimates.
4. Agreement with humans was measured against a placeholder reviewer.
5. No real login, interviews are held in memory, no encrypted storage.
6. No legal review or data protection impact assessment yet.

## 2. Principles for everything that follows
1. A human makes the final decision. The system recommends and explains.
2. Observable, not inferred. No emotion detection, no personality or lie detection.
3. Rules decide scores and decisions, so every result can be traced.
4. Consent first, purpose limited, least data.
5. Measure before scaling. Every phase ends with a gate.
6. Candidates should benefit, not only employers.
7. Firewall between practice (coaching) and hiring.

## 3. The three improvement areas
| Area | Verdict | Reason | Safe form |
|---|---|---|---|
| AI video analysis | Limited and late (Phase 4) | Accuracy varies with lighting, skin tone, camera, glasses, disability and bandwidth. Privacy risk | On-device, opt-in, observable signals only (face in frame, framing, lighting, pace). Never scored by default |
| Emotion detection | Do not build | Inferring emotions in recruitment is prohibited in the EU, the science is disputed, and it risks bias | Delivery feedback in a private practice mode: filler words, pace, pauses, answer structure |
| Real-time feedback | Build in two safe forms | Useful, if it does not turn real interviews into a game | Practice mode live tips. Recruiter live assist (topic coverage, time, suggested follow-ups). No live scores shown to candidates |

## 4. Feature priorities
Scales 1 to 5. Higher value is better. Higher effort and risk are worse.
| Idea | Value | Effort | Risk | Data readiness | Priority |
|---|---|---|---|---|---|
| Interview analytics dashboard | 5 | 2 | 1 | 4 (stored scores and decisions exist) | Now |
| Candidate improvement suggestions | 4 | 2 | 2 | 4 (missed key points are already stored) | Next |
| AI coaching system (practice mode) | 4 | 3 | 2 | 3 | Next |
| Recruiter live assist | 3 | 3 | 2 | 3 | Later |
| Multi-domain and multi-language expansion | 4 | 4 | 2 | 2 | Later |
| Semantic matching in technical scoring | 3 | 3 | 1 | 3 | Later |
| Non-inferential video features | 2 | 4 | 4 | 1 | Phase 4 only after fairness testing |
| Emotion detection | not scored | | prohibited | | Do not build |

## 5. Phased roadmap
### Phase 0: make the pilot real (weeks 0 to 6)
Goal: close the open items from Days 54 to 57.
- Wire the real ATS, screening and communication and confidence analysers into the end-to-end test.
- Get 2 or 3 real reviewers to judge at least 50 candidates, and measure AI against them and them against each other.
- Add real login, saved interviews, encrypted storage.
- Legal review and data protection impact assessment. Consent screens and notice.
- Decide on a soft ATS gate (low ATS goes to a recruiter before interview time is spent).

Gate to Phase 1: all tests and the edge-case battery pass on real modules, login and storage in place, legal sign-off, consent flow tested.

### Phase 1: controlled pilot (months 2 to 4)
Goal: one role family, consented real candidates.
- Compare AI with recruiters on every candidate. Record overrides and reasons.
- Calibrate thresholds on a labelled set, then check on a fresh holdout set.
- Analytics dashboard v1 for the project team.

Gate to Phase 2 (proposed targets): exact agreement with the recruiter majority at least 70 percent, serious disagreements (Selected against Rejected) at most 2 percent, no unresolved severe bugs, audit log and retention checks pass, a fairness review of aggregated results with no unexplained gaps.

### Phase 2: candidate value (months 4 to 7)
- Candidate improvement suggestions (opt-in, after the decision).
- AI coaching practice mode MVP (text-based, one domain).
- Dashboard v2: funnel, override rate, deferral rate, data quality, model versions.

Gate: candidate feedback rated useful by most users, no coaching data reaching hiring, no rise in complaints.

### Phase 3: scale (months 7 to 12)
- More domains (Java, DevOps, data analytics) and more languages.
- Queue-based speech and code-run pipeline, long-running model workers, model registry, shadow testing of new versions.
- Multi-tenant isolation and an API for client systems.
- Semantic matching for technical answers.

Gate: load test targets met, per-tenant isolation tested, rollbacks rehearsed.

### Phase 4: advanced (12 months and later)
- Optional, opt-in, on-device video features that are observable only, after fairness validation.
- Language-model help for drafting questions and phrasing feedback, behind guardrails and never for scoring or decisions.
- Recruiter live assist.

Gate: independent fairness and security review, legal sign-off per market.

## 6. KPIs
| Group | Measures |
|---|---|
| Decision quality | Agreement with recruiters, serious disagreement rate, false positive and false negative rate against reference, override rate, share deferred to a person |
| Fairness | Score and decision rates compared across consented groups. Small groups are hidden |
| Safety | Integrity flag false alarms (from reviewer feedback), complaints |
| Operations | Time to decision, cost per candidate, stage failure rate, resume upload failure rate |
| Candidate experience | Completion rate, usefulness rating of feedback |
| Governance | Audit chain checks passing, retention sweeps on time, rights requests answered on time |

## 7. Main risks
| Risk | Mitigation |
|---|---|
| Building on untested assumptions | Phase 0 and Phase 1 use real labelled data before any new feature |
| Legal change or reading | Lawyer review per market, laws re-checked each phase |
| Gaming of scores through feedback | Topic-level feedback, question variants, no thresholds disclosed |
| Bias in video or language features | Observable signals only, fairness testing, opt-in, off by default |
| Scope growth | Gates, and the "Do not build" list |
| Over-trust in AI | Confidence, safety rules, human sign-off, clear limits in every report |

## 8. Assumptions and dependencies
- A small team: about two backend or AI engineers, one front-end engineer, part-time QA, legal and data protection support.
- Access to consenting candidates and willing recruiters for Phases 0 and 1.
- Decisions needed early: which role family to pilot, which markets, the data retention periods.

## 9. Open questions
1. Which role family and which country first?
2. Is a soft ATS gate acceptable to recruiters?
3. Who owns the system and who is the data protection lead?
4. Should practice data ever be used to improve the product, and with what consent?

