# DRINKOO Security Notes

## Authentication

- Passwords are hashed with **bcrypt** (passlib, rounds=12) — plaintext passwords are never stored.
- JWT tokens use **HS256** with a secret key loaded from `SECRET_KEY` environment variable.
- Token lifetime is 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Protected routes use FastAPI's `Depends(get_current_user)` — any missing or invalid token returns HTTP 401.
- Login failure returns a generic "Incorrect email or password" message — no user enumeration.

## Input Validation

- All request bodies are validated with **Pydantic** schemas — type coercion and constraint checking.
- Email fields use `EmailStr` from pydantic-email-validator.
- Password length minimum is enforced at the API layer (>= 8 characters).
- SQL queries use **SQLAlchemy ORM** or parameterized `text()` queries — no string-interpolated SQL.
- SQL injection is prevented by never concatenating user input into SQL strings.

## Image Upload Security

- Allowed content types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`.
- Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`.
- Maximum file size: **5 MB** (enforced by reading full bytes and checking `len(data)`).
- Stored filenames are **UUID-based** — the original filename is never used as the storage path.
- This prevents path traversal attacks (`../../etc/passwd`) and overwrite attacks.
- Uploads are stored in `Backend/uploads/` which is NOT served without auth.

## Prompt Injection Prevention

- Chatbot detects adversarial patterns: "ignore previous", "ignore all", "disregard", "new instructions", "system prompt".
- Matching inputs are rejected with a safe fallback message — no LLM call is made.
- The system prompt instructs the LLM to answer only from retrieved DRINKOO context.
- LLM temperature is set to 0.2 to reduce hallucination and off-topic responses.
- Retrieved context is sanitized (max 4000 chars stored) to prevent context stuffing.

## Secret Handling

- `OPENROUTER_API_KEY` is read from environment variables only — never committed to the repository.
- `SECRET_KEY` (JWT signing key) is read from environment variables only.
- `.env.example` documents variable names without values.
- `.gitignore` excludes `.env` and the SQLite database file.

## Error Handling

- Global exception handler returns generic "Internal server error" to the client — no stack traces exposed.
- Failed login attempts are logged (email only, no password) for audit purposes.
- Upload errors are logged with filename and user email — no sensitive data in logs.

## Dependency Security

- Dependencies pinned to exact versions in `requirements.txt`.
- `passlib[bcrypt]` for secure password hashing.
- `python-jose[cryptography]` for JWT — uses the `cryptography` backend.
- No use of `pickle`, `eval`, or `exec` anywhere in the codebase.

## Security Test Summary

See `Reports/security-test-report.md` for full test results and remediation notes.
