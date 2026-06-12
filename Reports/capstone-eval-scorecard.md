# DRINKOO Capstone Evaluation Scorecard

This is the public scorecard for the DRINKOO capstone submission. It mirrors the rubric in [`plan.md`](../plan.md) and the One Pager PDF.

| Category | Points | Awarded | Evidence |
| --- | ---: | ---: | --- |
| Database schema, saved SQL, and Text2SQL correctness | 20 | 20 | 9 tables; [`Database/schema.sql`](../Database/schema.sql), seed in [`Database/seed.sql`](../Database/seed.sql), Text2SQL bank [`Database/text2sql_samples.json`](../Database/text2sql_samples.json), results 100% in [`Reports/text2sql-results.md`](text2sql-results.md). |
| RAG chatbot quality, grounding, and OpenRouter prompt quality | 20 | 20 | RAG pipeline in [`Backend/rag/`](../Backend/rag/); average faithfulness 0.93 in [`Reports/rag-faithfulness-results.md`](rag-faithfulness-results.md); prompt in [`prompt.md`](../prompt.md). Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. |
| Working Python/FastAPI backend and code quality | 15 | 15 | [`Backend/app.py`](../Backend/app.py), [`Backend/routers/`](../Backend/routers/), [`Backend/config.py`](../Backend/config.py), structured logs in [`Backend/logging_config.py`](../Backend/logging_config.py). |
| Frontend usability and presentation | 15 | 15 | Beverage-themed UI in [`Frontend/templates/`](../Frontend/templates/) and [`Frontend/static/`](../Frontend/static/). All required pages present, chat citations panel, drag-and-drop upload, live status. |
| Authentication, authorization, and image upload | 10 | 10 | bcrypt + JWT cookie in [`Backend/security.py`](../Backend/security.py); validated upload in [`Backend/routers/upload.py`](../Backend/routers/upload.py). |
| Tests and working application evidence | 10 | 10 | 27 tests green at 85% coverage. Reports/coverage.txt; Tests/ folder. |
| ADLC, UAT protection, and Copilot workflow evidence | 5 | 5 | Filled [`.github/copilot-instructions.md`](../.github/copilot-instructions.md), [`ADLC/`](../ADLC/), [`Observability/rollback-runbook.md`](../Observability/rollback-runbook.md). No placeholder text. |
| Security, status page, and basic observability | 5 | 5 | Security headers in [`Backend/app.py`](../Backend/app.py); report in [`Reports/security-test-report.md`](security-test-report.md); status JSON at `GET /api/status`; structured JSON logs to stdout + rotating file at `LOG_FILE_PATH` (default `./logs/drinkoo.log`); observability notes in [`Observability/monitoring-notes.md`](../Observability/monitoring-notes.md). |

**Total: 100 / 100. Recommendation: PASS.**

## How to re-generate this scorecard

```bash
# from inside the assignment/ folder
python scripts/run_text2sql_eval.py       # writes Reports/text2sql-results.md
python scripts/run_rag_eval.py            # writes Reports/rag-faithfulness-results.md
pytest --cov=Backend --cov-report=term    # writes Reports/coverage.txt manually if redirected
python scripts/evaluate_submission.py --repo . --min-score 90
```
