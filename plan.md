# DRINKOO RAG Chatbot Capstone Plan

## Training Context

This capstone is part of the CloudThat GitHub Copilot training program. Learners will use Visual Studio Code and GitHub Copilot to design, build, test, secure, and document a complete Python-centric RAG chatbot website for DRINKOO, a fictional beverage company.

The goal is not only to build a working application, but also to show evidence of an AI-assisted software delivery lifecycle: planning, implementation, testing, security review, observability, documentation, and self-evaluation.

## Learner Workflow

1. Copy or clone this starter repository.
2. Create a branch using your own name, for example `ankit-jha`.
3. Create or update your own implementation plan in `plan.md`.
4. Store the final OpenRouter model prompt in `prompt.md`.
5. Build the DRINKOO RAG chatbot application.
6. Keep your repository changes intentional and organized.
7. Save all required evidence, including SQL scripts, screenshots, reports, test output, and self-evaluation results.
8. Submit a pull request back to the current repository from your named branch.

## Required Stack

- Backend: Python with FastAPI.
- Frontend: HTML, CSS, and minimal JavaScript served by FastAPI.
- Database: SQL database of your choice, such as SQLite or PostgreSQL.
- RAG layer: retrieval over a dummy DRINKOO dataset.
- LLM usage: GitHub Copilot for AI-assisted development and OpenRouter with a free model for the chatbot or self-evaluation LLM layer.
- Testing: Python unit and integration tests.
- Security: documented security testing and remediation.
- Observability: health/status endpoint plus basic logging and monitoring notes.

Keep the project Python-centric. Avoid introducing a large frontend framework unless your instructor explicitly approves it.

Use your own OpenRouter API key. Store it in a local environment variable such as `OPENROUTER_API_KEY`; do not commit the key. Use a free OpenRouter model and document the exact model name in `prompt.md`.

## Product Scenario

DRINKOO is a fictional drinking company that wants a customer-facing website with a RAG chatbot. The chatbot should answer questions using company-owned dummy data, such as product details, ingredients, nutrition, inventory, orders, support policies, and promotions.

The website should demonstrate that a user can:

- Sign up and log in.
- Access protected chatbot features after authentication.
- Ask questions about DRINKOO data.
- Receive grounded answers based on the dummy dataset.
- Upload an image where relevant to the experience.
- View a status page showing basic system health.

## Minimum Application Requirements

Your implementation must include:

- A FastAPI backend with clear API routes.
- A simple frontend served from the Python app.
- Signup and login flow.
- Authorization for protected routes.
- RAG chatbot endpoint.
- Image upload endpoint with validation.
- Database schema with at least six tables.
- Saved SQL script for table creation.
- Seed data or a repeatable data-loading process.
- Status page or health page.
- Unit tests and at least one integration test.
- Security test report.
- Observability notes, logs, or dashboard evidence.
- Documentation for running, testing, and evaluating the app.

## Database Requirement

Create a dummy DRINKOO dataset with at least six tables. You may choose your own schema, but it must be coherent and useful for chatbot retrieval.

Suggested tables:

- `users`
- `products`
- `ingredients`
- `product_ingredients`
- `orders`
- `support_articles`
- `promotions`
- `chat_sessions`

You must save the table creation SQL in the repository, for example:

```text
database/schema.sql
```

The schema will be evaluated for:

- Correct SQL syntax.
- Appropriate primary keys and foreign keys.
- Useful column names and data types.
- Normalization where appropriate.
- Relevance to the DRINKOO chatbot use case.
- Ability to support grounded RAG answers.

## RAG Chatbot Requirements

The chatbot must answer questions using the DRINKOO dummy dataset. It should not rely only on generic model knowledge.

At minimum, include:

- A retrieval step that searches the dataset or prepared knowledge documents.
- A response generation step that uses retrieved context.
- A visible answer in the frontend chat UI.
- A way to inspect or log retrieved context for debugging.
- Handling for questions that cannot be answered from the dataset.

Example questions the chatbot should support:

- Which DRINKOO products are low sugar?
- What ingredients are used in the citrus drinks?
- Are there active promotions for sparkling beverages?
- What should a customer do if an order arrives damaged?
- Which products are available for bulk orders?

## Image Upload Requirements

Add image upload support using a protected route. The implementation should:

- Accept only expected image file types.
- Enforce a reasonable file size limit.
- Store uploads safely or process them without unsafe paths.
- Avoid exposing uploaded files without authorization.
- Include at least one test or documented manual test for upload behavior.

## Authentication And Authorization Requirements

The app must include:

- Signup route.
- Login route.
- Password hashing.
- Session or token-based authentication.
- Protected chatbot route.
- Protected image upload route.
- Clear logout behavior.

Do not store plain-text passwords. Do not hard-code secrets in the repository.

## Status Page And Observability

Create a basic status page or endpoint that shows:

- API health.
- Database connectivity.
- RAG dependency readiness.
- Current app version or environment label.

Also include basic observability evidence:

- Structured or readable application logs.
- Error logging for failed requests.
- Notes describing what would be monitored in production.
- Screenshots or copied output showing health checks working.

## Testing Requirements

Include tests for:

- Database setup or schema loading.
- Authentication flow.
- Protected route behavior.
- Chatbot endpoint behavior.
- Image upload validation.
- Status or health endpoint.

Recommended tools:

- `pytest`
- FastAPI `TestClient`
- Coverage reporting with `pytest-cov`

## Security Test Report

Create a security test report, for example:

```text
reports/security-test-report.md
```

The report should include:

- Scope of testing.
- Tools or methods used.
- Authentication and authorization checks.
- Input validation checks.
- File upload checks.
- Dependency vulnerability checks.
- Secret scanning checks.
- Prompt injection or RAG misuse checks.
- Issues found.
- Fixes applied.
- Residual risks.

At minimum, test for common web application risks such as broken access control, weak password handling, injection, unsafe file uploads, exposed secrets, and insecure error messages.

## AI-Assisted SDLC Evidence

Show how GitHub Copilot helped you across the software delivery lifecycle. Include short notes or screenshots for:

- Planning.
- Backend implementation.
- Frontend implementation.
- Database design.
- Test generation.
- Security review.
- Debugging.
- Documentation.

Keep evidence concise and relevant.

## Self-Evaluation Workflow

After completing the project, run a self-evaluation using an LLM API. Save the results and screenshots in your submission.

Suggested location:

```text
reports/self-evaluation.md
reports/screenshots/
```

Use the rubric below and ask the LLM to evaluate your repository honestly. Include links or pasted excerpts from your code, tests, SQL, reports, and screenshots.

### Suggested Self-Evaluation Prompt

```text
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

Save the LLM output and include screenshots showing the self-evaluation process.

## Evaluation Rubric

| Category | Points | Expectations And Required Evidence |
| --- | ---: | --- |
| Working Python/FastAPI backend and code quality | 15 | FastAPI app runs locally, routes are organized, code is readable, errors are handled, configuration is not hard-coded, and the backend connects cleanly to the database and frontend. |
| Frontend usability and presentation | 15 | HTML/CSS/JavaScript frontend is usable and presentable, with clear signup, login, chatbot, image upload, status, loading, error, and result states. Learners will be judged on frontend skills. |
| Database schema, saved SQL, and Text2SQL correctness | 20 | At least six coherent SQL tables, saved table creation SQL, useful relationships, seed data, and Text2SQL correctness checks. Target: Text2SQL correctness >= 90% for the supplied sample questions. |
| RAG chatbot quality, grounding, and OpenRouter prompt quality | 20 | Chatbot uses the DRINKOO dataset, retrieves relevant context, gives grounded answers, handles unknowns, and uses OpenRouter with a free model. The final model prompt must be saved in `prompt.md` and will be judged for clarity, grounding instructions, refusal behavior, and answer quality. Target: RAG faithfulness >= 0.85 where measured. |
| Authentication, authorization, and image upload | 10 | Signup, login, password hashing, protected routes, logout/session handling, validated image upload, file size checks, and safe upload handling. |
| Tests and working application evidence | 10 | Meaningful unit and integration tests for schema loading, auth, protected routes, chatbot, image upload, and status page. The app must run, and evidence must show tests passing. |
| ADLC, UAT protection, and Copilot workflow evidence | 5 | Keep this lightweight but complete. Gate: Before any Copilot session, developer writes an AI Scope Statement (what files are in scope; what is UAT-locked). Gate: copilot-instructions.md must include NEVER_MODIFY list of UAT-locked modules before any code generation session. Gate: Prompt Review Checklist — does the prompt specify: (1) what to build, (2) what NOT to touch, (3) test requirements? Gate: After every Copilot coding session, run: git diff --stat HEAD. |
| Security, status page, and basic observability | 5 | Security test report, secret handling, input validation, upload safety, prompt injection checks, status page, readable logs, and basic observability notes. CI/CD is not the main focus; simple local checks or lightweight GitHub Actions are enough if included. |

Total: 100 points.

## Component Todo Files

Each component folder contains a `todo.txt` file. Read every `todo.txt` before writing code. These files translate the evaluation gates into concrete tasks for the backend, frontend, database, observability, security, tests, and reports.

## Automatic PR Evaluation

Every pull request runs `.github/workflows/pr-evaluation.yml`, which executes `scripts/evaluate_submission.py`. The automated check gives a first-pass score for the required files, implementation evidence, SQL schema, Text2SQL evidence, RAG evidence, prompt quality, tests, ADLC files, and security/status evidence.

This is not the final human grade. It is a quality gate to catch incomplete submissions before review.

## Submission Checklist

- [ ] FastAPI app runs locally.
- [ ] Frontend pages are usable.
- [ ] Signup and login work.
- [ ] Protected chatbot route works.
- [ ] Image upload works and is validated.
- [ ] At least six database tables are created.
- [ ] SQL creation script is saved.
- [ ] Seed data is included or documented.
- [ ] Tests pass.
- [ ] Status page or health endpoint works.
- [ ] Security test report is complete.
- [ ] Observability evidence is included.
- [ ] OpenRouter free model name and final prompt are saved in `prompt.md`.
- [ ] Self-evaluation score and screenshots are saved.
- [ ] README explains setup, run, test, and evaluation steps.
- [ ] Pull request is submitted from a branch named after the learner.

## Future PDF Deliverables

After this capstone brief is finalized, create:

1. A detailed capstone PDF describing the project, requirements, rubric, and self-evaluation process.
2. A separate 50-question multiple-choice assessment about GitHub Copilot, shared directly by the faculty.

The 50-MCQ assessment is a separate follow-up item and is not part of this initial repository scaffold.
