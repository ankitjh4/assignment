# GitHub Copilot Instructions

## Project

DRINKOO RAG chatbot website — a Python/FastAPI backend with SQLite database, keyword-based RAG retrieval over DRINKOO product data, OpenRouter LLM integration (free model), and a plain HTML/CSS/JS frontend. The project is a capstone for the CloudThat GitHub Copilot training program.

## AI Scope Statement

Files and folders Copilot is allowed to help modify:

```text
Backend/
Frontend/
Database/
Tests/
Reports/
Security/
Observability/
requirements.txt
prompt.md
```

## NEVER_MODIFY

Copilot must never modify the following files:

```text
plan.md
README.md
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
.gitignore
.env.example
DRINKOO_Capstone_One_Pager.pdf
Database/schema.sql (after UAT approval)
Tests/conftest.py (after all tests pass)
Backend/config.py (requires human review for any change)
```

## Coding Constraints

1. Keep the app Python-centric. No Node.js, no npm, no frontend build tooling.
2. Use FastAPI for the backend.
3. Use simple HTML, CSS, and JavaScript for the frontend (no React, Vue, or Angular).
4. Use SQLite via the `sqlite3` stdlib. Do not add SQLAlchemy or any ORM.
5. Use OpenRouter with a free model (`meta-llama/llama-3.2-3b-instruct:free`).
6. Do not commit API keys or secrets. Use environment variables via `.env`.
7. Save the final model prompt in `prompt.md`.
8. Save SQL table creation scripts in `Database/schema.sql`.
9. Protect authenticated routes with `Depends(get_current_user)`.
10. Validate image uploads: check content_type and file size before reading content.

## Prompt Review Checklist

Before asking Copilot to generate code, confirm the prompt says:

1. What to build (specific function, route, or feature).
2. What not to touch (reference the NEVER_MODIFY list above).
3. What tests are required (which test file and what scenarios).

## Review Requirement

After every Copilot coding session, run:

```bash
git diff --stat HEAD
```

Confirm that only files within the allowed scope changed. If unexpected files appear in the diff, revert them before committing.
