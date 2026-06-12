# DRINKOO GitHub Copilot Capstone

This is the starter repository for the DRINKOO RAG Chatbot capstone assignment in the CloudThat GitHub Copilot training program.

## Read This First

Do not start coding until you have read [`plan.md`](plan.md) from top to bottom.

The evaluation is strict, but the priority is simple: build a working DRINKOO website with a good frontend, a correct backend, a useful database, strong Text2SQL behavior, and a grounded RAG chatbot.

You also need lightweight ADLC and UAT evidence, but this is not a DevOps-heavy project.

## How To Clone This GitHub Repo

1. Open the GitHub repository page in your browser.
2. Click the green **Code** button.
3. Copy the HTTPS GitHub URL. It will look like this:

```text
https://github.com/<owner>/<repo-name>.git
```

4. Open a terminal on your computer.
5. Run this command, replacing the URL with the one you copied:

```bash
git clone https://github.com/<owner>/<repo-name>.git
```

6. Go into the cloned folder:

```bash
cd <repo-name>
```

## Branch And Pull Request Submission

Create a branch using your own name before you start coding:

```bash
git checkout -b your-name
```

Example:

```bash
git checkout -b ankit-jha
```

When your project is complete, commit your work, push your branch, and submit a pull request to the current repository.

```bash
git add .
git commit -m "Complete DRINKOO capstone"
git push -u origin your-name
```

Then open GitHub, create a pull request from your branch, and submit that PR for evaluation.

## Automatic PR Evaluation

Every pull request runs a lightweight GitHub Actions check:

```text
.github/workflows/pr-evaluation.yml
```

The workflow runs:

```bash
python scripts/evaluate_submission.py --repo . --min-score 70
```

This check looks for the required implementation and evidence: FastAPI backend, frontend files, six-table SQL schema, Text2SQL evidence, grounded RAG evidence, completed `prompt.md`, auth/upload work, tests, ADLC files, security notes, and status/observability evidence.

The automated check is not a perfect grader. It is a first-pass quality gate. Human review will still evaluate whether the app actually works well.

## Read Every Folder Todo

Before writing code in any component, read the matching `todo.txt` file:

- [`Backend/todo.txt`](Backend/todo.txt)
- [`Frontend/todo.txt`](Frontend/todo.txt)
- [`Database/todo.txt`](Database/todo.txt)
- [`Observability/todo.txt`](Observability/todo.txt)
- [`Security/todo.txt`](Security/todo.txt)
- [`Tests/todo.txt`](Tests/todo.txt)
- [`Reports/todo.txt`](Reports/todo.txt)
- [`scripts/evaluate_submission.py`](scripts/evaluate_submission.py)

Each `todo.txt` translates the evaluation criteria into concrete work for that folder. If you skip these files, you will miss required grading evidence.

Also read and complete:

- [`prompt.md`](prompt.md)
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- [`ADLC/ai-scope-statement.md`](ADLC/ai-scope-statement.md)
- [`ADLC/prompt-review-checklist.md`](ADLC/prompt-review-checklist.md)
- [`ADLC/uat-protection.md`](ADLC/uat-protection.md)

Additional reference:

- [CloudThat Copilot Training Reference](https://app.layers.md/p/home-19b9e/pages/f0393ec4-d8b2-4fb8-b81e-7da8d8cb8307)

## What To Build

Build a Python-centric FastAPI website for DRINKOO with:

- A backend API.
- A simple HTML/CSS/JavaScript frontend.
- A SQL database with at least six tables and saved schema SQL.
- A grounded RAG chatbot.
- Signup, login, authorization, and protected routes.
- Image upload.
- Status page and observability evidence.
- Unit tests, integration tests, and eval tests.
- Security testing and a security report.
- LLM-based self-evaluation with scores and screenshots.

## Required PDFs

Read the capstone one-pager:

- [`DRINKOO_Capstone_One_Pager.pdf`](DRINKOO_Capstone_One_Pager.pdf)

The GitHub Copilot MCQ assessment will be shared separately by the faculty.

## OpenRouter Requirement

Use your own OpenRouter API key with a free model.

Do not commit your API key. Store it locally as an environment variable:

```bash
export OPENROUTER_API_KEY="your_key_here"
```

Use [`.env.example`](.env.example) as a reference for the expected variable names.

You must save the final model prompt in [`prompt.md`](prompt.md). Your prompt will be evaluated for whether it helps the model answer from DRINKOO data, avoid hallucination, handle unknown questions, and produce useful responses.

Learners should build the application themselves using GitHub Copilot as part of the assignment and keep their repository changes intentional and well documented.
