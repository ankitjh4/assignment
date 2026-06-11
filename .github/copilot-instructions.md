# GitHub Copilot Instructions

TODO: Complete this file before using GitHub Copilot for code generation.

## Project

TODO: Describe the DRINKOO RAG chatbot implementation you are building.

## AI Scope Statement

TODO: List the files and folders Copilot is allowed to help modify for your current task.

## NEVER_MODIFY

TODO: List UAT-locked or protected files that Copilot must not modify.

Examples:

```text
plan.md
README.md after final submission instructions are approved
Database/schema.sql after UAT approval
Tests/ after tests are approved and passing
```

## Coding Constraints

TODO: Add constraints for your implementation.

Required constraints:

1. Keep the app Python-centric.
2. Use FastAPI for the backend.
3. Use simple HTML, CSS, and JavaScript for the frontend.
4. Use OpenRouter with a free model.
5. Do not commit API keys or secrets.
6. Save the final model prompt in `prompt.md`.
7. Save SQL table creation scripts in the Database folder.
8. Protect authenticated routes.
9. Validate image uploads.
10. Add or update tests for generated code.

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

TODO: Review whether any unexpected files changed.
