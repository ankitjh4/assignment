# DRINKOO GitHub Copilot Capstone

This repository now contains a working DRINKOO FastAPI application with:
- Backend API routes
- Frontend HTML/CSS/JavaScript
- SQLite schema and seed data
- Grounded retrieval-first chatbot flow with OpenRouter support
- Signup/login/logout and protected routes
- Protected image upload endpoint with validation
- Status endpoint and observability notes
- Tests and rubric-aligned report evidence

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies.
3. Set OpenRouter variables locally.
4. Run the API.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set OPENROUTER_API_KEY=your_key_here
set OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
uvicorn Backend.app:app --reload
```

Open http://127.0.0.1:8000

## Test Commands

```bash
pytest -q
pytest --cov=Backend --cov=Tests --cov-report=term-missing
python scripts/evaluate_submission.py --repo . --min-score 70
```

## Implementation Map

- Backend app: `Backend/app.py`
- Frontend files: `Frontend/index.html`, `Frontend/styles.css`, `Frontend/app.js`
- SQL schema: `Database/schema.sql`
- Seed SQL: `Database/seed.sql`
- Text2SQL evidence: `Database/text2sql_checks.md`
- Tests: `Tests/test_app.py`
- Security report: `Reports/security-test-report.md`
- Self evaluation: `Reports/self-evaluation.md`
- Observability notes: `Observability/monitoring-notes.md`

## Pull Request Submission

Create your personal branch, commit, push, and open a PR.

```bash
git checkout -b your-name
git add .
git commit -m "Complete DRINKOO capstone"
git push -u origin your-name
```
