# Developer Onboarding Guide -- Zecpath AI

Goal: a new developer runs the system and makes a safe change on day one.

## Day 1: setup (about 1 hour)
1. Install Anaconda and Git. Install ffmpeg and add it to PATH if you will touch speech-to-text.
2. Clone the repository.
3. Create the environment:

       conda create -n zecpath-ai python=3.11 -y
       conda activate zecpath-ai
       pip install -r requirements.txt

4. Run the tests. All must pass before you change anything:

       pytest tests/

5. Run the ATS pipeline using the command list in the handbook, section 7.

## Day 1: read in this order
1. README.md
2. ZECPATH_AI_TECHNICAL_HANDBOOK.md
3. SYSTEM_ARCHITECTURE_DOCUMENTATION.md
4. MODULE_INDEX.md
5. CODING_STANDARDS.md
6. TROUBLESHOOTING_NOTES.md

## Repository map
- data/ : sample resumes, JDs and every stage's output
- parsers/ : extraction, parsing and semantic matching
- ats_engine/ : scoring, ranking, fairness, screening, interview, unified scoring, API stubs, observability
- utils/ : shared logger
- tests/ : one test file per module
- notebooks/ : experiments only, not production code

## Coding rules
- PEP8, snake_case, a docstring on every function.
- One module has one job.
- Use the shared logger, not print.
- Never log personal data.
- Weights and thresholds live in config files, not inside functions.
- Add a test with every change. Test files start with sys.path.append(".").

## Your first task: add a skill to the dictionary
1. Open parsers/skill_master_dictionary.py and add the skill with its synonyms.
2. Add a test in tests/test_skill_extraction.py.
3. Run pytest tests/.
4. Re-run python -m parsers.run_skill_extraction and look at the output.
5. Commit with a clear message.

## Rules that protect the system
- Do not auto-reject on a system failure. Route to manual review.
- Do not fill a missing score with a made-up value. Redistribute the weight.
- Do not bypass attribute masking when adding new scoring inputs.
- Do not change a threshold without checking the real score spread first.
- Do not claim a number you cannot reproduce from the repository.

## Habits that avoid known mistakes
- Check a file with type after saving. Empty files happened several times.
- Before pasting new code over a file, select all and delete first. Pasting after old code caused a syntax error.
- Run modules with python -m, not by file path.
- Re-run the whole pipeline after changing source data, so outputs match inputs.

## Where to get help
TROUBLESHOOTING_NOTES.md first, then IMPROVEMENT_BACKLOG.md for known
gaps, then ask the previous developer.

## Good next tasks
- Column-aware PDF extraction (top backlog item).
- Replace dictionary skill matching with a trained NER model.
- Multilingual question bank.
- Connect the API stubs to a real database and queue.
- Validate thresholds on real recruiter-labelled data.