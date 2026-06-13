# DRINKOO Observability Notes

## Status Endpoint

The `/api/status` endpoint returns a JSON health check covering:

| Field | Description |
|---|---|
| `api_healthy` | Always `true` if the API is responding |
| `database_connected` | Result of `SELECT 1` probe against SQLite |
| `rag_ready` | `true` if `OPENROUTER_API_KEY` environment variable is set |
| `version` | App version from `APP_VERSION` env var (default `1.0.0`) |
| `environment` | Deployment environment label (`development`, `production`) |
| `timestamp` | UTC ISO timestamp of the health check |

This endpoint is public (no auth required) so monitoring tools can poll it without credentials.

## Application Logging

Logging is configured in `Backend/main.py` via `setup_logging()`:

```python
fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
```

Log output goes to:
1. **stdout** — visible in the terminal during development and in container logs in production
2. **`logs/app.log`** — rotating file (5 MB per file, 3 backups kept), gitignored

### What is logged (INFO level)
- Application startup
- User signups and logins (username only, never password)
- Chat requests (user_id, truncated question, whether context was retrieved)
- Image uploads (user_id, safe filename, file size, content type)
- Status endpoint hits (db and rag readiness)
- Database initialisation from schema.sql

### What is logged (WARNING level)
- Failed login attempts (username only)
- Database health check failures

### What is logged (ERROR level)
- OpenRouter API errors (timeout, non-200 response)
- Any unhandled exceptions in route handlers

### What is NEVER logged
- Passwords or password hashes
- JWT tokens or bearer tokens
- API keys
- Full user question text (truncated to 60 chars)

## Production Monitoring Recommendations

In a production deployment, the following monitoring would be set up:

1. **Uptime monitoring:** Poll `/api/status` every 60 seconds. Alert if `api_healthy` is false or response time exceeds 2 seconds.

2. **Database connectivity:** Alert if `database_connected` is false for 2 consecutive health checks.

3. **RAG readiness:** Alert if `rag_ready` is false (means `OPENROUTER_API_KEY` is unset or empty).

4. **Error rate:** Monitor the application logs for `ERROR` lines. Alert if more than 5 errors occur in a 1-minute window.

5. **Latency:** Track response times for the `/api/chat` endpoint. Alert if P95 latency exceeds 10 seconds (OpenRouter calls can be slow on free tier).

6. **Structured logging:** In production, switch to JSON-format logs (e.g. using `python-json-logger`) so they can be ingested by ELK Stack, Datadog, or CloudWatch.

## Rollback Steps

If a bad deployment is detected:

1. Stop the running server (`Ctrl+C` or `kill <uvicorn_pid>`)
2. Restore the previous version: `git checkout <previous_commit>`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Restart: `uvicorn Backend.main:app --reload`
5. Verify health: `curl http://localhost:8000/api/status`

For database schema changes, restore from the previous `schema.sql` and re-run:
```bash
python Database/seed.py
```

## Evidence of Health Checks Working

Run the server and verify:

```bash
# Start server
uvicorn Backend.main:app --reload

# Check status endpoint
curl http://localhost:8000/api/status

# Expected response:
{
  "api_healthy": true,
  "database_connected": true,
  "rag_ready": true,
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-06-13T..."
}
```

The status page at `http://localhost:8000/status.html` shows green indicators for all three health checks when the application is running correctly.
