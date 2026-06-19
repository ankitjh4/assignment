# Prompt Review Checklist

Complete this checklist before asking GitHub Copilot to generate or modify code.

## Prompt

Build a Python FastAPI DRINKOO app with signup/login/logout, protected chat and image upload routes, SQLite schema with at least six tables, a grounded retrieval-first chatbot flow with OpenRouter support, and a simple HTML/CSS/JS frontend for chat, upload, status, and auth. Keep edits in Backend, Frontend, Database, Tests, Observability, Security, Reports, README, prompt, and ADLC docs only. Do not modify evaluator scripts, plan, workflow files, or PDF assets. Add and run tests for auth, protected chat, upload validation, status endpoint, and schema checks.

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

Prompt is safe, specific, and scoped. It includes explicit boundaries, security-aware requirements, and concrete tests to reduce drift and protect UAT-sensitive files.
