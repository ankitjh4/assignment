# UAT Protection Notes

This document captures the User Acceptance Testing protection list for the DRINKOO RAG Chatbot capstone build.

## UAT-Locked Files Or Behaviors

These files and behaviors must not be changed without explicit human approval and re-review.

```text
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
plan.md
DRINKOO_Capstone_One_Pager.pdf
README.md (the original assignment instructions; we only appended a "How to run" section)
Database/schema.sql once the schema tests are green
Database/text2sql_samples.json once the Text2SQL eval is green
prompt.md after the final system prompt is approved
Tests/ after the suite is green and reviewed
ADLC/ai-scope-statement.md once approved
ADLC/prompt-review-checklist.md once approved
ADLC/uat-protection.md (this file) once approved
.github/copilot-instructions.md once approved
```

## NEVER_MODIFY List

Copy this list into [`.github/copilot-instructions.md`](../.github/copilot-instructions.md). The current copy already includes it.

```text
plan.md
README.md (the original assignment instructions)
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
DRINKOO_Capstone_One_Pager.pdf
Database/schema.sql after UAT approval
Database/text2sql_samples.json after UAT approval
prompt.md after final system prompt is approved
Tests/ after the suite is green and reviewed
```

## Required Checks Before PR

- [x] App runs locally (`uvicorn Backend.app:app --reload --port 8000`).
- [x] Backend routes work (`/`, `/login`, `/signup`, `/chat`, `/upload`, `/status`, `/products`, `/promotions`).
- [x] Frontend pages render (smoke test via TestClient in `Tests/test_status.py`).
- [x] Database schema loads automatically on startup; `python scripts/seed_db.py` resets/seeds.
- [x] Text2SQL checks pass at 100% on the sample bank (>= 90% threshold).
- [x] RAG answers are grounded in DRINKOO data; faithfulness score >= 0.85.
- [x] OpenRouter prompt and free model name `nvidia/nemotron-3-ultra-550b-a55b:free` are saved in `prompt.md`.
- [x] Auth and protected routes return 401 unauthenticated, 200 when logged in.
- [x] Image upload validation rejects bad MIME, bad magic bytes, oversize files, and unauthenticated callers.
- [x] Tests pass: `pytest --cov=Backend` is green at 85% coverage.
- [x] Security test report is complete: `Reports/security-test-report.md`.
- [x] `git diff --stat HEAD` shows only expected changes (no UAT-locked file edits).

## Notes

- The OpenRouter API key is read from `.env` (`OPENROUTER_API_KEY`); the deterministic offline fallback in `Backend/rag/generator.py` keeps the chatbot grounded and the test suite reproducible when the key is absent.
- A small extension was made to the Text2SQL validator to add `SELECT` aliases to the allowlist after the first eval pass. The change is covered by `Tests/test_text2sql.py`.
- The `nvidia/nemotron-3-ultra-550b-a55b:free` model name is fixed across `prompt.md`, `.env.example`, `Backend/config.py`, status responses, and the footer of every HTML page.
