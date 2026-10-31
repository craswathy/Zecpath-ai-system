# Governance Documentation -- Zecpath Hiring Intelligence (Day 55)

## 1. Roles and responsibilities
| Role | Responsible for |
|---|---|
| System owner | Purpose of the system, approving changes, accepting risks |
| Data protection lead | Consent records, candidate rights, retention, deletion, breach decisions |
| Security lead | Access control, storage, monitoring, incident response |
| Recruiter | Reviewing reports, making and recording the final decision |
| Hiring manager | Second review on request, own jobs |
| Auditor | Independent checks of the audit log and reviews |
| Admin | User accounts. No access to candidate data |

Name a person for each role before real use.

## 2. Audit trail system
### Events logged
| Event | Written when | Main fields |
|---|---|---|
| score | A unified score is calculated | model_version, job, role profile, hiring fit, category, round scores, weights, low-reliability rounds |
| decision | A recommendation is made | model_version, decision, score-based decision, confidence, rule IDs, human review required, final decision (empty) |
| human_decision | A person records the final decision | reviewer, final decision, reason |
| access | Anyone tries to read or change candidate data | user, role, action, allowed or denied, reason |
| consent | Consent is given or withdrawn | purpose, notice version, time |
| deletion | Data is deleted | record type, reason, time. Never the content |
| config_change | Weights, thresholds or roles change | what changed, who approved |

### Entry format
```
{"seq": 2, "time": "2026-10-31T10:00:00+00:00", "event": "decision", "actor": "system",
 "candidate_id": "demo_confident", "detail": {...}, "prev_hash": "...", "hash": "..."}
```

### Rules
1. Append only. Nobody edits or deletes entries.
2. Each entry holds a hash of its content and the hash of the entry before it. Editing or removing an entry breaks the chain (AuditLog.verify).
3. The log never holds transcript text, answers, video or names. It holds IDs, numbers, rule IDs, versions and who did what.
4. Score and decision entries carry the model version, so any result can be explained later.
5. Access to the log is limited to the data protection lead and auditors. Read-only.
6. Keep logs for at least one year (starting value 365 days). Check the legal minimum for each country.
7. Verify the chain every week. Store the latest hash outside the system.
8. Logs are never committed to Git. Only the simulated demo log is.

### Reconstructing a decision
For one candidate: find the score entry (inputs, weights, version), the decision entry (rules, confidence), the human_decision entry (who, what, why), and the access entries (who looked).

## 3. Data retention policy (starting values for approval)
| Data | Keep for | Then | Notes |
|---|---|---|---|
| Transcripts | 180 days | Delete | Retention starts at the interview |
| Reports | 365 days | Delete | |
| Score records | 365 days | Delete | |
| Decision records | 365 days | Delete | |
| Behavior features | 90 days | Delete | Only exists with video analysis consent |
| Code snapshots (machine test) | 180 days | Delete | |
| Consent records | 1095 days (3 years) | Delete | Kept longer to prove consent |
| Audit log | 365 days minimum | Archive or delete | Contains no personal content |

Rules:
1. Keep data only while the purpose lasts. Do not keep data "just in case".
2. A legal hold stops deletion for the records it covers. Each hold has an owner and a reason.
3. If consent is withdrawn, the related records are listed for deletion review the same day (find_withdrawal_deletions).
4. A sweep runs every quarter (find_expired). The data protection lead approves the list, deletion is carried out, and an audit entry is written.
5. Backups expire on a fixed cycle, so deleted data does not return.
6. Tell candidates the retention periods in the notice.
7. Review the periods every year and when the law changes.

## 4. Human oversight procedure
1. The system produces a recommendation and a report. It never contacts the candidate.
2. The reviewer reads the headline, the strengths, weaknesses and risks, and the rules that fired.
3. For Hold / Review, the reviewer checks the reason (for example a weak key round, rounds that disagree, integrity priority).
4. The reviewer records the final decision and a short reason. This writes a human_decision entry.
5. A reviewer who disagrees with the system explains why. Frequent disagreements are reviewed (section 6).
6. Integrity and behavioral information is context only. It is never the only reason for a rejection.

## 5. Model and change management
1. Every record carries a model version.
2. Any change to weights, thresholds or rules needs: a written reason, a test run (all tests passing), an accuracy and fairness check, and approval from the system owner and the data protection lead.
3. Each change gets a version number and an entry in CHANGELOG.md and in the audit log (config_change).
4. Keep the previous version so a change can be rolled back.
5. Results from earlier versions are not changed. They stay explainable under their own version.

## 6. Review cadence
| How often | Check |
|---|---|
| Weekly | Verify the audit chain |
| Monthly | Review who has access. Review denied-access alerts |
| Quarterly | Retention sweep. Review reviewer disagreements with the system |
| Every 6 months | Accuracy and fairness review on consented, recruiter-labelled data |
| Yearly | Review this policy, the retention periods and the law |

## 7. AI system register entry
| Field | Value |
|---|---|
| Name | Zecpath Hiring Intelligence |
| Purpose | Decision support for candidate evaluation |
| Risk class | High-risk use (recruitment) |
| Data | Resumes, interview transcripts, test results, optional behavior and integrity signals |
| Output | Scores, recommendation, report. Human decides |
| Owner | To be named |
| Status | Prototype on simulated data |

### Main risks
| Risk | Mitigation |
|---|---|
| Unfair or wrong decisions | Human decision, explanations, error analysis, fairness checks, no emotion inference |
| Over-trust in scores | Confidence score, safety rules, reports state limits |
| Data leak | Security framework |
| Keeping data too long | Retention schedule and sweep |
| Using data without consent | Consent check on every access |
| Silent changes to the system | Versioning and change approval |

## 8. How to run the reference module
```
python -m ats_engine.run_governance_demo
pytest tests\
```

## 9. Limits
- Prototype on simulated data. No real candidates.
- Roles are not yet named. Retention periods, review cadence and target times are starting values.
- The module authorizes but does not authenticate. Storage encryption, alerts and scheduled deletion are designed, not built.
- Laws and dates change. A lawyer must confirm each duty before real use.