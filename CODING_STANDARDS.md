# Coding Standards - Zecpath AI System

## Style

- Follow PEP 8 (Python standard style guide)
- Use `snake_case` for variables and function names
- Use `PascalCase` for class names
- Maximum line length: 100 characters

## Documentation

- Every function and class must include a docstring explaining its purpose, inputs, and outputs.
- Use inline comments only for complex or non-obvious logic.

## Structure

- One module should have one responsibility (e.g., `ats_engine/` handles only resume scoring logic).
- Place shared or reusable code in `utils/`.
- Store all test files in `tests/` and name them `test_*.py`.

## Logging

- Use the shared logger from `utils/logger.py` instead of `print()` statements.
- Log level guide:
  - `INFO` – Normal application flow
  - `WARNING` – Recoverable issues
  - `ERROR` – Failures or exceptions

## Git Commits

- Write clear, concise commit messages describing what changed.
- Commit small, logical changes instead of one large commit.