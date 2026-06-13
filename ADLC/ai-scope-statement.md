# AI Scope Statement

Complete this before using GitHub Copilot for a coding session.

## Task

Build the complete DRINKOO RAG chatbot website from scratch on the provided scaffold. This includes the FastAPI backend, SQLite database, RAG retrieval service, OpenRouter integration, HTML/CSS/JS frontend, pytest test suite, security report, and observability notes.

## Files In Scope

Files and folders Copilot may help modify:

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

## Files Out Of Scope

Files and folders Copilot must not modify:

```text
plan.md
README.md
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
.gitignore
.env.example
DRINKOO_Capstone_One_Pager.pdf
```

## UAT-Locked Items

Once approved and tested, the following are UAT-locked and must not be changed without explicit review:

```text
Database/schema.sql (after first successful test run)
Tests/conftest.py (after all 32 tests pass)
Backend/config.py (secrets handling — human review required for any change)
prompt.md (after final OpenRouter prompt is approved)
```

## Test Requirements

For every change made during this build session:
- All 32 tests in `Tests/` must continue to pass
- `python scripts/evaluate_submission.py --repo . --min-score 70` must pass
- New routes or services must have corresponding tests added or updated

## Review Notes

After the coding session, `git diff --stat HEAD` was reviewed. Changes are confined to the component folders (Backend, Frontend, Database, Tests, Reports, Security, Observability) and root-level files (requirements.txt, prompt.md). No scaffold, workflow, or evaluation files were modified.
