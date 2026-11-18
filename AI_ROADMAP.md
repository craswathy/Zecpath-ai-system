# AI Roadmap -- Zecpath AI Engine

This roadmap comes from the gaps documented during the internship: the Day 64
improvement list, the Day 57 and 68 limitations, the Day 59 integration
design and the Day 60 and 61 operations plans. Phases show order and
dependency. They are not committed dates.

## 1. Where things stand

| Area | Status |
|---|---|
| Resume and job parsing, ATS scoring, ranking, fairness checks | Built and tested |
| Screening and HR interview scoring | Built and tested on simulated text |
| Technical scoring, cross-round aggregation, decision engine | Built and tested |
| Governance controls (consent, access, audit, retention) | Built as code, not deployed |
| API (decision endpoint, ATS and HR stubs) | Working locally |
| Logging, metrics and alert rules | Working locally |
| Documentation, demo dataset, release validation | Done |
| Accuracy on real data, deployment, real calls | Not done |

## 2. Roadmap

### Phase 1: Validate (needs real data)
| Item | Why | Done when |
|---|---|---|
| Tune thresholds and weights on recruiter-labelled outcomes | Current values were tuned on small simulated data | Precision, recall and confidence intervals reported on a held-out set |
| Measure agreement with recruiters | Accuracy has never been measured | Agreement (for example Cohen's kappa) reported |
| Fairness audit on real data | Bias checks exist but were run on small samples | Score and shortlist gaps across groups tested with significance |
| Fix ATS keyword inflation | Known open weakness | Keyword-stuffed resumes no longer outscore genuine ones |

### Phase 2: Harden
| Item | Why | Done when |
|---|---|---|
| Column-aware PDF reading and OCR for scanned files | Multi-column and scanned PDFs fail | Test files of both types extract correctly |
| Trained skill recognition model | Dictionary matching misses unseen skills | Beats the dictionary on a labelled sample |
| Real HTTP load test | Current load test is function-level | Throughput and latency measured against a running service |

### Phase 3: Deploy
| Item | Why | Done when |
|---|---|---|
| Database, queue and authentication | Specified in the integration document, not connected | Resume jobs run through a queue with signed webhooks |
| Containers, load balancer, shared embedding cache | Scaling plan | Services scale by adding instances |
| Deploy logging, metrics, dashboards and alerts | Monitoring is local only | Dashboard shows live traffic |
| Encrypted storage, saved sessions, secrets manager, legal review | Open security and compliance items | Each item reviewed and signed off |

### Phase 4: Extend
| Item | Why | Done when |
|---|---|---|
| Multilingual questions and speech | English only | At least one more language passes the same tests |
| Real telephony for screening calls | Calls are simulated | A real call produces a scored transcript |
| Video and behaviour analysis | Not built | Design reviewed for ethics first |
| Recruiter dashboard | Output is JSON and text | Recruiters can search and review candidates |
| Learned scoring model | Rules are the baseline | An interpretable model (such as logistic regression) beats the weighted score on held-out data |

## 3. Dependencies

- Phases 1 and 2 need real, consented, labelled hiring data.
- Phase 3 needs infrastructure and a backend team.
- Phase 4 needs product decisions and an ethics review.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Scores treated as final decisions | Human review stays required in every decision |
| Bias on real populations | Fairness audit before any real use |
| Overfitting thresholds to small data | Held-out evaluation, report intervals |
| Data privacy | Masking, consent checks, retention rules, no personal data in logs |

## 5. Success measures

Agreement with recruiters, time to first shortlist, share of candidates sent to
manual review, response time and failure rate. Targets are set after Phase 1.

