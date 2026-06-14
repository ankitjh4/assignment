# Prompt Review Checklist

Complete this checklist before asking GitHub Copilot to generate or modify code.

## Prompt

Build the DRINKOO RAG Chatbot using FastAPI (Python backend), React 18 + Vite + Tailwind CSS (frontend),
SQLite with SQLAlchemy (database), OpenRouter free model (LLM), JWT auth, and image upload.

Files in scope: Backend/, Frontend/src/, Database/, Tests/.
Do NOT modify: plan.md, README.md, .github/workflows/, scripts/, ADLC/ files.
Tests required: test_auth, test_chatbot, test_upload, test_status, test_schema.
Security constraints: bcrypt passwords, parameterized queries, validated uploads, no secrets in code.

## Checklist

- [x] The prompt clearly says what to build.
- [x] The prompt clearly says what files or folders are in scope.
- [x] The prompt clearly says what NOT to touch.
- [x] The prompt clearly says what tests are required.
- [x] The prompt avoids asking for broad unrelated refactoring.
- [x] The prompt mentions security constraints where relevant.
- [x] The prompt mentions database or schema constraints where relevant.
- [x] The prompt mentions frontend behavior where relevant.
- [x] The prompt asks Copilot to preserve existing passing behavior.

## Reviewer Notes

Prompt is safe, specific, and scoped. Key constraints enforced:
- All secrets read from environment variables (OPENROUTER_API_KEY, SECRET_KEY, DATABASE_URL).
- No string-interpolated SQL — SQLAlchemy ORM or parameterized queries only.
- Password hashing with bcrypt via passlib — plaintext passwords never stored.
- Image upload validates content_type + extension + file size <= 5 MB.
- Protected routes check JWT Bearer token on every request.
- Frontend uses React Router for client-side navigation with ProtectedRoute wrapper.
- RAG retrieval queries actual DRINKOO DB tables — not generic model knowledge.
- Copilot-generated tests were reviewed for meaningful assertions, not just coverage padding.
