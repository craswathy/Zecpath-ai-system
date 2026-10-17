# Technical Interview AI -- Blueprint (Day 46)

Status: design only. Not built yet.

## 1. Interview structure
1. Introduction: confirm role and years of experience
2. Experience questions: past projects and tools
3. Conceptual questions: core knowledge
4. Scenario problems: solve a realistic problem
5. Closing

## 2. Experience logic
| Years | Level | Focus |
|---|---|---|
| under 3 | Basics | fundamentals, simple tasks |
| 3 to under 5 | Intermediate | applied knowledge, debugging |
| 5 and above | Advanced | system design, scale, ownership |

Task text overlaps at 5 years, so bands use exact years as shown.

## 3. Role to skill domain
| Domain | Roles | Topics |
|---|---|---|
| MERN | MERN Developer | JavaScript, React, Node/Express, MongoDB |
| Java | Java Backend Developer | Java core, OOP, Spring Boot, SQL |
| DevOps | DevOps Engineer | Linux, Git, CI/CD, Docker, Kubernetes |
| Data Analytics | Data Analyst | SQL, statistics, Python, dashboards |

Match job title to domain. New domain = new data, not new code.

## 4. Difficulty progression
Levels: L1 basic, L2 applied, L3 advanced.
- Basics start at L1, Intermediate at L2, Advanced at L2 (scenarios at L3).
- Good answer: next question one level up.
- Weak answer: next question one level down.
- Otherwise: same level.

## 5. Flow states
Setup, Introduction, Experience, Conceptual, Scenario, Closing, Scoring, Report ready, Ended.
Phases only move forward. Diagram: INTERVIEW_FLOW_DESIGN.md.

## 6. Scoring
Components: technical knowledge, problem solving, experience depth, communication.
Missing data is excluded, never invented.
Any component below 0.5 lowers the overall band one level.
Output is decision support. A human recruiter decides.

## 7. Reuse from HR module
Transcript cleanup, follow-up engine, communication scorer, scoring structure.

## 8. Limits
- All numbers are starting values, not tuned on real data.
- Sample question bank is small.
- Text answers only, no live coding.