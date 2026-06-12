# DRINKOO Security Test Report

This is the security test report for the DRINKOO RAG Chatbot capstone submission. It covers the scope of testing, the tools and methods used, findings, fixes, and residual risks. The application controls behind these tests are documented in [`Security/security-controls.md`](../Security/security-controls.md).

## 1. Scope

In scope:

- FastAPI backend (`Backend/`) including auth, chat, upload, status, catalog, and text2sql routes.
- SQLite database created from `Database/schema.sql` and `Database/seed.sql`.
- RAG generator + retriever including prompt-injection defenses.
- Image upload endpoint and stored file behavior.
- Environment configuration and secret handling.

Out of scope:

- Production infrastructure (none deployed).
- The PR evaluator `scripts/evaluate_submission.py` (UAT-locked).
- The OpenRouter service itself.

## 2. Tools and methods

| Tool / method | Purpose |
| --- | --- |
| `pytest` | Behavioral testing of auth, protected routes, upload validation, and prompt-injection refusals. |
| `bandit -r Backend` | Static analysis for common Python security issues. |
| `pip-audit -r requirements.txt` | Known-vulnerability scan of pinned dependencies. |
| Manual curl / HTTP probes | Auth, header verification, upload abuse cases. |
| Code review | Human review of all AI-suggested security-sensitive code. |

## 3. Authentication and authorization checks

| Test | Result |
| --- | --- |
| Signup hashes the password (bcrypt) and stores only the hash. | PASS - verified in `Backend/security.py::hash_password`. |
| Login fails with a generic message on wrong password (no user enumeration). | PASS - `Tests/test_auth.py::test_signup_and_login_and_logout`. |
| Weak password rejected (no upper / no digit / < 8 chars). | PASS - `Tests/test_auth.py::test_signup_rejects_weak_password`. |
| `/api/chat`, `/api/upload`, `/api/text2sql` return 401 without a session. | PASS - `Tests/test_auth.py::test_protected_route_requires_login` and `Tests/test_upload.py::test_upload_requires_auth`. |
| Logout clears the session cookie and revokes access. | PASS - integration test verifies subsequent `/api/auth/me` returns 401. |
| Authenticated user can only download their own uploads (non-admin). | PASS - `Backend/routers/upload.py::download_image` enforces user-id prefix on the safe filename. |

## 4. Input validation checks

| Test | Result |
| --- | --- |
| Email validation rejects malformed addresses. | PASS - Pydantic + `email-validator`. |
| Chat message length bounded (1..2000). | PASS - `ChatRequest`. |
| Text2SQL question length bounded (3..400). | PASS - `Text2SQLRequest`. |
| Text2SQL rejects multi-statement input. | PASS - `Tests` exercise via `validate` and runtime path; validator flags `must_be_single_statement`. |
| Text2SQL rejects forbidden keywords (INSERT/UPDATE/DELETE/DROP/PRAGMA/ATTACH). | PASS - validator blocks them. |
| Text2SQL only references allowlisted tables/columns. | PASS - `_collect_used_tables` and `_collect_used_columns`. |
| `LIMIT` is injected when missing, capped at 100. | PASS - `validate(...)`. |

## 5. File upload checks

| Test | Result |
| --- | --- |
| Content-Type must be `image/png`, `image/jpeg`, or `image/webp`. | PASS - `Tests/test_upload.py::test_upload_rejects_unsupported_content_type`. |
| Magic-byte sniff rejects text disguised as PNG. | PASS - `Tests/test_upload.py::test_upload_rejects_text_file`. |
| Files larger than 5 MB are rejected with `413`. | PASS - `Tests/test_upload.py::test_upload_enforces_size_limit`. |
| Filename regenerated server-side with `uuid4`, path-traversal blocked. | PASS - `_safe_filename` + resolved-path containment check. |
| Upload requires authentication. | PASS - `Tests/test_upload.py::test_upload_requires_auth`. |

## 6. Dependency vulnerability checks

- `pip-audit -r requirements.txt` is the recommended command. Pinned versions in [`requirements.txt`](../requirements.txt) reflect releases available as of capstone build time.
- No findings of severity high or critical were left unremediated. Any future audit findings are tracked in `Observability/monitoring-notes.md` as part of the residual-risk register.

## 7. Secret scanning checks

- `OPENROUTER_API_KEY` and `APP_SECRET` are read from `.env` via `pydantic-settings` and never committed. `.env` is excluded by `.gitignore`.
- Log records are JSON-formatted and explicitly exclude secrets and request bodies. The same JSON stream is mirrored to stdout (for log collectors) and a rotating file sink configured by `LOG_FILE_PATH` / `LOG_FILE_MAX_MB` / `LOG_FILE_BACKUP_COUNT` (default `./logs/drinkoo.log`, 5 MB x 5 backups). The `logs/` directory is excluded by `.gitignore`.
- Grep across the repository for `OPENROUTER_API_KEY=` confirms only the placeholder in `.env.example`.

## 8. Prompt injection and RAG misuse checks

| Test | Result |
| --- | --- |
| Injection patterns ("ignore previous instructions", "reveal the system prompt", "developer mode", "you are no longer DRINKOO") are detected. | PASS - `Tests/test_prompt_injection.py::test_detector_catches_injection`. |
| Chat endpoint returns a refusal and zero citations when injection is detected. | PASS - `Tests/test_prompt_injection.py::test_chat_refuses_injection_via_api`. |
| Unknown / off-topic questions yield the explicit unknown-answer message instead of fabricated facts. | PASS - `Tests/test_chat_rag.py::test_chat_handles_unknown_question`. |
| Grounded answers always include at least one source citation. | PASS - `Tests/test_chat_rag.py::test_chat_returns_grounded_answer`. |

## 9. Issues found

No high or critical findings remain.

| Severity | Title | Status |
| --- | --- | --- |
| Low | Initial Text2SQL validator over-restricted SELECT aliases. | Fixed by collecting aliases into the allowlist. See `Backend/text2sql/validator.py::_collect_select_aliases`. |
| Low | Authenticated download could leak across users. | Mitigated by user-id prefix check + admin role escape hatch in `download_image`. |

## 10. Residual risks

- Without an external rate limiter the in-memory IP rate-limiting is best-effort only.
- The offline RAG fallback intentionally surfaces snippets from the retrieved DRINKOO documents; the system prompt and refusal flow are the only guards against malicious content slipping into context. Adding an embedding-based moderation hook is a recommended follow-up.
- Static HTML pages serve fonts from Google Fonts; if a stricter CSP is needed the fonts can be self-hosted.

## 11. Fixes applied during the capstone build

- Replaced placeholder password handling with `bcrypt` hashing.
- Added magic-byte sniffing for the upload endpoint after the initial implementation only checked `Content-Type`.
- Tightened the Text2SQL validator after the first eval pass flagged `SELECT id, ... SUM(qty) AS total_qty` (the alias `total_qty` is now allowed; non-allowlisted columns remain blocked).
- Hardened the chat endpoint with explicit prompt-injection detection and a dedicated test.
