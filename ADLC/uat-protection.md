# UAT Protection Notes

## UAT-Locked Files Or Behaviors

The following must not be changed without explicit review and re-approval:

```
Database/schema.sql              — Table structure underpins all RAG retrieval and Text2SQL checks
Tests/conftest.py                — TestClient and DB fixtures must stay stable across test runs
Backend/auth.py                  — Auth logic is a security boundary; any change needs security review
prompt.md                        — Final RAG prompt is evaluated for faithfulness; changes reset scoring
.github/workflows/pr-evaluation.yml — Automated quality gate must not be bypassed
scripts/evaluate_submission.py   — Grading script must not be modified
plan.md                          — Assignment spec is locked by the instructor
README.md                        — Submission instructions must not change
```

## NEVER_MODIFY List

Copy this list into `.github/copilot-instructions.md`:

```
plan.md
README.md
Database/schema.sql              (after UAT sign-off)
Tests/conftest.py                (after first passing test run)
ADLC/ai-scope-statement.md
ADLC/prompt-review-checklist.md
ADLC/uat-protection.md
.github/workflows/pr-evaluation.yml
scripts/evaluate_submission.py
```

## Required Checks Before PR

- [x] App runs locally (`uvicorn Backend.main:app --reload`).
- [x] Backend API routes work (`/api/auth/signup`, `/api/auth/login`, `/api/chat`, `/api/upload`, `/api/status`).
- [x] Frontend pages work (Home, Login, Signup, Chat, Upload, Status).
- [x] Database schema loads and seeds without error.
- [x] Text2SQL checks pass (>= 90% on sample questions in `Database/text2sql_checks.md`).
- [x] RAG answers are grounded in DRINKOO data (retrieved context visible in responses).
- [x] OpenRouter prompt is saved in `prompt.md` with all placeholders filled.
- [x] Auth and protected routes work (401 on unauthenticated access).
- [x] Image upload validation works (type check, size check, path safety).
- [x] Tests pass (`pytest Tests/ --cov=Backend --cov-report=term-missing`).
- [x] Security test report is complete (`Reports/security-test-report.md`).
- [x] `git diff --stat HEAD` shows only expected changes after each Copilot session.

## Notes

UAT approval strategy: Each locked module is approved after its corresponding integration test passes
in CI and a human review of the diff confirms no unexpected side effects. Once approved, the file hash
is noted and any subsequent diff triggers re-review before merge.

Security-sensitive modules (auth.py, upload.py) require human review even if tests pass — AI-assisted
code in these files is always treated as a draft until a developer reads it line by line.
