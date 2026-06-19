# GitHub Copilot Instructions

This file defines safe and scoped Copilot usage for the DRINKOO capstone.

## Project

Build and test a Python-centric FastAPI DRINKOO application with grounded RAG behavior, authentication, image upload validation, status checks, tests, and report evidence.

## AI Scope Statement

Copilot may modify these folders and files for implementation work:
- Backend/
- Frontend/
- Database/
- Tests/
- Observability/
- Security/
- Reports/
- prompt.md
- README.md
- ADLC/ evidence files

## NEVER_MODIFY

These UAT-locked or protected files require explicit human review before updates:
- plan.md
- DRINKOO_Capstone_One_Pager.pdf
- scripts/evaluate_submission.py
- .github/workflows/pr-evaluation.yml

## Coding Constraints

Required constraints:

1. Keep the app Python-centric.
2. Use FastAPI for the backend.
3. Use simple HTML, CSS, and JavaScript for the frontend.
4. Use OpenRouter with a free model.
5. Do not commit API keys or secrets.
6. Save the final model prompt in prompt.md.
7. Save SQL table creation scripts in the Database folder.
8. Protect authenticated routes.
9. Validate image uploads.
10. Add or update tests for generated code.
11. Use parameterized SQL queries.
12. Keep logs readable and avoid sensitive data leakage.

## Prompt Review Checklist

Before asking Copilot to generate code, confirm the prompt says:

1. What to build.
2. What not to touch.
3. What tests are required.

## Review Requirement

After every Copilot coding session, run:

```bash
git diff --stat HEAD
```

Confirm that changed files match the expected scope and that no protected files were edited unintentionally.
