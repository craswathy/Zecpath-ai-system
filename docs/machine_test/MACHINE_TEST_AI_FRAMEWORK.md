# Machine Test AI Framework (Day 50)

Status: design only. Nothing here is implemented.
Related: TASK_EVALUATION_LOGIC.md, SCORING_MODEL_REAL_WORLD_TASKS.md,
Day 46 (interview structure), Day 47 (technical scoring), Day 49 (integrity).

## 1. Purpose
Evaluate real-world technical skill by giving the candidate tasks to do, not only
questions to answer. The system runs the candidate's work, measures it, and gives
the recruiter an explainable score.

## 2. Principles
1. Tests and rules decide the score. AI assists with task variants and report wording,
   never with the number.
2. Every score stores its explanation and the evidence behind it.
3. Null means no data. A platform failure is never scored as zero.
4. Correctness matters most. Speed and style adjust the score, they do not replace it.
5. Capture only what is needed: code snapshots and run results. No screen recording.
6. A human makes the final decision. A score is decision support.

## 3. Types of machine tests
| Type | Candidate receives | Candidate produces | Evaluated by |
|---|---|---|---|
| Coding problem | Problem statement, starter code, visible tests | A working solution | Hidden tests, runtime, static analysis, approach note |
| Debugging task | Broken code and failing tests | A fixed program plus a short note on the root cause | Hidden tests, size of the change, note rubric |
| File-based task | Input files (CSV, JSON or log) and a goal | A script or an output file | Comparison with the expected output, runtime, static analysis |
| Mini system design | A short scenario with requirements | Written design: components, data flow, trade-offs | Rubric of required points, with human review |

Examples by domain: MERN (fix a broken Express route), Java (implement a collection
task), DevOps (read a log file and report failed deployments), Data Analytics
(clean a messy CSV and compute summary figures).

## 4. Difficulty by experience (links to Day 46)
| Experience | Coding | Debugging | File-based | Mini design |
|---|---|---|---|---|
| Under 3 years | L1 to L2 | L1 to L2 | L1 | not used |
| 3 to under 5 years | L2 to L3 | L2 | L2 | L2 |
| 5 years and above | L3 | L3 | L2 to L3 | L3 |

Levels: L1 basic, L2 applied, L3 advanced.

## 5. Architecture
```
Candidate browser (editor, Run button, task panel, timer)
   |  Run (visible tests only)          |  Submit or deadline
   v                                    v
Session service ---------------------> Job queue
   |  stores snapshots, run events        |
   |                                      v
   |                              Sandbox worker pool
   |                              (isolated containers)
   |                                      |
   |                              Hidden tests, timing, static analysis
   |                                      v
   +---------------------------> Evaluation service (formulas in the logic document)
                                          v
                              Scoring service -> report -> recruiter review
```

| Part | Job |
|---|---|
| Editor and task panel | Show the task, the editor, visible test results and the timer |
| Session service | Keep the server-side timer, snapshots and run events |
| Job queue | Hold evaluation jobs so many candidates can run at once (sync and async split, as in the HR API) |
| Sandbox workers | Run candidate code safely. Scale workers with queue length |
| Evaluation service | Compute correctness, efficiency, quality and approach |
| Scoring service | Combine metrics, apply the time factor, write the report |
| Task bank | Versioned task records, reviewed by a human before release |

Task record fields: id, type, level, domain, prompt, starter files, visible tests,
hidden tests with weights, reference solution runtime, expected time, time limit,
rubric points, allowed resources, task version.

## 6. Input and output capture
| Captured | How | Used for |
|---|---|---|
| Code snapshots | Autosave every 30 seconds if changed, on every Run, and on Submit. Stored as timestamped changes | Approach analysis, report timeline |
| Execution results | Per run: exit code, runtime, memory, stdout and stderr (cut at 10 KB), visible test results | Correctness, efficiency, report |
| Hidden test results | Stored, never shown to the candidate | Correctness |
| Output files | Stored with a hash | File-based comparison |
| Candidate notes | Approach or root-cause text | Approach score |
| Timing | Server-side task start, run times, submit time | Time-based scoring |

Not captured: screen recording, keystroke logs, clipboard content, webcam (video is
handled only by the Day 48 design and only with consent).

Run limit: one Run every 10 seconds per candidate, to protect the workers.

## 7. Sandbox and security requirements
Candidate code is untrusted. These are requirements, not an implementation:
- Each run in a fresh, isolated container that is destroyed afterwards.
- No network access.
- Hard limits on CPU time, memory, number of processes and disk space.
- Read-only base image. Only the working folder is writable.
- No access to hidden tests, the reference solution, other candidates' data or platform secrets.
- Allow-listed languages and libraries per task.
- Kill on timeout. A run that is killed is recorded as a failed run, not a platform error.
- Output size limits, so a program cannot flood the logs.
- A security review before any build.

## 8. Fairness and accessibility
| Risk | Mitigation |
|---|---|
| Different editors and habits | Provide a standard editor with basic help. Do not score typing speed |
| Language choice | Candidate picks from the allowed list. Thresholds are set per language |
| Slow internet | Autosave locally. Time is measured server-side and excludes outages |
| Assistive tools, keyboard only | Editor must work with screen readers and keyboard navigation |
| Extra time needs | A configurable time multiplier per candidate. Reason is not stored |
| Task wording favours one culture or language | Plain English, reviewed by more than one person before release |
| Task leaks | Several variants per task. Variants are checked for equal difficulty |

## 9. Integration with other parts
| Part | Link |
|---|---|
| Technical interview (Days 46, 47) | Same experience bands, levels and level weights. Machine test is a separate round |
| Technical scoring engine (Day 47) | Reused for scoring written notes and mini system design |
| Integrity (Day 49) | Large paste events from snapshots can be shown as recruiter context only. Never scored |
| Behavioral signals (Day 48) | Not used for the machine test score |
| Unified hiring fit | Machine test becomes a possible extra round. Its weight is decided later |
| Metadata and null rules | Day 7 metadata. Null means no data |

## 10. Limits and open decisions
1. Not built. Thresholds are untuned starting values.
2. Static analysis tools judge style narrowly. Code quality has a low weight for this reason.
3. Approach scoring from snapshots can misjudge people who plan offline and type once.
4. Mini system design scoring is pattern-based, so a human reviewer is needed.
5. Open decision: may candidates look up documentation or use AI assistants? Allowed
   resources are set per task and shown to the candidate.
6. Open decision: which languages to support first.
7. Legal and privacy check needed before use. This is not legal advice.