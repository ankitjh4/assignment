# UAT Protection Notes

Use this file to document what must not be broken while building the DRINKOO capstone.

## UAT-Locked Files Or Behaviors

The following files and behaviors are UAT-locked after initial approval:

```text
Database/schema.sql — table structure, column names, data types, and foreign keys
Tests/conftest.py — shared fixtures; changing these would invalidate all test results
Backend/config.py — environment variable loading; changes here affect all services
prompt.md — final approved OpenRouter system prompt
scripts/evaluate_submission.py — grading script; must not be modified
```

## NEVER_MODIFY List

```text
plan.md
README.md
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
.env.example
Database/schema.sql (after UAT approval)
Tests/conftest.py (after all tests pass)
```

## Required Checks Before PR

- [x] App runs locally (`uvicorn Backend.main:app --reload` on port 8000)
- [x] Backend routes work (tested with curl and FastAPI /docs)
- [x] Frontend pages work (index, signup, login, chat, upload, status all load)
- [x] Database schema loads (32 schema tests pass)
- [x] Text2SQL checks pass (Database/text2sql_checks.md — 6/6 PASS)
- [x] RAG answers are grounded in DRINKOO data (retrieval confirmed via chat tests)
- [x] OpenRouter prompt is saved in `prompt.md` (all placeholders filled)
- [x] Auth and protected routes work (9 auth tests pass)
- [x] Image upload validation works (6 upload tests pass)
- [x] Tests pass (32/32 tests pass)
- [x] Security test report is complete (Reports/security-test-report.md)
- [x] `git diff --stat HEAD` shows only expected changes

## Notes

UAT approval gate: All 32 pytest tests must pass before any change to UAT-locked files. The evaluate_submission.py script must score >= 70 before pull request submission.

Any change to Database/schema.sql must be reviewed by a human (instructor) and all tests re-run from scratch after the schema change.
