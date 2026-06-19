# Security Test Report

## Scope
- FastAPI authentication and authorization
- Protected chatbot and upload routes
- Input validation and SQL query safety
- File upload behavior and content type checks
- Secret handling and prompt injection risk checks

## Methods Used
- Manual auth checks with valid and invalid tokens
- Endpoint testing with malformed input
- Validation of parameterized SQL queries
- Upload tests for invalid content_type and size boundaries
- Repository secret scan review for API key exposure

## Security Findings
- Password hashing is enforced with PBKDF2 and salt.
- Protected routes reject missing or invalid bearer tokens.
- SQL statements use parameterized placeholders.
- Upload blocks unsupported content_type and excessive file size.
- Prompt injection risk is reduced by grounding to retrieved context and unknown-answer behavior.

## Issues Found And Fixes
- Issue: Unauthenticated chat/upload access possible in early scaffolding.
- Fix: Added token-based authorization dependency.

- Issue: Potential unsafe upload naming.
- Fix: Added safe file name generation and controlled uploads directory.

## Dependency And Secret Checks
- No API keys committed in repository files.
- `OPENROUTER_API_KEY` is loaded from environment.

## Residual Risks
- Token store is in-memory and not suitable for multi-instance production.
- Rate limiting and brute-force protection should be added for production hardening.
