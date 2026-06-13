# DRINKOO Security Notes

## Authentication Controls

Password hashing uses the `bcrypt` library directly (rounds=12 default). Passwords are never stored in plain text. The `hash_password` and `verify_password` functions in `Backend/services/auth_service.py` handle all password operations.

JWT tokens are signed with `python-jose` using HS256 and expire after 60 minutes. The secret key is loaded from the environment variable `SECRET_KEY`; it is never hard-coded in source code.

## Input Validation

All request bodies are validated by Pydantic models before any route handler runs. Email format is validated with a regex in `UserCreate.validate_email_format`. Invalid inputs return HTTP 422 automatically by FastAPI.

File upload validation (`Backend/routes/upload.py`) checks:
- `content_type` must be one of `image/jpeg`, `image/png`, `image/gif`, `image/webp`
- File size must not exceed `MAX_UPLOAD_BYTES` (default 5 MB)

## Secret Handling

All secrets (`OPENROUTER_API_KEY`, `SECRET_KEY`) are loaded via `python-dotenv` from a `.env` file. The `.env` file is in `.gitignore`. Only `.env.example` (with placeholder values) is committed to the repository.

No API keys, passwords, or private keys appear anywhere in the source code.

## SQL Injection Prevention

All database queries use parameterised statements with `sqlite3`'s `?` placeholder syntax. The `execute_query`, `execute_one`, and `execute_write` helpers in `Backend/services/db_service.py` always accept a `params` tuple — raw string interpolation into SQL is never used.

## File Upload Safety

Uploaded filenames from the client are never used directly. The server generates a new filename as `uuid4().hex + original_extension`. This prevents:
- Path traversal attacks (`../../../etc/passwd`)
- Filename collisions
- Executable file injection via misleading extensions

Files are stored in the `uploads/` directory which is excluded from version control via `.gitignore`.

## Prompt Injection Checks

User input (the chat question) is inserted into the `user` role message only. It never appears in the `system` role prompt, which is a fixed string defined in `rag_service.py`. This limits the attack surface for prompt injection — a malicious user cannot overwrite the grounding instructions.

The system prompt explicitly instructs the model to answer only from retrieved context and to refuse unrelated questions. This reduces the risk of prompt injection leading to policy bypass.

## Observability and Logging

Application logs use Python's `logging` module with `INFO` level. Sensitive data (passwords, tokens, API keys) is never logged. Request logging includes: username (not password), user_id, truncated question text, and upload filename. Error conditions are logged at `WARNING` or `ERROR` level.

Log files are written to `logs/app.log` (gitignored) with rotation (5 MB max, 3 backups).

## Health and Status

The `/api/status` endpoint returns API health, database connectivity, and RAG readiness. It does not expose internal configuration values, error details, or secrets.

## Dependency Security

Dependencies are pinned in `requirements.txt`. To scan for known vulnerabilities:
```bash
pip install pip-audit
pip-audit
```

## Residual Risks

- JWT tokens stored in `localStorage` are vulnerable to XSS attacks. Mitigation: add a Content-Security-Policy header; consider migrating to httpOnly cookies in production.
- No rate limiting on login or signup endpoints — a production deployment should add IP-based rate limiting to prevent brute-force attacks.
- The SQLite database file is stored on the local filesystem; in production, use PostgreSQL with proper access controls.
- Image files are stored on local disk without virus scanning; in production, scan uploads with ClamAV or similar.
