# I developed this file with Codex assistance; see PROCESS_LOG.md.
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest

from personal_agent.broker import Broker
from personal_agent.state import PolicyError


@pytest.mark.parametrize("failed", ["email", "calendar", "both", "neither"])
async def test_independent_alert_sources_deduplicate_and_report_degradation(settings, store, failed, caplog):
    async def emails():
        if failed in ("email", "both"):
            raise PolicyError("PRIVATE PROVIDER ERROR")
        return {"untrusted_data": [{"id": "mail-1", "subject": "Synthetic urgent", "urgent": True}]}
    async def calendar():
        if failed in ("calendar", "both"):
            raise httpx.ConnectError("PRIVATE CONNECTION ERROR")
        return {"untrusted_data": [
            {"id": "meeting-1", "summary": "Synthetic meeting",
             "start": {"dateTime": (datetime.now(UTC) + timedelta(minutes=10)).isoformat()}},
            {"id": "far-away", "summary": "Later",
             "start": {"dateTime": (datetime.now(UTC) + timedelta(hours=2)).isoformat()}},
            {"id": "all-day", "start": {"date": "2026-11-17"}},
        ]}
    # Freeze the event timestamp across repeated polls.
    events = None if failed in ("calendar", "both") else await calendar()
    original_calendar = calendar
    async def stable_calendar():
        return events if events else await original_calendar()
    broker = Broker(settings, store, SimpleNamespace(emails=emails, calendar=stable_calendar))
    with caplog.at_level("INFO", logger="a3.audit"):
        first = await broker.call("a3_alerts", {})
        second = await broker.call("a3_alerts", {})
    expected = 0 if failed == "both" else 2 if failed == "neither" else 1
    assert len(first["alerts"]) == len(second["alerts"]) == expected
    assert set(first["unavailable_sources"]) == (
        {"email", "calendar"} if failed == "both" else set() if failed == "neither" else {failed}
    )
    assert "PRIVATE" not in caplog.text
    assert store.db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0] == expected


async def test_slow_source_is_cancelled_without_losing_other_alerts(settings, store, monkeypatch):
    import asyncio

    from personal_agent import broker as module

    monkeypatch.setattr(module, "ALERT_SOURCE_SECONDS", 0.02)
    cancelled = asyncio.Event()

    async def emails():
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    async def calendar():
        return {"untrusted_data": [{"id": "soon", "summary": "Synthetic meeting",
            "start": {"dateTime": (datetime.now(UTC) + timedelta(minutes=10)).isoformat()}}]}

    broker = Broker(settings, store, SimpleNamespace(emails=emails, calendar=calendar))
    async with asyncio.timeout(1):
        result = await broker.call("a3_alerts", {})
    assert cancelled.is_set()
    assert result["unavailable_sources"] == ["email"]
    assert len(result["alerts"]) == 1
