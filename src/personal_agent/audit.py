# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Structured operational events deliberately exclude prompts, tool arguments and credentials."""

import json
import logging
from datetime import UTC, datetime

LOG = logging.getLogger("a3.audit")
FIELDS = frozenset(
    {
        "request_id",
        "route",
        "reason",
        "model",
        "provider",
        "requested_model",
        "outcome",
        "latency_ms",
        "task_type",
        "status",
        "job",
        "count",
        "component",
        "version",
        "generation",
    }
)


def emit(event: str, **fields):
    if not fields.keys() <= FIELDS:
        raise ValueError("Unsafe audit field")
    record = {"event": event, "timestamp": datetime.now(UTC).isoformat(), **fields}
    LOG.info(json.dumps(record, ensure_ascii=True, separators=(",", ":")))
    return record


def configure():
    import sys

    LOG.setLevel(logging.INFO)
    LOG.propagate = False
    if not LOG.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        LOG.addHandler(handler)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
