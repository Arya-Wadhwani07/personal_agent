# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Date rollover, freshness, service failure and recovery without real network access."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest

from personal_agent import integrations
from personal_agent.integrations import Services
from personal_agent.state import PolicyError


def snapshot(now):
    local = now.astimezone(ZoneInfo("America/Los_Angeles"))
    return {
        "timezone": "America/Los_Angeles",
        "current": {
            "time": local.replace(tzinfo=None).isoformat(),
            "temperature_2m": 18.5,
            "weather_code": 0,
        },
        "current_units": {"temperature_2m": "°C"},
        "daily": {
            "time": [local.date().isoformat()],
            "temperature_2m_min": [12.0],
            "temperature_2m_max": [22.0],
        },
        "daily_units": {"temperature_2m_min": "°C", "temperature_2m_max": "°C"},
    }


@pytest.fixture
def clock(monkeypatch):
    value = [datetime(2026, 11, 17, 16, tzinfo=UTC)]

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return value[0].astimezone(tz or UTC)

    monkeypatch.setattr(integrations, "datetime", Clock)
    return value


@pytest.mark.parametrize(
    "start", [datetime(2026, 11, 18, 7, 59, tzinfo=UTC), datetime(2026, 11, 1, 8, 59, tzinfo=UTC)]
)
async def test_weather_reloads_across_local_midnight_and_dst(settings, clock, start):
    clock[0] = start
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url.host == "api.open-meteo.com"
        assert request.url.params["forecast_days"] == "1"
        assert request.url.params["timezone"] == settings.timezone
        assert "start_date" not in request.url.params and "end_date" not in request.url.params
        return httpx.Response(200, json=snapshot(clock[0]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        service = Services(settings, client)
        first = await service.weather()
        clock[0] += timedelta(minutes=2)
        second = await service.weather()
        assert len(calls) == 2
        assert second["daily"]["time"] == [
            clock[0].astimezone(ZoneInfo(settings.timezone)).date().isoformat()
        ]
        assert first["as_of"] != second["as_of"]
        clock[0] += timedelta(days=1)
        third = await service.weather()
        assert len(calls) == 3 and third["daily"]["time"] != second["daily"]["time"]


@pytest.mark.parametrize(
    "bad",
    ["yesterday", "stale", "future", "null", "nan", "empty", "units", "timezone", "reversed_range"],
)
async def test_weather_rejects_invalid_or_stale_data(settings, clock, bad):
    data = snapshot(clock[0])
    if bad == "yesterday":
        data["daily"]["time"] = ["2026-11-16"]
    elif bad == "stale":
        data["current"]["time"] = "2026-11-17T04:00"
    elif bad == "future":
        data["current"]["time"] = "2026-11-18T08:00"
    elif bad == "null":
        data["current"]["temperature_2m"] = None
    elif bad == "nan":
        data["current"]["temperature_2m"] = float("nan")
    elif bad == "empty":
        data["daily"]["temperature_2m_max"] = []
    elif bad == "units":
        data["current_units"]["temperature_2m"] = "°F"
    elif bad == "timezone":
        data["timezone"] = "UTC"
    elif bad == "reversed_range":
        data["daily"]["temperature_2m_min"] = [30]
    # stdlib encoding deliberately permits NaN to test hostile provider JSON.
    import json

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, content=json.dumps(data)))
    ) as client:
        with pytest.raises(PolicyError, match="temporarily unavailable"):
            await Services(settings, client).weather()


@pytest.mark.parametrize("failure", [503, "disconnect", "timeout"])
async def test_weather_retries_transient_read_and_recovers(settings, clock, failure):
    calls = []

    def respond(request):
        calls.append(request)
        if len(calls) == 1:
            if failure == "disconnect":
                raise httpx.ConnectError("synthetic disconnect")
            if failure == "timeout":
                raise httpx.ReadTimeout("synthetic timeout")
            return httpx.Response(failure)
        return httpx.Response(200, json=snapshot(clock[0]))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await Services(settings, client).weather()
    assert result["status"] == "available" and len(calls) == 2


@pytest.mark.parametrize("status,expected", [(429, 1), (403, 1), (400, 1), (503, 2)])
async def test_weather_outage_is_bounded_and_not_cached(settings, clock, status, expected):
    calls = []
    healthy = False

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json=snapshot(clock[0])) if healthy else httpx.Response(status)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        service = Services(settings, client)
        with pytest.raises(PolicyError, match="temporarily unavailable"):
            await service.weather()
        assert len(calls) == expected + 1  # One bounded NWS fallback lookup.
        healthy = True
        clock[0] += timedelta(days=1)
        assert (await service.weather())["status"] == "available"
        assert len(calls) == expected + 2
