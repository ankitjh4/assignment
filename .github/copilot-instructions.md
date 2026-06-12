# GitHub Copilot Instructions

These instructions apply to every Copilot-assisted change in the DRINKOO RAG Chatbot capstone repository.

## Project

We are building a Python-centric DRINKOO website for the CloudThat GitHub Copilot capstone. The stack is FastAPI + Jinja2 + vanilla CSS/JS + SQLite (via SQLAlchemy). The chatbot is a grounded retrieval-augmented generator wired to OpenRouter (`nvidia/nemotron-3-ultra-550b-a55b:free`) with a deterministic offline fallback. The full implementation plan lives in [`drinkoo_Impl_plan.md`](../../drinkoo_Impl_plan.md) at the repo root.

## AI Scope Statement (for the current capstone build)

In scope for AI assistance:

- `Backend/` application code (routers, RAG pipeline, Text2SQL pipeline, security utilities, logging).
- `Frontend/` templates, CSS, and JavaScript.
- `Database/schema.sql`, `Database/seed.sql`, `Database/text2sql_samples.json`, `Database/README.md`.
- `Tests/` unit, integration, and evaluation tests.
- `Observability/` notes and rollback runbook.
- `Security/security-controls.md`.
- `Reports/` evidence (security report, self-evaluation, scorecards).
- `scripts/seed_db.py`, `scripts/run_text2sql_eval.py`, `scripts/run_rag_eval.py`.
- `ADLC/` evidence files.

## NEVER_MODIFY

These files are UAT-locked. Copilot must never modify them without an explicit, human-reviewed change request:

```text
plan.md
README.md (the original assignment instructions)
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
DRINKOO_Capstone_One_Pager.pdf
.gitignore (only minor additions allowed)
Database/schema.sql after UAT approval
Database/text2sql_samples.json after UAT approval
prompt.md after final system prompt is approved
Tests/ after the suite is green and reviewed
```

## Coding constraints

1. Keep the app Python-centric. No large frontend framework.
2. Use FastAPI for the backend and Jinja2 for HTML.
3. Use bcrypt for password hashing. Never store or log plain-text passwords.
4. Use OpenRouter with the free model `nvidia/nemotron-3-ultra-550b-a55b:free`. The model name is fixed and must be referenced everywhere it appears.
5. Read `OPENROUTER_API_KEY` from environment via pydantic-settings; never commit secrets.
6. Save the final system prompt in `prompt.md`.
7. Save SQL table creation in `Database/schema.sql` and seed data in `Database/seed.sql`.
8. Protect chatbot, upload, and text2sql routes with `require_user`.
9. Validate image uploads (MIME, magic bytes, size, filename, path containment).
10. Add or update tests for every behavioral change. Do not delete existing passing tests.
11. Run the prompt-injection detector on every chat message before retrieval.

## Prompt Review Checklist

Before asking Copilot to generate code, confirm the prompt says:

1. What to build, in plain English.
2. Which files are in scope and which are NEVER_MODIFY.
3. What tests must pass, and which thresholds (Text2SQL >= 90%, RAG faithfulness >= 0.85).
4. Any security or schema constraints.

## Review Requirement

After every Copilot coding session, run:

```bash
git diff --stat HEAD
```

Confirm only expected files changed. If any UAT-locked file shows up in the diff, revert that part of the change and re-run the suite.
