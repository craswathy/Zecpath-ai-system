# Security Framework -- Zecpath Hiring Intelligence (Day 55)

Status: design, with access control and audit logging built as a tested reference module.

## 1. Assets and classification
| Level | Data | Handling |
|---|---|---|
| 3 Restricted | Transcripts, reports, code snapshots, behavior features, consent records | Encrypted, access by role and job scope, consent required |
| 2 Confidential | Scores, decisions, audit log (pseudonymous IDs) | Encrypted, role access |
| 1 Internal | Configuration, weights, thresholds, model code | Version control, change approval |
| 0 Public | Public documentation | None |

Candidates are identified by ID in all files, logs and file names. Names and contact details are kept in a separate store.

## 2. Threats and responses
| Threat | Response |
|---|---|
| Someone reads candidate data they should not see | Role and job-scope checks, consent check, deny by default, every attempt logged |
| Insider misuse (browsing, copying, bulk export) | Need-to-know scope, export is a separate permission, alerts on unusual access |
| Scores or decisions changed after the fact | Hash-chained audit log, human decisions logged, config changes approved |
| Data leaked through logs or error messages | No transcript text, answers or names in logs. Log IDs and numbers only |
| Stolen login or API key | MFA, short-lived tokens, secrets in a secret store, rotation |
| Malicious candidate code (machine test) | Locked sandbox from Day 50: no network, hard limits, isolated and destroyed per run |
| Lost or stolen backup | Encrypted backups with the same retention rules |
| Third-party or model vendor risk | Review vendors, sign data processing terms, prefer running speech and text models inside the platform |
| Over-keeping data | Retention schedule and a scheduled sweep (find_expired) |

## 3. Access control (least privilege, separation of duties)
| Role | May do | May not do |
|---|---|---|
| Recruiter | View report, scores, transcript, export report, record decision, for own jobs only | See other jobs, manage users, view the audit log |
| Hiring manager | View report and scores, record decision, own jobs only | View transcripts, export |
| Data protection lead | View audit log, delete data on a valid request | Change scores or decisions |
| Auditor | Read the audit log | Anything else. No change rights |
| Admin | Manage users and system settings | See candidate data |
| System service | Write scores, decisions and audit entries | Read reports |

Rules:
1. Deny by default. A role gets only the actions listed above.
2. Recruiters and hiring managers see only candidates on their assigned jobs.
3. Access to candidate data also needs valid consent for the purpose (interview_scoring).
4. Every attempt, allowed or denied, writes an audit entry.
5. MFA for every human role. Sessions end after inactivity.
6. Access is reviewed monthly. Leavers lose access the same day.
7. Admin cannot read candidate data, and auditors cannot change anything.

Implemented in ats_engine/governance_controls.py (is_allowed, has_consent, check_access). The module authorizes. Authentication (who is this user) is a separate service that must supply a verified user.

## 4. Secure storage
### Transcripts
- Stored in a separate encrypted store, not in the report or score tables.
- Encryption at rest with a strong standard (for example AES-256), keys held in a key management service and not on the same server as the data.
- Linked to a candidate only by ID. Transcript files are named with random IDs, not names.
- Access only through the service layer, which applies the access rules. No direct database access for people.
- Retention 180 days (starting value), then secure deletion.
- Never copied into logs, tickets, chat messages or emails.

### Reports
- Stored encrypted. Downloads use signed links that expire (for example in 15 minutes) and are single use.
- Exports are logged, and the file carries the candidate ID and a generated date.
- Retention 365 days (starting value).

### Other stores
- Scores and decisions: encrypted, pseudonymous IDs.
- Consent records: kept longer than the data they cover, so consent can be proven.
- Behavior features: numbers only, retention 90 days, off unless the candidate consented.

### Deletion
- Delete the record, then destroy its encryption key where records have their own key (so copies in backups become unreadable).
- Backups expire within a fixed period (for example 35 days), so deleted data does not live on forever.
- Every deletion writes an audit entry with the record type and time, never the content.

## 5. Data in transit and the API
- TLS for all traffic.
- Authenticated API calls with short-lived tokens. No anonymous access to candidate data.
- Input validation (the Day 44 API already returns a single error shape and 422 for bad input).
- Rate limits on login, answer submission and report download.
- One error format that never shows internal details.

## 6. Secrets and software
- No passwords, keys or tokens in the code repository. Use environment variables or a secret manager.
- Scan the repository for secrets before every push.
- Pin dependency versions and check them for known problems on a schedule.
- Keep generated data (candidate files, audit logs, results) out of Git. Only simulated demo data is committed.

## 7. Monitoring
Alerts on:
- repeated denied access by one user
- many report downloads in a short time
- access outside normal hours
- audit chain check failing (verify)
- a role change or a new admin

To make tampering with the whole log detectable, store the latest audit hash outside the system that holds the log (for example weekly, in a separate account).

## 8. Incident response
1. Detect and contain: disable the affected accounts and keys.
2. Assess: what data, how many candidates, how long.
3. Notify: the data protection lead decides on notice to the regulator and to candidates. Plan for notice within 72 hours of finding a breach, and confirm the exact duty for each country.
4. Fix, then review: write down what happened and what changes.
5. Keep a record of every incident and its handling.

## 9. Security testing
- Automated tests for roles, scope, consent, audit chain and retention (tests/test_governance_controls.py).
- Access review monthly. Penetration test before real candidates.
- Test restoring from backup, and test that deleted data is gone.

## 10. Build status
| Item | Status |
|---|---|
| Role and scope checks, consent check, audit log with verification, retention lists | Built and tested |
| Authentication and MFA, encrypted stores and key management, signed links, rate limits, alerts, secret scanning, backup rules | Designed, not built |
| Penetration test, vendor review | Not done |

## 11. Limits
- Design only for most items. The reference module runs in memory and trusts its inputs.
- Data location rules for each country must be checked.
- Numbers (link expiry, backup period) are starting values.