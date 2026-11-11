# Zecpath Demo Dataset (Day 63)

All names, resumes, job descriptions and answers are fictional and
written for demonstration. No real person's data is used.

## Contents
- resumes/ : 8 resumes of varied quality
- job_descriptions/ : 2 job descriptions (Data Analyst, Business Analyst)
- test_candidate_profiles.json : per candidate, the job, a quality label, spoken answers with duration and speech-to-text confidence, a simulated screening score, and the intended outcome
- simulation_results.json : output of the end-to-end run

## Test candidates
| Candidate | Scenario it tests |
|---|---|
| cand_priya | Strong, well structured resume with detail |
| cand_arun | Average profile, applying to the Business Analyst job |
| cand_meera | Fresher with no experience section |
| cand_ravi | Keyword-stuffed skills list, thin substance, hesitant and off-topic answers |
| cand_sana | Good skills with a long career gap |
| cand_john | Overqualified senior profile |
| cand_divya | Unstructured resume with no section headings |
| cand_kiran | Wrong domain (civil engineer applying to analytics) |

## What is real and what is simulated
- Real (computed by the repository's code): resume parsing, section detection, skill, experience and education extraction, semantic matching, ATS score, communication and confidence scoring, HR interview score, unified hiring fit.
- Simulated: the screening score (typed in per candidate, no real call), the spoken answers (written text, no audio), and the resumes themselves.

## How to run
    python -m ats_engine.create_demo_dataset
    python -m ats_engine.run_demo_simulation

## Limits
- Eight candidates show behaviour, not accuracy.
- The "intended outcome" is the author's expectation. A mismatch is a finding to investigate, not proof of a bug or a pass.
- Resumes are short plain text, easier than real PDFs. They do not test multi-column or scanned layouts.