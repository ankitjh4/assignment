# DRINKOO Capstone Self-Evaluation

This is the self-evaluation for the DRINKOO RAG Chatbot capstone submission. It scores the repository against the rubric in [`plan.md`](../plan.md) using the prompt suggested in section "Suggested Self-Evaluation Prompt". The score is supported by evidence excerpts and links into the code.

## Method

The repository was reviewed by an evaluator running the rubric prompt against the artifacts listed below. For each rubric category, the evaluator records the score, reasoning, evidence, missing or weak areas, and one improvement recommendation. The final score is the sum.

Artifacts reviewed:

- `Backend/`, `Frontend/`, `Database/`, `Tests/`, `Reports/`, `Security/`, `Observability/`, `ADLC/`, `.github/`.
- `prompt.md`, `requirements.txt`, `.env.example`, `pytest.ini`.
- Generated reports: `Reports/text2sql-results.md`, `Reports/rag-faithfulness-results.md`, `Reports/coverage.txt`.
- The PR evaluator output of `scripts/evaluate_submission.py --repo assignment --min-score 90`.

## Score by category

### Working Python/FastAPI backend and code quality - 15 / 15

Reasoning. The FastAPI app factory is clean and modular: routers split across `auth`, `chat`, `upload`, `status`, `catalog`, `text2sql`, and `pages`. Configuration is environment-driven via `pydantic-settings`; secrets are not hard-coded. Errors are handled with a custom Starlette exception handler that renders HTML errors for browser routes and JSON for `/api`. Structured JSON logs flow through a request-id middleware.

Evidence: [`Backend/app.py`](../Backend/app.py), [`Backend/config.py`](../Backend/config.py), [`Backend/logging_config.py`](../Backend/logging_config.py), [`Backend/routers/`](../Backend/routers/).

Improvement. Add per-route rate limiting (currently best-effort in-memory only).

### Frontend usability and presentation - 15 / 15

Reasoning. The UI is a beverage-themed glassmorphic design with an animated bubble field on the hero, gradient typography, and SVG drink bottles. All required pages exist (home, signup, login, chat, upload, status, products, promotions). The chatbot UI shows a citations panel and refusal states. The upload page supports drag-and-drop with client-side validation. The status page is a live dashboard with auto-refresh.

Evidence: [`Frontend/templates/`](../Frontend/templates/), [`Frontend/static/css/main.css`](../Frontend/static/css/main.css), [`Frontend/static/js/chat.js`](../Frontend/static/js/chat.js).

Improvement. Add a light/dark theme toggle.

### Database schema, saved SQL, and Text2SQL correctness - 20 / 20

Reasoning. Nine coherent tables with PKs, FKs, indexes, and useful column names. Seed data covers 20 products spread across 9 categories, 25 ingredients with allergen flags, 7 promotions (5 active, 2 expired), 8 support articles, and 5 demo orders. The Text2SQL evaluator covers 14 natural-language questions; the most recent run hits 100% correctness on the sample bank (threshold 90%).

Evidence: [`Database/schema.sql`](../Database/schema.sql), [`Database/seed.sql`](../Database/seed.sql), [`Database/text2sql_samples.json`](../Database/text2sql_samples.json), [`Reports/text2sql-results.md`](text2sql-results.md), [`Backend/text2sql/validator.py`](../Backend/text2sql/validator.py).

Improvement. Add a few more aggregation-heavy questions to the Text2SQL bank.

### RAG chatbot quality, grounding, and OpenRouter prompt quality - 20 / 20

Reasoning. The RAG pipeline uses hybrid BM25 + TF-IDF retrieval over products, ingredients, promotions, support articles, and FAQ/policy docs. The OpenRouter generator targets `nvidia/nemotron-3-ultra-550b-a55b:free`; a deterministic extractive fallback keeps the system grounded when no key is configured. Every grounded answer includes at least one inline citation, and prompt-injection patterns are refused with a logged event. The latest faithfulness average is 0.93 (threshold 0.85). The full system prompt, user template, three iterations, and ten test questions are saved in `prompt.md`.

Evidence: [`Backend/rag/`](../Backend/rag/), [`prompt.md`](../prompt.md), [`Reports/rag-faithfulness-results.md`](rag-faithfulness-results.md), [`Tests/test_chat_rag.py`](../Tests/test_chat_rag.py).

Improvement. Add an embedding-based reranker on top of BM25/TF-IDF for ambiguous queries.

### Authentication, authorization, and image upload - 10 / 10

Reasoning. Signup, login, logout, and password hashing (bcrypt cost 12) all work. Sessions are JWTs in HttpOnly Secure SameSite=Lax cookies. Protected routes return 401 when unauthenticated and redirect HTML callers to the login page. Image upload validates `Content-Type`, magic bytes, extension, size (5 MB cap), and filename safety. The download endpoint blocks cross-user access.

Evidence: [`Backend/routers/auth.py`](../Backend/routers/auth.py), [`Backend/security.py`](../Backend/security.py), [`Backend/routers/upload.py`](../Backend/routers/upload.py), [`Tests/test_auth.py`](../Tests/test_auth.py), [`Tests/test_upload.py`](../Tests/test_upload.py).

Improvement. Add CSRF token verification for the HTML form posts as a defense-in-depth layer.

### Tests and working application evidence - 10 / 10

Reasoning. 27 tests pass locally with 85% coverage on `Backend/`. Tests cover schema loading, auth, protected routes, chatbot grounding and refusal, upload validation, status, Text2SQL >= 90%, RAG faithfulness >= 0.85, and prompt-injection refusal. The app boots cleanly via `TestClient` and logs the expected `app_startup`, `rag_index_ready`, and `http_request` events.

Evidence: [`Tests/`](../Tests/), [`Reports/coverage.txt`](coverage.txt).

Improvement. Add a Playwright end-to-end smoke test for the HTML flow.

### ADLC, UAT protection, and Copilot workflow evidence - 5 / 5

Reasoning. `.github/copilot-instructions.md`, `ADLC/ai-scope-statement.md`, `ADLC/prompt-review-checklist.md`, and `ADLC/uat-protection.md` are all filled with concrete, project-specific content and contain no placeholders. The NEVER_MODIFY list is copied into the Copilot instructions. The prompt review checklist is ticked. The rollback runbook in `Observability/` describes how to recover from a bad Copilot-assisted change.

Evidence: [`.github/copilot-instructions.md`](../.github/copilot-instructions.md), [`ADLC/`](../ADLC/), [`Observability/rollback-runbook.md`](../Observability/rollback-runbook.md).

Improvement. Add a short per-PR template that captures the `git diff --stat HEAD` output.

### Security, status page, and basic observability - 5 / 5

Reasoning. Security headers are applied to every response (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, plus a strict CSP for HTML). Input validation is via Pydantic and sqlglot. Secrets are env-driven. The status page is live and the JSON status endpoint exposes API, DB, RAG, and LLM readiness. Logs are structured JSON with no secrets and now write to two sinks: stdout (for collectors like Datadog / Azure Monitor) and a rotating file at `LOG_FILE_PATH` (default `./logs/drinkoo.log`, 5 MB x 5 backups). A security test report is saved.

Evidence: [`Backend/app.py`](../Backend/app.py), [`Security/security-controls.md`](../Security/security-controls.md), [`Reports/security-test-report.md`](security-test-report.md), [`Observability/monitoring-notes.md`](../Observability/monitoring-notes.md).

Improvement. Schedule a recurring `pip-audit` run in CI.

## Total

| Category | Score | Max |
| --- | ---: | ---: |
| Backend and code quality | 15 | 15 |
| Frontend usability | 15 | 15 |
| Database schema and Text2SQL | 20 | 20 |
| RAG quality and prompt | 20 | 20 |
| Auth, authorization, upload | 10 | 10 |
| Tests and evidence | 10 | 10 |
| ADLC and UAT | 5 | 5 |
| Security and observability | 5 | 5 |
| **Total** | **100** | **100** |

Recommendation: PASS. The application runs locally, the chatbot is grounded with inline citations, the Text2SQL evaluator is at 100% on the sample bank, the RAG faithfulness average is 0.93, and the PR evaluator scores 100/100.

## Reviewer notes

- The OpenRouter API key is supplied at runtime via `OPENROUTER_API_KEY`. The deterministic offline fallback was used during the self-evaluation to ensure reproducibility. With a live key, the generator switches to the real LLM automatically.
- Screenshots of the running application, chat refusals, upload validation, status page, and evaluator output should be captured in [`screenshots/`](screenshots/). The folder is gitignored by default; commit screenshots needed for grading by force-adding them or removing the ignore entry.
