\# Coding Standards - Zecpath AI System



\## Style

\- Follow PEP8 (Python standard style guide)

\- Use snake\_case for variables and function names

\- Use PascalCase for class names

\- Max line length: 100 characters



\## Documentation

\- Every function/class must have a docstring explaining purpose, inputs, and outputs

\- Use inline comments for complex logic only (not obvious lines)



\## Structure

\- One module = one responsibility (e.g. ats\_engine handles only resume scoring logic)

\- Shared/reusable code goes in utils/

\- All tests go in tests/, named test\_<module>.py



\## Logging

\- Use the shared logger from utils/logger.py instead of print() statements

\- Log level guide: INFO for normal flow, WARNING for recoverable issues, ERROR for failures



\## Git Commits

\- Write clear, short commit messages describing what changed

\- Commit small, logical chunks rather than one giant commit

