# DRINKOO Observability and Monitoring Notes

## Application logging

The app emits structured JSON logs via [`Backend/logging_config.py`](../Backend/logging_config.py). Every line includes a timestamp, level, logger, message, and named fields (no secrets). Three event families are most important to operators:

- `http_request` — emitted by the request-id middleware in [`Backend/app.py`](../Backend/app.py) for every response. Fields: `request_id`, `path`, `method`, `status`, `latency_ms`.
- `chat_event` — emitted by [`Backend/routers/chat.py`](../Backend/routers/chat.py) for every chatbot turn. Fields: `user_id`, `session_id`, `model`, `used_fallback`, `retrieved` (list of citation ids), `refused`.
- `chat_refused` — emitted when prompt-injection is detected. Fields: `reason`, `user_id`, `session_id`.

Other named events: `app_startup`, `rag_index_ready`, `user_signup`, `user_login`, `text2sql_event`, `upload_event`, `openrouter_error`.

Logs are written to two sinks:

1. **stdout** — always on, so any standard collector (CloudWatch, Loki, Datadog, Azure Log Analytics) can scoop the same lines.
2. **Rotating file** — `LOG_FILE_PATH` (default `./logs/drinkoo.log`), rotated at `LOG_FILE_MAX_MB` (default 5 MB) with `LOG_FILE_BACKUP_COUNT` backups (default 5). Set `LOG_FILE_PATH=""` to disable the file sink. The `logs/` directory is gitignored.

## Health and status endpoints

- `GET /api/health` — cheap liveness probe. Always returns 200 when the process is alive.
- `GET /api/status` — readiness + dependency status. Returns JSON with components for `api`, `database`, `rag`, `llm`, `environment`, `version`. The HTML status page at `/status` renders this every 15 seconds.

## What we would monitor in production

| SLI | Definition | Target |
| --- | --- | --- |
| Chat latency p95 | p95 of `chat_event.latency_ms` (measured indirectly via the wrapping `http_request`) | < 4000 ms |
| Chat success rate | 1 - (errors / total chat requests) | >= 99% |
| LLM error rate | `openrouter_error` per minute | < 5/min sustained |
| Refusal rate | `chat_refused` / total chat requests | < 25% |
| Retrieval hit rate | proportion of chat events where `len(retrieved) > 0` | > 80% |
| Text2SQL correctness | nightly run of `scripts/run_text2sql_eval.py` | >= 90% |
| RAG faithfulness | nightly run of `scripts/run_rag_eval.py` | >= 0.85 |

## Suggested dashboards

- **Chat health**: requests per minute, latency p50/p95, refusal rate, fallback rate, top retrieved sources.
- **Catalog reliability**: errors per route, slow queries, retrieval index size.
- **Security**: signup/login failure ratios, upload rejection breakdown by reason, prompt-injection refusal counts.
- **Build info**: `version` and `environment` tagged across all panels.

## Alerts

- Page when chat latency p95 > 6 s for 5 minutes.
- Page when `openrouter_error` events spike above the 5/min sustained rate.
- Warn when refusal rate > 40% (likely retrieval degradation).
- Page when the `/api/health` endpoint stops returning 200 for 2 minutes.

## Evidence

- The structured logs from a manual test run are captured in [`screenshots/`](../Reports/screenshots/) (see `Reports/README.md` for the screenshot checklist).
- Eval trends land in [`Reports/text2sql-results.md`](../Reports/text2sql-results.md) and [`Reports/rag-faithfulness-results.md`](../Reports/rag-faithfulness-results.md), regenerated on demand by the two CLI eval scripts.
