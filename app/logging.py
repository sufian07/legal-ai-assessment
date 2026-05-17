"""Structured logging shared across the pipeline.

Every module gets a named logger via ``get_logger(__name__)``. Logs are
emitted to stderr as single-line JSON by default; set ``LOG_FORMAT=text``
in the environment for human-readable output during development.

Usage::

    from app.logging import get_logger
    logger = get_logger(__name__)
    logger.info("ingest started", extra={"doc_id": "01_case_brief"})
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.config import settings

_STANDARD_LOGRECORD_FIELDS = {
    "args",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON for structured ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOGRECORD_FIELDS:
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


_configured = False


def _configure_root() -> None:
    """Wire up the root logger once per process."""
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stderr)
    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given name."""
    _configure_root()
    return logging.getLogger(name)
