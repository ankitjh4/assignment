"""Structured logging configuration for DRINKOO.

Emits compact JSON log lines for app, request, chat, and security events. Keeps
secrets and API keys out of the log surface by design — only metadata is logged.

Sinks:
- stdout (always on) so collectors like Datadog / CloudWatch / Loki can scoop it up.
- Rotating file at `LOG_FILE_PATH` (default `./logs/drinkoo.log`) so logs persist on
  disk. Set `LOG_FILE_PATH=""` to disable file logging.
"""
from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Render log records as a single-line JSON document."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    from .config import get_settings

    settings = get_settings()
    formatter = JsonFormatter()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    log_path = (settings.log_file_path or "").strip()
    if log_path:
        path = Path(log_path)
        if not path.is_absolute():
            path = settings.project_root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=settings.log_file_max_mb * 1024 * 1024,
            backupCount=settings.log_file_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        logging.getLogger(__name__).info(
            "logging_file_sink_ready",
            extra={
                "path": str(path),
                "max_mb": settings.log_file_max_mb,
                "backups": settings.log_file_backup_count,
            },
        )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
