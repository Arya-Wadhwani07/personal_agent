# I developed this file with Codex assistance; see PROCESS_LOG.md.
import json

import pytest

from personal_agent.audit import emit


def test_audit_rejects_raw_content_and_escapes_log_injection(caplog):
    with pytest.raises(ValueError):
        emit("routing", prompt="synthetic private text")
    with caplog.at_level("INFO", logger="a3.audit"):
        emit("routing", route="local", reason="fixture\nforged", model="synthetic", outcome="success")
    record = json.loads(caplog.records[-1].message)
    assert record["reason"] == "fixture\nforged"
    assert "\n" not in caplog.records[-1].message
    assert "timestamp" in record
