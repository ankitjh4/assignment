# AI Scope Statement

This document captures the AI Scope Statement used for the DRINKOO RAG Chatbot capstone build.

## Task

Implement the complete DRINKOO capstone application from scratch: FastAPI backend, Jinja2 + CSS/JS frontend, SQLite database with 9 coherent tables and seed data, grounded RAG chatbot wired to OpenRouter (`nvidia/nemotron-3-ultra-550b-a55b:free`) with a deterministic offline fallback, Text2SQL pipeline (>= 90% correctness on a 14-question sample bank), authentication and protected image upload, status and observability evidence, security controls and report, and the ADLC artifacts required by the PR evaluator.

## Files in scope

```text
Backend/                              -- application code
Frontend/templates/, Frontend/static/ -- UI
Database/schema.sql                   -- schema
Database/seed.sql                     -- seed data
Database/text2sql_samples.json        -- Text2SQL eval bank
Database/README.md                    -- DB usage notes
Tests/                                -- unit, integration, eval tests
Observability/                        -- monitoring notes + rollback runbook
Security/security-controls.md         -- security controls write-up
Reports/                              -- evaluation evidence
scripts/seed_db.py, scripts/run_text2sql_eval.py, scripts/run_rag_eval.py
ADLC/ai-scope-statement.md, ADLC/prompt-review-checklist.md, ADLC/uat-protection.md
.github/copilot-instructions.md
.env.example
requirements.txt
pytest.ini
prompt.md
```

## Files out of scope

```text
scripts/evaluate_submission.py    -- UAT-locked grader; never edit
.github/workflows/pr-evaluation.yml -- UAT-locked CI gate
plan.md                            -- original assignment plan
README.md                          -- original assignment instructions (we only append a How-To-Run section)
DRINKOO_Capstone_One_Pager.pdf     -- assignment PDF
```

## UAT-Locked Items

The list mirrors [`ADLC/uat-protection.md`](uat-protection.md):

```text
scripts/evaluate_submission.py
.github/workflows/pr-evaluation.yml
plan.md
DRINKOO_Capstone_One_Pager.pdf
Database/schema.sql once tests are green
Database/text2sql_samples.json once tests are green
prompt.md after the final system prompt is reviewed
Tests/ after the suite is green and reviewed
```

## Test Requirements

Every behavioral change must be covered by tests under `Tests/`. Coverage thresholds and evals required for this capstone:

- `pytest` overall suite green.
- Schema test confirms all 9 tables exist and seed data is loaded.
- Auth tests cover signup, login, logout, weak-password rejection, and protected-route 401.
- Upload tests cover happy path, missing auth, wrong content type, wrong magic bytes, and size limit.
- Chat tests cover grounded answer with citation, unknown-question refusal, and prompt-injection refusal.
- `Tests/test_text2sql.py` enforces correctness >= 90%.
- `Tests/test_rag_eval.py` enforces average faithfulness >= 0.85.
- Coverage report written to `Reports/coverage.txt`.

## Review Notes

After the build is complete the developer runs:

```bash
git diff --stat HEAD
```

and confirms that no UAT-locked file appears in the diff. The PR evaluator (`scripts/evaluate_submission.py`) is run against `assignment/` and must report at least 90/100. The current build hits 100/100 on the evaluator and the local test suite is green.
