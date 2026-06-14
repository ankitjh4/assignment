# DRINKOO Observability Notes

## Status / Health Endpoint

`GET /api/status` returns:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "api": "ok",
    "database": "ok",
    "rag": "ready",
    "openrouter_model": "liquid/lfm-2.5-1.2b-instruct:free"
  }
}
```

- `status` is `"healthy"` if all checks pass, `"degraded"` otherwise.
- `database` check executes `SELECT 1` and catches any exception.
- `rag` check verifies `OPENROUTER_API_KEY` is set.
- Auto-refreshes every 30 seconds on the frontend Status page.

## Application Logging

Logging is configured in `Backend/main.py` using Python's `logging.config.dictConfig`.

Format:
```
2026-06-14 10:30:00 [INFO] Backend.auth: User logged in: alice@example.com
2026-06-14 10:30:01 [INFO] Backend.rag: Retrieved context length: 1420 chars
2026-06-14 10:30:02 [WARNING] Backend.chatbot: Prompt injection attempt by user alice@example.com
2026-06-14 10:30:05 [ERROR] Backend.rag: OpenRouter HTTP error: 429 — rate limited
```

### What is logged

| Event | Level | Details |
|---|---|---|
| Startup | INFO | "DRINKOO API started — DB initialised." |
| User signup | INFO | email address |
| User login | INFO | email address |
| Login failure | WARNING | email address (no password) |
| Chat request | INFO | email + first 80 chars of question |
| Retrieved context | INFO | character count only (no PII) |
| Prompt injection | WARNING | email + first 80 chars of input |
| Upload | INFO | email + original filename + size + stored name |
| DB health failure | ERROR | exception message |
| OpenRouter failure | ERROR | HTTP status or exception message |
| Unhandled exception | ERROR | method + path + exception |

## What Would Be Monitored in Production

| Metric | Tool | Alert Threshold |
|---|---|---|
| API error rate (5xx) | Datadog / CloudWatch | > 1% of requests |
| DB connection pool saturation | Datadog | > 80% utilised |
| Average chat latency (p95) | Datadog | > 3 seconds |
| OpenRouter API error rate | Custom log parser | > 5% of calls |
| Upload failure rate | Custom log parser | > 2% of uploads |
| JWT auth failure rate | Fail2Ban / SIEM | Spike > 10/min per IP |
| Disk usage (uploads directory) | Prometheus node_exporter | > 80% |

## Rollback Steps for a Bad Copilot-Assisted Change

1. Identify the bad commit:
   ```bash
   git log --oneline -10
   git diff HEAD~1 HEAD --stat
   ```

2. Revert to the last known-good commit:
   ```bash
   git revert HEAD          # safe: creates a new revert commit
   # OR if the commit was never pushed:
   git reset --hard HEAD~1  # destructive: only on local branches
   ```

3. Re-seed the database if schema changed:
   ```bash
   python Database/seed.py --reset
   ```

4. Re-run tests:
   ```bash
   pytest Tests/ -v
   ```

5. Check the status endpoint confirms healthy state:
   ```bash
   curl http://localhost:8000/api/status
   ```

## RAG Eval Score Tracking

| Date | Faithfulness | Text2SQL % | Notes |
|---|---|---|---|
| 2026-06-14 | Manual review (grounded answers confirmed) | 100% (10/10) | `Database/test_text2sql.py` automated checker |

Target: RAG faithfulness >= 0.85, Text2SQL >= 90%.
