# AI Scope Statement

Complete this before using GitHub Copilot for a coding session.

## Task

Implement the DRINKOO FastAPI web application end-to-end, including auth, protected chat, upload validation, SQL schema/seed, tests, observability notes, and security/report evidence.

## Files In Scope

Copilot-modifiable scope for this session:

```text
Backend/
Frontend/
Database/
Tests/
Observability/
Security/
Reports/
README.md
prompt.md
ADLC/
```

## Files Out Of Scope

Out-of-scope files for this session:

```text
DRINKOO_Capstone_One_Pager.pdf
plan.md
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
```

## UAT-Locked Items

UAT-locked items requiring human review before any edits:

```text
Database/schema.sql after acceptance validation
Tests/test_app.py after passing baseline
prompt.md after rubric-aligned finalization
```

## Test Requirements

- Run tests for signup/login/logout and protected route behavior.
- Run tests for chat endpoint and retrieval response shape.
- Run tests for upload validation and success path.
- Run test for status endpoint and schema table count.
- Run evaluator script and verify minimum score threshold.

## Review Notes

After coding, run `git diff --stat HEAD` and confirm only expected backend, frontend, database, tests, and evidence files changed.
