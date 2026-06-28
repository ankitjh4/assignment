# Plan: DRINKOO End-to-End Implementation

## TL;DR

Deliver a complete DRINKOO SKU management and RAG chatbot system using Python FastAPI, SQLite, and a lightweight HTML/JS frontend. The implementation must satisfy all TODO items from Backend, Database, Frontend, Observability, Reports, and Tests folders, while adhering to the guardrails in `instructions.md`.

## Steps

### 1. Project Initialization

1.1. verify existing folder structure.  
1.2. Create a virtual environment and install dependencies listed in Backend/todo.txt (fastapi, uvicorn, pydantic, python‑multipart, pytest).  
1.3. Add a root `requirements.txt` for reproducibility.  
1.4. Set up `git` housekeeping: ensure `git diff --stat HEAD` will be run after each Copilot session.

### 2. Database Design (Database/todo.txt)

2.1. Define at least six tables: `users`, `products`, `ingredients`, `product_ingredients`, `orders`, `support_articles` (plus optional `promotions`, `chat_sessions`).  
2.2. Create `Database/schema.sql` with:

- Primary keys, foreign keys, appropriate data types.
- Comments explaining relationships.
- Constraints (e.g., `unit_volume_ml` CHECK IN (1,1.5)).  
  2.3. Add seed data or a repeatable data‑loading script (`Scripts/load_data.py`).  
  2.4. Draft sample natural‑language questions and their expected SQL outputs for Text2SQL validation (≥90% correctness).  
  2.5. Document DB creation, reset, and seeding steps in `Database/README.md`.

### 3. Backend Implementation (Backend/todo.txt)

3.1. **App Structure** – Create `Backend/app/main.py` to mount routers.  
3.2. **Authentication** – Implement signup, login, logout, password hashing (e.g., `passlib`), and protect all routes except `/login`.  
3.3. **Chatbot Endpoint** – Build a protected `/chatbot` route that:

- Retrieves relevant DRINKOO data via SQL queries.
- Sends retrieved context to an OpenRouter free model.
- Returns a grounded answer.  
  3.4. **Image Upload** – Add a protected `/upload` endpoint with:
- File‑type whitelist (e.g., image/\*).
- Size limit (e.g., ≤5 MB).
- Safe storage path handling.  
  3.5. **Configuration** – Load secrets (e.g., `OPENROUTER_API_KEY`) from environment variables; no hard‑coded credentials.  
  3.6. **OpenRouter Integration** – Use the free model endpoint; save the final prompt in `prompt.md`.  
  3.7. **Error Handling & Logging** – Structured exception handling, readable logs for requests, chatbot retrievals, and uploads (no secret leakage).  
  3.8. **Health/Status Exposure** – Implement `/health` endpoint reporting API health, DB connectivity, RAG readiness; this satisfies Observability requirements.  
  3.9. **Database Connection** – Connect to the SQLite schema created in `Database/`, using a context manager and connection pooling.

### 4. Frontend Implementation (Frontend/todo.txt)

4.1. **Pages/Templates** – Create `Frontend/index.html` (or multiple HTML files) for:

- Signup
- Login
- Logout
- Chatbot interaction
- Image upload
- Status dashboard  
  4.2. **Chatbot UI** – Display user question, grounded answer, and error states (e.g., “No relevant data found”).  
  4.3. **Protected Access** – Hide chatbot and upload pages behind authentication (store token in `localStorage`).  
  4.4. **Image Upload Form** – Include validation messages for file type and size.  
  4.5. **Status Page** – Show API health, DB connectivity, RAG readiness, and app version.  
  4.6. **Styling & Usability** – Keep UI simple, semantic HTML, ARIA labels, high‑contrast CSS; avoid heavy frameworks.  
  4.7. **Screenshot Documentation** – Capture screenshots of each page and store them in `Reports/` as required.

### 5. Observability (Observability/todo.txt)

5.1. **Status Page** – Extend `/status` endpoint to expose API health, DB connectivity, RAG readiness, environment label.  
5.2. **Logging** – Add structured logs for successful/failed requests, chatbot retrievals, and image uploads.  
5.3. **Retention** – Ensure logs do not contain secrets.  
5.4. **Production Monitoring Plan** – Document what will be monitored (latency, error rates, DB connections).  
5.5. **Rollback Steps** – Write concise rollback instructions for undoing a bad Copilot change.  
5.6. **Evidence Capture** – Save screenshots/logs in `Reports/` demonstrating health checks.

### 6. Testing (Tests/todo.txt)

6.1. **Unit Tests** – Write tests for backend routes, service functions, and model validations.  
6.2. **Integration Tests** – Cover signup, login, protected route access, chatbot, image upload, and health/status endpoints using FastAPI `TestClient`.  
6.3. **Database Tests** – Verify schema loading, foreign‑key integrity, and seed data correctness.  
6.4. **RAG Evaluation** – Implement tests for groundedness and RAGAS faithfulness (≥0.85 target).  
6.5. **Text2SQL Checks** – Validate natural‑language questions against expected SQL (≥90% correctness).  
6.6. **Coverage Reporting** – Use `pytest-cov`; ensure coverage does not decrease after adding Copilot‑generated tests.  
6.7. **Documentation** – Add a `Tests/README.md` explaining how to run all tests locally.

### 7. Documentation & Reporting (Reports/todo.txt)

7.1. **Security Test Report** – Create `Reports/security-test-report.md` covering auth, input validation, upload safety, secret handling.  
7.2. **Self‑Evaluation** – Produce `Reports/self-evaluation.md` using the provided rubric; include score, reasoning, evidence, and improvement recommendation.  
7.3. **AI Scope Statement & Prompt Review Checklist** – Store evidence of these artifacts.  
7.4. **Git Diff Evidence** – After each Copilot session, capture `git diff --stat HEAD` output and store it.  
7.5. **Coverage & Eval Results** – Save coverage reports and RAGAS/Text2SQL results.  
7.6. **Copilot SDLC Evidence** – Document planning, coding, testing, security, debugging, and documentation moments.  
7.7. **Capstone Scorecard** – Present the final evaluation scorecard publicly.

### 8. Review Gates & Compliance

8.1. **Prompt Review Checklist** – Ensure the prompt specifies: (1) what to build, (2) what NOT to touch, (3) test requirements.  
8.2. **UAT‑Locked Files** – Maintain a `NEVER_MODIFY` list in `copilot-instructions.md`; do not modify these files without permission.  
8.3. **Security Gate** – Any high/critical security finding blocks PR merging until remediated.  
8.4. **Post‑Session Diff** – Run `git diff --stat HEAD` after every Copilot coding session and review changes.

### 9. Risks & Mitigations

- **Data Realism** – Use statistical proportions for customer generation; spot‑check a sample.
- **SKU Volume Constraint** – Enforce SQLite CHECK; add unit tests to verify compliance.
- **Concurrency** – SQLite suitable for low‑to‑moderate load; plan migration to PostgreSQL if needed.
- **Frontend Simplicity** – Keep UI minimal to meet “non‑technical executable” requirement.

### 10. Next Action

Begin with Step 1 (Project Initialization). Confirm the virtual environment setup and install the dependencies listed in `Backend/todo.txt`. Once the environment is ready, proceed to database schema design (Step 2).
