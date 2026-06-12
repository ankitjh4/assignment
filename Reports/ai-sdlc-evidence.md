# DRINKOO AI-Assisted SDLC Evidence

This file captures concise evidence that GitHub Copilot was used across the software delivery lifecycle for the DRINKOO RAG Chatbot capstone. Each entry summarises the activity, the prompt or scope, and the resulting artifact.

## Planning

- Activity: Drafted the capstone implementation plan covering scope, repo layout, schema, RAG pipeline, Text2SQL safety, frontend design, observability, security, and ADLC artifacts.
- Prompt scope: build a Python-centric DRINKOO website with grounded RAG and strong Text2SQL behavior; keep the OpenRouter model name pinned to `nvidia/nemotron-3-ultra-550b-a55b:free`; honor the PR evaluator constraints.
- Artifact: [`drinkoo_Impl_plan.md`](../../drinkoo_Impl_plan.md) at the repo root.

## Backend implementation

- Activity: Generated FastAPI app factory with security headers, request-id middleware, structured JSON logging, error handlers, and routers for auth, chat, upload, status, catalog, text2sql, and pages.
- Prompt scope: implement FastAPI auth (bcrypt + JWT cookie), grounded RAG endpoint with citations, Text2SQL endpoint with sqlglot safety, and image upload validation. Read OpenRouter key from env. Do not modify the PR evaluator.
- Artifact: [`Backend/`](../Backend/).

## Frontend implementation

- Activity: Generated Jinja2 templates plus vanilla CSS and JS for a beverage-themed UI with home, signup, login, chat (citations panel), upload (drag-and-drop), status (live), products (filtered grid), and promotions pages.
- Prompt scope: simple HTML/CSS/JS frontend with a creative DRINKOO brand identity; no large framework; cite sources visibly on chat answers.
- Artifact: [`Frontend/templates/`](../Frontend/templates/), [`Frontend/static/`](../Frontend/static/).

## Database design

- Activity: Designed a 9-table schema covering users, products, ingredients, product_ingredients, orders, order_items, promotions, support_articles, and chat_sessions; seeded ~20 products and supporting rows; authored a 14-question Text2SQL sample bank with row-signature comparisons.
- Prompt scope: at least six coherent tables, useful for grounded RAG, supporting >= 90% Text2SQL correctness.
- Artifacts: [`Database/schema.sql`](../Database/schema.sql), [`Database/seed.sql`](../Database/seed.sql), [`Database/text2sql_samples.json`](../Database/text2sql_samples.json).

## Test generation

- Activity: Generated unit and integration tests for schema, auth, chat (grounded answer, refusal, unknown question), upload (auth, MIME, magic bytes, size), status, Text2SQL >= 90%, RAG faithfulness >= 0.85, and prompt-injection refusal.
- Prompt scope: tests must run under `pytest` with a fresh SQLite per session; never delete existing passing tests; cover all rubric paths.
- Artifact: [`Tests/`](../Tests/), result snapshot in [`Reports/coverage.txt`](coverage.txt).

## Security review

- Activity: Wrote the security controls write-up and the security test report; added the prompt-injection detector and dedicated tests; hardened the upload endpoint with magic-byte sniffing and path containment.
- Prompt scope: cover OWASP-flavored risks: broken access control, injection, weak auth, file upload, exposed secrets, prompt injection.
- Artifacts: [`Security/security-controls.md`](../Security/security-controls.md), [`Reports/security-test-report.md`](security-test-report.md), [`Backend/rag/grounding.py`](../Backend/rag/grounding.py), [`Tests/test_prompt_injection.py`](../Tests/test_prompt_injection.py).

## Debugging

- Activity: Resolved three issues mid-build.
  1. The `email-validator` library rejected the `.test` TLD, which is reserved. Updated tests to use `example.com` addresses.
  2. The Text2SQL validator initially flagged the `SUM(qty) AS total_qty` alias as an unknown column. Extended `_collect_select_aliases` so any aliased output is added to the allowed set. Eval lifted from 92.9% to 100%.
  3. Logs were only streaming to stdout, so they weren't durable across restarts. Added a rotating file sink (`LOG_FILE_PATH`, default `./logs/drinkoo.log`, 5 MB x 5 backups) alongside the existing stdout handler. On startup the app emits a `logging_file_sink_ready` event with the resolved path.
- Prompt scope: minimal, targeted, reversible fixes; never modify the PR evaluator or any UAT-locked file.

## Documentation

- Activity: Wrote `prompt.md` (model, system prompt, user template, three iterations, ten test questions), ADLC artifacts, capstone scorecard, self-evaluation, monitoring notes, and rollback runbook.
- Prompt scope: every required evidence file must be fully filled and contain no placeholder text so the PR evaluator's filled-file check passes.
- Artifacts: [`prompt.md`](../prompt.md), [`ADLC/`](../ADLC/), [`Reports/`](.), [`Observability/`](../Observability/).

## Review and git hygiene

- Activity: After each Copilot-assisted session, the developer runs `git diff --stat HEAD` and confirms that no UAT-locked file appears in the diff. The session ends only when:
  - `pytest --cov=Backend` is green at >= 80% coverage.
  - `python scripts/run_text2sql_eval.py` reports >= 90%.
  - `python scripts/run_rag_eval.py` reports >= 0.85.
  - `python scripts/evaluate_submission.py --repo . --min-score 90` returns 0.
