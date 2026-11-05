# Innovation Proposal (Day 58)

Status: proposal. Related: AI_ROADMAP.md, FUTURE_ARCHITECTURE.md.

## 1. Summary
Three features come first: an interview analytics dashboard, candidate improvement
suggestions, and an AI coaching practice mode. They build on data and modules that already
exist. Video analysis is limited and late. Emotion detection is not proposed.

## 2. The three improvement areas

### 2.1 AI video analysis
What it could do: check lighting and framing before an interview, confirm a face is in the
frame, and measure speaking pace from the audio.
Benefits: fewer technical failures, a clearer interview recording for the recruiter.
Risks:
- Accuracy differs across skin tones, lighting, glasses, head coverings, cameras and bandwidth.
- Candidates with disabilities or different habits may be misjudged.
- It raises privacy concerns and can make candidates self-conscious.
Decision: limited and late (Phase 4).
Safe form (follows the Day 48 design):
- opt-in and off by default
- processed on the candidate's device, with only numbers sent
- observable signals only
- never used to lower a decision
- tested for fairness before any use

### 2.2 Emotion detection
What it would claim to do: guess feelings such as nervousness or enthusiasm from face or voice.
Decision: do not build.
Reasons:
1. Inferring emotions in recruitment is prohibited in the EU.
2. The science behind emotion recognition is disputed.
3. Expressions differ across cultures and people, so the bias risk is high.
4. It could be used to punish people for harmless differences.
Alternative: delivery feedback in the private practice mode, based on what can be counted:
filler words, pace, pauses, answer length and structure. Nothing about feelings.

### 2.3 Real-time feedback
| Form | Decision | What it does |
|---|---|---|
| Practice mode live tips | Build | Live counter for filler words, speaking time, a reminder to give an example |
| Recruiter live assist | Later | Shows which topics are covered, time left, suggested follow-ups. The recruiter stays in control |
| Live scores or hints shown to a candidate during a real interview | Do not build | Turns the interview into a game, and may leak the scoring |
| Alerts based on emotion | Do not build | Same reasons as 2.2 |

## 3. New features

### F1. Interview analytics dashboard
Problem: nobody can see how the system behaves over many candidates.
Users: recruiters, hiring managers, the project owner, the data protection lead.
Views:
| View | Shows |
|---|---|
| Funnel | Candidates reaching each stage, and where they drop out |
| Score distributions | Per round and for the hiring fit, by role and job |
| Decisions | Selected, Hold / Review and Rejected counts. Share deferred to a person |
| Human overrides | How often reviewers disagree with the system, with their reasons |
| Integrity and review | Flag rates and what reviewers decided afterwards |
| Data quality | Resume upload failures, stage errors, missing rounds |
| Time | Time per stage and time to decision |
| Model versions | Compare results across versions |
| Fairness (restricted) | Aggregated rates across consented groups. Groups under 10 people are hidden |
| Skill gaps | Most common weak topics, for training and sourcing |
Data: the stored score objects, decision objects and the audit log. No transcript text.
Privacy: aggregated views, role-based access (Day 55), no names.
MVP: six charts from existing JSON files (funnel, score histograms, decision mix, override
rate, failure rate, time to decision).
Success: used weekly by recruiters, and it finds at least one real issue in the pilot.

### F2. Candidate improvement suggestions
Problem: rejected or on-hold candidates learn nothing.
What it does: after the decision, and only if the candidate opted in, send a short feedback
report with:
- strengths (topics answered well)
- topics to improve, with the key points that were missed (the technical scorer already stores them)
- communication tips (fillers, short answers, adding an example)
- suggested practice topics
What it never shows: scores, thresholds, other candidates, integrity flags, behavioral labels,
or the decision rules.
How it works: rule-based templates over stored results. A recruiter can review before release.
Language-model help can polish wording later.
Consent: separate opt-in. The feedback does not change the hiring decision.
Risks and answers:
| Risk | Answer |
|---|---|
| Candidates learn the rubric and game it | Topic-level feedback, question variants, no thresholds |
| Feedback is read as a decision | Sent after the decision, worded as development advice |
| Harsh or wrong feedback | Templates reviewed, recruiter release, a way to report errors |
| Data kept too long | Same retention rules as reports |
MVP: a text report for the technical interview and the HR interview.
Success: candidates rate it useful, complaints do not rise.

### F3. AI coaching system (practice mode)
Problem: candidates cannot practise with feedback.
What it does: a mock interview with the same question types (introduction, experience,
conceptual, scenario). After each answer it shows:
- key points covered and missed
- depth and reasoning of the answer
- delivery counts (fillers, pace, length)
- a suggested structure for a better answer (for example situation, action, result)
It tracks progress across sessions.
Firewall:
- practice data is private to the candidate
- never shared with an employer
- a separate consent
- a separate practice question bank, so real questions do not leak
- deleted on request
Optional later: language-model help for phrasing, behind the guardrails in FUTURE_ARCHITECTURE.md.
Risks and answers:
| Risk | Answer |
|---|---|
| Answers all sound the same | Encourage the candidate's own examples, not scripted text |
| Practice bank leaks real questions | Separate banks, regular rotation |
| Misleading confidence | Say clearly that practice scores do not predict hiring results |
| Conflict of interest | The firewall above |
MVP: text-based mock interview, one domain, using the existing question and scoring modules.
Success: scores and answer depth improve across a candidate's sessions, satisfaction is high.

## 4. Other ideas
- Question authoring assistant: drafts questions and key points, humans approve.
- Recruiter feedback loop: override reasons feed threshold calibration.
- Decision explanation view: why this result, in plain words.
- Candidate rights portal: self-service access, correction and erasure requests.
- Fairness monitoring toolkit.
- Semantic matching for technical answers.
- Multi-language support.

## 5. Ethics and legal checklist per feature
| Feature | Consent | Human in the loop | Affects hiring decision | Check before launch |
|---|---|---|---|---|
| Dashboard | Not needed for aggregates | Yes | No | Small-group hiding, access control |
| Improvement suggestions | Separate opt-in | Recruiter release | No | Wording review, retention |
| Coaching | Separate opt-in | Candidate only | No | Firewall test, separate data store |
| Recruiter live assist | Notice to candidate | Yes | Indirectly | No emotion signals, no hidden scoring |
| Video features | Opt-in | Yes | No by default | Fairness test, legal review |

## 6. How to test an idea before building it
1. Prototype on simulated data.
2. Pilot with a few consenting users.
3. Compare against a plain baseline (for example, feedback against no feedback).
4. Run the fairness check on aggregated results.
5. Go or no-go at the phase gate.

## 7. Open questions
1. Who reviews candidate feedback before release?
2. Should coaching be free or part of the employer package?
3. Which markets first, and what do they require?