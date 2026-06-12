# DRINKOO Security Controls

This file documents the security controls baked into the DRINKOO application. The companion security test report lives at [`Reports/security-test-report.md`](../Reports/security-test-report.md).

## 1. Authentication and password handling

- Passwords are hashed with `bcrypt` at cost factor 12 via `passlib`. See [`Backend/security.py`](../Backend/security.py).
- Plain-text passwords are never logged or stored.
- The signup endpoint enforces a strength policy in `validate_password_strength`: at least 8 characters, at least one upper, one lower, and one digit.
- Login responses use a generic "Invalid email or password" error to prevent user enumeration.

## 2. Session and authorization

- Sessions ride on a signed JWT (`HS256`) stored in an HttpOnly, SameSite=Lax cookie named `drinkoo_session`. In non-local environments the cookie is also flagged `Secure`.
- Token TTL is 24 hours (configurable via `JWT_EXP_HOURS`).
- Protected routes (`/chat`, `/upload`, `/api/chat`, `/api/upload`, `/api/text2sql`) depend on `require_user`, which returns `401` if the token is missing or invalid.
- HTML protected pages redirect via the 401 handler to the login page.

## 3. Input validation

- All API request bodies are validated by Pydantic models with explicit `min_length`, `max_length`, and type constraints.
- Email addresses are validated by `email-validator`.
- The Text2SQL pipeline rejects any non-SELECT statement, forbidden keywords (INSERT/UPDATE/DELETE/DROP/ATTACH/PRAGMA/etc.), multiple statements, and any reference to a table or column outside the schema allowlist. See [`Backend/text2sql/validator.py`](../Backend/text2sql/validator.py).
- SQL is parsed by `sqlglot` and a `LIMIT` is injected if absent (cap 100 rows) before execution.

## 4. File upload safety

The upload endpoint at [`Backend/routers/upload.py`](../Backend/routers/upload.py) enforces:

- `Content-Type` allowlist (PNG, JPEG, WebP) and a separate extension allowlist.
- Magic-byte sniffing of the first 8 bytes to confirm the actual file format matches the declared MIME.
- Maximum file size 5 MB (configurable via `MAX_UPLOAD_MB`).
- Filenames are sanitized and replaced with `f"{user_id}_{uuid4().hex}{ext}"` to neutralize path traversal.
- The resolved path is verified to be inside `UPLOAD_DIR` before write.
- Uploaded files are served only through an authenticated endpoint, never via static mounting.
- Cross-user access is blocked: a non-admin user can only retrieve files prefixed with their own user id.

## 5. Prompt injection and RAG misuse

- The RAG generator wraps user context in delimiters and never grants the user any privileged instruction.
- [`Backend/rag/grounding.py`](../Backend/rag/grounding.py) implements `detect_injection` with regexes for common patterns ("ignore previous instructions", "reveal the system prompt", "developer mode", etc.) and the chat endpoint returns a logged refusal when triggered. This is covered by [`Tests/test_prompt_injection.py`](../Tests/test_prompt_injection.py).
- The chatbot only returns content that came from retrieved DRINKOO snippets and always attaches at least one citation. When retrieval is empty it surfaces the explicit "I don't have that information in the DRINKOO knowledge base yet." message.

## 6. Headers and transport

- Every HTTP response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Permissions-Policy` denying camera, mic, and geolocation.
- HTML responses additionally set a strict `Content-Security-Policy` (script-src 'self', no inline scripts, no third-party iframes).

## 7. Secret handling

- The OpenRouter API key is read from `OPENROUTER_API_KEY` in `.env` and never committed. `.env` is excluded by `.gitignore`. The `.env.example` documents the variable names.
- App secret, DB URL, and upload directory are all environment-driven via [`Backend/config.py`](../Backend/config.py).
- Log records strip secrets by design — the logger only records metadata such as `user_id`, `model`, `latency_ms`, `request_id`, and citation ids.

## 8. Dependency review

- Pinned versions in `requirements.txt`.
- Run `bandit -r Backend` for static security analysis.
- Run `pip-audit -r requirements.txt` for known vulnerable dependencies.

## 9. AI-generated code review

- Every AI-assisted change is reviewed by a human and runs through the test suite plus the PR evaluator. See [`ADLC/uat-protection.md`](../ADLC/uat-protection.md) for the NEVER_MODIFY list.
