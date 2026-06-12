# Prompt Review Checklist

This is the completed Prompt Review Checklist for the DRINKOO RAG Chatbot capstone scaffold session.

## Prompt

Below is the high-level prompt used to drive the capstone build. The session followed a longer plan stored at `drinkoo_Impl_plan.md`, but this is the gating prompt that was reviewed before code generation started.

```text
Build a Python-centric DRINKOO website inside assignment/ with:

- FastAPI backend with auth (signup/login/logout, bcrypt, JWT cookie), protected /api/chat and /api/upload, status/health endpoints, structured JSON logs, and a Text2SQL endpoint with sqlglot validation.
- Jinja2 + vanilla CSS/JS frontend covering home, login, signup, chat, upload, status, products, promotions pages. Beverage-themed brand. No frontend framework.
- SQLite database with at least six tables. Use the suggested DRINKOO schema (users, products, ingredients, product_ingredients, orders, order_items, promotions, support_articles, chat_sessions). Save schema.sql and seed.sql. Add a 14-question Text2SQL sample bank.
- Grounded RAG pipeline that retrieves from products + promotions + support_articles + Markdown FAQ/policies, generates answers using OpenRouter model "nvidia/nemotron-3-ultra-550b-a55b:free" with a deterministic offline fallback when the API key is absent, and refuses prompt injection.
- Tests under Tests/: schema, auth, chat (grounded + injection refusal + unknown), upload (auth, MIME, magic-bytes, size, path safety), status, Text2SQL >= 90%, RAG faithfulness >= 0.85, prompt-injection direct unit tests.
- Reports/, Security/, Observability/, ADLC/, .github/copilot-instructions.md filled with concrete evidence; no placeholder text remains.
- Do not modify scripts/evaluate_submission.py, .github/workflows/pr-evaluation.yml, plan.md, README.md (original instructions), DRINKOO_Capstone_One_Pager.pdf.
- The PR evaluator must score >= 90/100 and the local test suite must be green.
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

The prompt is safe, specific, and scoped to the assignment directory. It hard-codes the OpenRouter free model name, explicitly forbids editing the PR evaluator and the original plan/README, sets numeric thresholds for Text2SQL (>= 90%) and RAG faithfulness (>= 0.85), and demands that the resulting evidence files contain no placeholders so the evaluator's filled-file check passes. Human review of the generated diff is required before submission, per `.github/copilot-instructions.md`.
