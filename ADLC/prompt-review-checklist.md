# Prompt Review Checklist

Complete this checklist before asking GitHub Copilot to generate or modify code.

## Prompt

The following prompt was used to guide the initial DRINKOO RAG chatbot build:

```
Build a Python FastAPI backend for the DRINKOO RAG chatbot website. The backend must:
1. Use SQLite via the sqlite3 stdlib (no SQLAlchemy)
2. Implement signup, login, logout with bcrypt password hashing and JWT tokens
3. Implement a RAG chatbot endpoint that retrieves context from the products,
   support_articles, and promotions tables, then calls OpenRouter with a grounding prompt
4. Implement an image upload endpoint that validates content_type and file size
5. Implement a /api/status health check endpoint
6. Use environment variables for all secrets (OPENROUTER_API_KEY, SECRET_KEY)
7. NOT modify: plan.md, README.md, scripts/evaluate_submission.py, .github/workflows/

All new routes must have corresponding pytest tests in the Tests/ folder.
Do not add features beyond what is listed above.
```

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

The prompt was specific, scoped, and included explicit NOT-to-touch constraints. The security constraint (no hardcoded secrets, env vars only) was included upfront. The database constraint (sqlite3 stdlib only) prevented unnecessary dependency introduction. The test requirement ensured every new route had corresponding test coverage. The prompt was reviewed against the Prompt Review Checklist before each coding session.
