# Internal Review Report -- Zecpath AI System (Day 64)

## 1. Scope and method
Walkthrough of the pipeline ATS -> Screening -> HR -> Technical -> Decision
using the Day 63 demo dataset (8 fictional candidates, 2 jobs), run with
python -m ats_engine.run_system_walkthrough. Reviewers: [names/roles].
Full run time: [ ] seconds (includes model load).

## 2. Walkthrough result
| Stage | Works | Evidence | Caveat |
|---|---|---|---|
| ATS | Yes, on plain-text resumes | Day 63 results | Not tested on multi-column or scanned PDFs |
| Screening | Logic works | Day 22-31 tests | Score is simulated here, no real call or audio |
| HR interview | Logic works | Day 33-42 tests | Answers are typed text, no real interview |
| Technical | Scoring module exists | Day 47 tests | Not included in the Day 63 simulation |
| Decision | Works | Day 41, 52 tests | Thresholds tuned on small simulated data |

Candidates matching intended outcome: [ ] / 8.
Mismatches and their causes: [list from walkthrough_findings.json]

## 3. Findings

### Accuracy gaps
| # | Gap | Evidence |
|---|---|---|
| A1 | Skill, section and intent detection is dictionary and pattern based | Day 8-9, 25 limitations |
| A2 | Multi-column and scanned PDFs break section detection | Day 12 bug, Day 5 scanned file |
| A3 | Thresholds and floors were tuned on the same few cases that exposed the problems | Day 14, 42 notes |
| A4 | Accuracy against real recruiter decisions has never been measured | Day 17 sample was 10 resumes |
| A5 | [add any mismatch found in the walkthrough] | |

### UX issues
| # | Issue | Evidence |
|---|---|---|
| U1 | There is no user interface. Output is JSON and plain text | Repository contents |
| U2 | Reports show scores but few plain-language reasons per candidate | Day 28, 39 report format |
| U3 | English only | Day 22 note |
| U4 | [add reviewer comments from the feedback forms] | |

### Performance issues
| # | Issue | Evidence |
|---|---|---|
| P1 | Model load is a fixed cost per process | Day 18, 60 benchmarks |
| P2 | Parallel extraction can be slower for small batches | Day 60 result: [ ] |
| P3 | Load numbers come from one laptop and a function-level simulation | Day 60 limitations |

### Engineering and documentation issues
| # | Issue | Evidence |
|---|---|---|
| E1 | Duplicate-looking modules (hiring_fit_calculator_v2, unified_candidate_score_object) need a documented purpose or removal | MODULE_INDEX.md |
| E2 | run_answer_understanding.py appeared to contain summary code instead of a run function | MODULE_INDEX.md |
| E3 | The handbook does not yet describe the technical scoring, decision, aggregation and governance modules | Day 62 review |
| E4 | API stubs exist only for ATS and HR. No real database, queue or authentication | Day 59 document |

## 4. Reviewer feedback
[Paste a short summary of each reviewer's answers, with name and date.]

## 5. What the review does not show
- Accuracy on real candidates, real calls or real PDFs.
- Behaviour under real traffic.
- Anything about video or computer-vision analysis, which is not built.