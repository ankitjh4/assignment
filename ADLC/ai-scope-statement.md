# AI Scope Statement

Complete this before using GitHub Copilot for a coding session.

## Task

Build the full DRINKOO RAG Chatbot capstone: FastAPI backend, React + Vite + Tailwind frontend,
SQLite database with 8 tables, grounded RAG via OpenRouter, JWT auth, image upload, tests, and reports.

## Files In Scope

```
Backend/main.py
Backend/config.py
Backend/database.py
Backend/models.py
Backend/auth.py
Backend/rag.py
Backend/chatbot.py
Backend/upload.py
Backend/status.py
Backend/requirements.txt
Frontend/src/
Frontend/index.html
Frontend/package.json
Frontend/vite.config.js
Frontend/tailwind.config.js
Database/schema.sql
Database/seed.sql
Database/seed.py
Database/text2sql_checks.md
Tests/
Security/security-notes.md
Observability/observability-notes.md
Reports/
prompt.md
```

## Files Out Of Scope

```
plan.md
README.md
.github/workflows/pr-evaluation.yml
scripts/evaluate_submission.py
ADLC/ai-scope-statement.md
ADLC/prompt-review-checklist.md
ADLC/uat-protection.md
```

## UAT-Locked Items

```
Database/schema.sql              (locked after first successful seed + test run)
Tests/conftest.py                (locked after first passing test suite)
Backend/auth.py                  (locked after auth integration tests pass)
prompt.md                        (locked after RAG faithfulness >= 0.85 confirmed)
```

## Test Requirements

- test_schema.py: verify all 8 tables exist and have correct columns
- test_auth.py: signup, login, JWT validation, protected route access/rejection
- test_chatbot.py: chat endpoint returns grounded answer; unknown question handled gracefully
- test_upload.py: valid image accepted; wrong type rejected; oversized file rejected
- test_status.py: /api/status returns healthy JSON with db/rag/version fields

## Review Notes

After each Copilot coding session, run:

```bash
git diff --stat HEAD
```

Confirm only expected files changed. If a UAT-locked file appears in the diff, revert it immediately
before committing.
