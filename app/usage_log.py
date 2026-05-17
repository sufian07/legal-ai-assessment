"""Append-only JSONL writer for token usage and latency.

Every LLM call records one line into ``usage_log.jsonl``. The dashboard's
Stats view reads from this file to render cost and latency trends.

The writer is threadsafe within a single process via line-buffered append
semantics; no cross-process locking is provided — the dashboard reads but
does not write.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import settings


def record(
    stage: str,
    *,
    tokens_in: int = 0,
    tokens_out: int = 0,
    latency_ms: float = 0.0,
    model: str | None = None,
    **extra: Any,
) -> None:
    """Append a single usage record to the usage log.

    Parameters
    ----------
    stage:
        Pipeline stage name, e.g. ``"ingest"``, ``"extract"``, ``"draft"``,
        ``"classify"``.
    tokens_in:
        Input token count reported by the model provider.
    tokens_out:
        Output token count reported by the model provider.
    latency_ms:
        Wall-clock latency for the call in milliseconds.
    model:
        Model identifier; defaults to ``settings.anthropic_model``.
    extra:
        Additional fields to record (``doc_id``, ``retry_count``, etc.).
    """
    path = Path(settings.usage_log)
    if path.parent != Path("") and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(),
        "stage": stage,
        "model": model or settings.anthropic_model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency_ms,
    }
    payload.update(extra)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, default=str) + "\n")
