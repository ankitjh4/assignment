# GitHub Copilot Instructions

## Project

DRINKOO RAG Chatbot — a Python-centric FastAPI web application for a fictional beverage company.
The app includes signup/login (JWT auth), a grounded RAG chatbot powered by OpenRouter, image upload,
a SQL database (SQLite, 8 tables), and a status/health page. The frontend is React 18 + Vite + Tailwind CSS.

## AI Scope Statement

Files and folders Copilot is allowed to assist with during active development sessions:

```
Backend/
Frontend/src/
Database/
Tests/
Security/
Observability/
Reports/
prompt.md
```

## NEVER_MODIFY

The following files are UAT-locked after initial approval. Copilot must not modify these:

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

## Coding Constraints

1. Keep the app Python-centric — FastAPI for all backend routes.
2. Use SQLite via SQLAlchemy for the database.
3. Use simple React 18 + Vite + Tailwind CSS for the frontend — no SSR framework.
4. Use OpenRouter with a free model (`mistralai/mistral-7b-instruct:free`).
5. Do not commit API keys or secrets — read from environment variables only.
6. Store the final RAG prompt in `prompt.md`.
7. Store all SQL table creation scripts in `Database/schema.sql`.
8. Protect `/api/chat` and `/api/upload` routes with JWT auth.
9. Validate image uploads: allowed types (jpg, jpeg, png, gif, webp), max 5 MB.
10. Add or update tests for every generated code change — coverage must not decrease.
11. Use parameterized queries or SQLAlchemy ORM — never string-interpolated SQL.
12. Hash passwords with bcrypt (passlib) — never store plaintext passwords.

## Prompt Review Checklist

Before asking Copilot to generate code, confirm the prompt says:

1. What to build (specific route, component, or function).
2. What NOT to touch (reference NEVER_MODIFY list).
3. What tests are required.

## Review Requirement

After every Copilot coding session, run:

```bash
git diff --stat HEAD
```

Review whether any unexpected files changed. If a UAT-locked file appears in the diff, revert it immediately.
