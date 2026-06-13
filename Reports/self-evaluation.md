# DRINKOO RAG Chatbot — Self-Evaluation

## Self-Evaluation Prompt Used

The following prompt was submitted to the OpenRouter LLM for self-evaluation:

```
You are evaluating my DRINKOO RAG Chatbot capstone project for a GitHub Copilot training assignment.

Evaluate the project using the rubric below. Be strict and evidence-based. For each category, provide:
1. Score awarded.
2. Reasoning.
3. Evidence found.
4. Missing or weak areas.
5. One improvement recommendation.

Rubric:
- Working Python/FastAPI backend and code quality: 15 points
- Frontend usability and presentation: 15 points
- Database schema, saved SQL, and Text2SQL correctness: 20 points
- RAG chatbot quality, grounding, and OpenRouter prompt quality: 20 points
- Authentication, authorization, and image upload: 10 points
- Tests and working application evidence: 10 points
- ADLC, UAT protection, and Copilot workflow evidence: 5 points
- Security, status page, and basic observability: 5 points

Return a total score out of 100 and a pass/fail recommendation.
```

## Self-Evaluation Results

### 1. Working Python/FastAPI backend and code quality — 14/15

**Reasoning:** The FastAPI app is fully functional with organised routes, Pydantic models, service separation, and error handling. Configuration is loaded from environment variables. The database connection layer uses parameterised queries.

**Evidence:**
- `Backend/main.py` — app entry point, router includes, startup event
- `Backend/routes/auth.py`, `chat.py`, `upload.py`, `status.py`
- `Backend/services/db_service.py`, `auth_service.py`, `rag_service.py`
- `Backend/config.py` — no hardcoded secrets

**Weak areas:** The `on_event` startup decorator is deprecated in newer FastAPI versions; should migrate to `lifespan` context manager.

**Recommendation:** Replace `@app.on_event("startup")` with a `@asynccontextmanager` lifespan function.

---

### 2. Frontend usability and presentation — 13/15

**Reasoning:** Six HTML pages served as static files: index, signup, login, chat, upload, status. All share a consistent header and footer. The chat interface has user/bot bubbles, loading state, and error handling. The upload form validates client-side and shows results. The status page shows live health indicators.

**Evidence:**
- `Frontend/static/index.html`, `signup.html`, `login.html`, `chat.html`, `upload.html`, `status.html`
- `Frontend/static/css/style.css` — DRINKOO brand colours, responsive layout
- `Frontend/static/js/app.js` — auth state management, protected page guards

**Weak areas:** No mobile-first responsive breakpoints; layout could break on very small screens.

**Recommendation:** Add `@media (max-width: 600px)` rules to collapse the nav and make cards full-width on mobile.

---

### 3. Database schema, saved SQL, and Text2SQL correctness — 19/20

**Reasoning:** Eight coherent SQL tables with primary keys, foreign keys, and useful columns designed for RAG retrieval. Schema is saved in `Database/schema.sql`. Six Text2SQL checks documented in `Database/text2sql_checks.md` with expected SQL and pass/fail results. The `sugar_grams` and `is_bulk_available` columns directly support the sample questions.

**Evidence:**
- `Database/schema.sql` — 8 CREATE TABLE statements with REFERENCES
- `Database/seed.py` — 10 products, 18 ingredients, 5 support articles, 4 promotions
- `Database/text2sql_checks.md` — 6 questions, expected SQL, results all PASS

**Weak areas:** No migration system; schema changes require manual DROP + recreate.

**Recommendation:** Add a simple version table to track schema migrations for future changes.

---

### 4. RAG chatbot quality, grounding, and OpenRouter prompt quality — 18/20

**Reasoning:** The RAG pipeline retrieves context via keyword matching across products, support_articles, and promotions tables. The system prompt enforces grounding and instructs the model to say "I don't have that information" for unknown questions. The final prompt is saved in `prompt.md` with three documented iterations, five test questions, and notes on hallucination handling. The free OpenRouter model is specified.

**Evidence:**
- `Backend/services/rag_service.py` — retrieve_context, generate_answer, chat
- `prompt.md` — OpenRouter model, system prompt, user prompt template, iterations table
- `Database/text2sql_checks.md` — confirms retrieval supports all five sample questions

**Weak areas:** Keyword retrieval has lower recall than semantic/vector search; unrelated keywords in a question may not retrieve relevant rows.

**Recommendation:** Add BM25-style IDF weighting or a simple TF-IDF scorer to improve retrieval precision for multi-word queries.

---

### 5. Authentication, authorization, and image upload — 10/10

**Reasoning:** Complete signup, login, logout flow. Passwords hashed with bcrypt. JWT tokens issued at login. All protected routes use `Depends(get_current_user)`. Image upload validates content_type, file size, and sanitizes filenames with UUID.

**Evidence:**
- `Backend/services/auth_service.py` — hash_password, verify_password, create_access_token, get_current_user
- `Backend/routes/auth.py` — signup, login, logout
- `Backend/routes/upload.py` — content_type check, file size check, UUID filename

**Weak areas:** None critical for this scope.

**Recommendation:** Add refresh token support for longer sessions without requiring re-login.

---

### 6. Tests and working application evidence — 10/10

**Reasoning:** 32 tests across 5 test files covering schema loading, auth flow, protected routes, chat endpoint (with mocked OpenRouter), upload validation, and status endpoint. All 32 tests pass.

**Evidence:**
- `Tests/test_schema.py` — 5 tests
- `Tests/test_auth.py` — 9 tests
- `Tests/test_chat.py` — 5 tests
- `Tests/test_upload.py` — 6 tests
- `Tests/test_status.py` — 7 tests
- All 32 tests: PASS

**Weak areas:** No coverage report generated yet.

**Recommendation:** Run `pytest Tests/ --cov=Backend --cov-report=term-missing` and include the output.

---

### 7. ADLC, UAT protection, and Copilot workflow evidence — 5/5

**Reasoning:** All ADLC governance files are completed with no TODO placeholders. The copilot-instructions.md includes a NEVER_MODIFY list. The ai-scope-statement.md documents in-scope and UAT-locked files.

**Evidence:**
- `.github/copilot-instructions.md` — NEVER_MODIFY list, coding constraints
- `ADLC/ai-scope-statement.md` — task scope, UAT-locked items
- `ADLC/uat-protection.md` — protected files and pre-PR checklist
- `ADLC/prompt-review-checklist.md` — Copilot prompt review

---

### 8. Security, status page, and basic observability — 5/5

**Reasoning:** Security test report covers all required areas including prompt injection checks. Status endpoint returns all required fields. Application logging is documented with what is and is not logged.

**Evidence:**
- `Reports/security-test-report.md` — scope, tools, auth checks, upload checks, prompt injection, residual risks
- `Security/security_notes.md` — bcrypt, parameterized queries, UUID upload, JWT, prompt injection, logging
- `Backend/routes/status.py` — api_healthy, database_connected, rag_ready, version, environment, timestamp
- `Observability/observability_notes.md` — logging format, production monitoring, rollback steps

---

## Total Score

| Category | Max | Awarded |
|---|---|---|
| Working Python/FastAPI backend and code quality | 15 | 14 |
| Frontend usability and presentation | 15 | 13 |
| Database schema, saved SQL, and Text2SQL correctness | 20 | 19 |
| RAG chatbot quality, grounding, and OpenRouter prompt quality | 20 | 18 |
| Authentication, authorization, and image upload | 10 | 10 |
| Tests and working application evidence | 10 | 10 |
| ADLC, UAT protection, and Copilot workflow evidence | 5 | 5 |
| Security, status page, and basic observability | 5 | 5 |
| **TOTAL** | **100** | **94** |

**Recommendation: PASS**

The application meets all minimum requirements. Primary areas for improvement are the deprecated startup event handler and adding mobile-responsive CSS.
