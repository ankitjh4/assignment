# Observability Notes

## Status And Health
- Endpoint: `/api/status`
- Shows API health, database connectivity, RAG readiness, app version, and environment.

## Logging
- Backend logs include signup/login outcomes, retrieval status, chatbot request handling, upload results, and errors.
- Sensitive values like API keys and password values are never logged.

## Production Monitoring Plan
- API success/error rates by route.
- Database connectivity failures and latency spikes.
- Chat retrieval miss rate and unknown-answer rate.
- Upload validation rejection rate and file-size violation attempts.

## Rollback Steps
1. Identify failing change from recent commit history.
2. Revert only the problematic commit.
3. Re-run tests and status checks.
4. Confirm auth, chat, upload, and status routes are healthy.
5. Re-deploy and monitor logs for recovery.
