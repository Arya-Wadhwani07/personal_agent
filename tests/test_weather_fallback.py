# I developed this file with Codex assistance; see PROCESS_LOG.md.
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from personal_agent import integrations
from personal_agent.integrations import Services
from personal_agent.state import PolicyError
from personal_agent.weather_fallback import forecast_url, nws_snapshot

NOW = datetime(2026, 11, 18, 5, 30, tzinfo=UTC)
URL = "https://api.weather.gov/gridpoints/LOX/155,45/forecast"


def data():
    return {
        "properties": {
            "generatedAt": NOW.isoformat(),
            "periods": [
                {
                    "name": "Tonight",
                    "startTime": "2026-11-17T20:00:00-08:00",
                    "endTime": "2026-11-18T06:00:00-08:00",
                    "isDaytime": False,
                    "temperature": 50,
                    "temperatureUnit": "F",
                    "shortForecast": "Partly Cloudy",
                },
                {
                    "name": "Wednesday",
                    "startTime": "2026-11-18T06:00:00-08:00",
                    "endTime": "2026-11-18T18:00:00-08:00",
                    "isDaytime": True,
                    "temperature": 68,
                    "temperatureUnit": "F",
                    "shortForecast": "Mostly Sunny",
                },
            ],
        }
    }


async def test_live_style_tls_failure_falls_back_without_following_arbitrary_urls(
    settings, monkeypatch
):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW

    monkeypatch.setattr(integrations, "datetime", Clock)
    calls = []

    def respond(request):
        calls.append(str(request.url))
        if request.url.host == "api.open-meteo.com":
            raise httpx.ConnectTimeout("Synthetic TLS handshake timeout")
        assert request.headers["User-Agent"].startswith("MondayAssignment3/")
        if request.url.path.startswith("/points/"):
            return httpx.Response(200, json={"properties": {"forecast": URL}})
        assert str(request.url) == URL
        return httpx.Response(200, json=data())

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await Services(settings, client).weather()
    assert len(calls) == 4
    assert result["provider"] == "NWS fallback"
    assert result["forecast_periods"][0]["temperature_c"] == 10
    assert result["forecast_periods"][0]["temperature_kind"] == "low"
    assert result["forecast_periods"][1]["temperature_c"] == 20
    assert "current" not in result


@pytest.mark.parametrize(
    "url",
    [
        "http://api.weather.gov/gridpoints/LOX/155,45/forecast",
        "https://api.weather.gov.evil.test/gridpoints/LOX/155,45/forecast",
        "https://127.0.0.1/forecast",
        "https://api.weather.gov@evil.test/forecast",
        URL + "?redirect=https://evil.test",
        URL + "/../../secrets",
    ],
)
def test_fallback_reference_rejects_ssrf(url):
    with pytest.raises(PolicyError):
        forecast_url(url)


@pytest.mark.parametrize("bad", ["stale", "future", "null", "nan", "unit", "empty"])
def test_nws_rejects_invalid_data(bad):
    d = data()
    if bad == "stale":
        d["properties"]["generatedAt"] = (NOW - timedelta(days=1)).isoformat()
    if bad == "future":
        d["properties"]["generatedAt"] = (NOW + timedelta(days=1)).isoformat()
    if bad == "null":
        d["properties"]["periods"][0]["temperature"] = None
    if bad == "nan":
        d["properties"]["periods"][0]["temperature"] = float("nan")
    if bad == "unit":
        d["properties"]["periods"][0]["temperatureUnit"] = "K"
    if bad == "empty":
        d["properties"]["periods"] = []
    with pytest.raises(PolicyError):
        nws_snapshot(d, "America/Los_Angeles", NOW)


def test_nws_excludes_expired_periods_and_retains_local_dates():
    d = data()
    now = datetime(2026, 11, 18, 16, tzinfo=UTC)
    d["properties"]["generatedAt"] = now.isoformat()
    result = nws_snapshot(d, "America/Los_Angeles", now)
    assert len(result["forecast_periods"]) == 1
    assert result["forecast_periods"][0]["start"].startswith("2026-11-18T06:00")
    assert result["forecast_periods"][0]["temperature_kind"] == "high"
