# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Validate NWS forecast periods without presenting forecasts as observations."""

import math
import re
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from .state import PolicyError


def forecast_url(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"https://api\.weather\.gov/gridpoints/[A-Z]{3}/-?[0-9]+,-?[0-9]+/forecast", value
    ):
        raise PolicyError("Invalid NWS forecast reference")
    return value


def nws_snapshot(data, timezone, now):
    try:
        p = data["properties"]
        generated = datetime.fromisoformat(p["generatedAt"].replace("Z", "+00:00"))
        if generated.tzinfo is None or not -900 <= (now - generated).total_seconds() <= 43200:
            raise ValueError("Stale NWS forecast")
        zone = ZoneInfo(timezone)
        periods = []
        for item in p["periods"][:14]:
            start = datetime.fromisoformat(item["startTime"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(item["endTime"].replace("Z", "+00:00"))
            if start.tzinfo is None or end.tzinfo is None or end <= start:
                raise ValueError("Invalid forecast interval")
            if end <= now or (start - now).total_seconds() > 172800:
                continue
            value = item["temperature"]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("Invalid forecast temperature")
            unit = item["temperatureUnit"]
            if unit not in ("C", "F") or type(item["isDaytime"]) is not bool:
                raise ValueError("Invalid forecast units")
            value = (value - 32) * 5 / 9 if unit == "F" else value
            if not -100 <= value <= 70:
                raise ValueError("Invalid forecast temperature")
            condition = item["shortForecast"]
            if not isinstance(condition, str) or not condition.strip():
                raise ValueError("Missing forecast description")
            periods.append(
                {
                    "name": str(item["name"])[:80],
                    "start": start.astimezone(zone).isoformat(),
                    "end": end.astimezone(zone).isoformat(),
                    "temperature_c": round(value, 1),
                    "temperature_kind": "high" if item["isDaytime"] else "low",
                    "forecast": condition[:200],
                }
            )
            if len(periods) == 4:
                break
        if not periods:
            raise ValueError("No current forecast periods")
    except (KeyError, ValueError, TypeError, IndexError, AttributeError) as exc:
        raise PolicyError("NWS forecast is stale or invalid") from exc
    return {
        "status": "available",
        "source": "https://www.weather.gov/",
        "provider": "NWS fallback",
        "timezone": timezone,
        "as_of": now.astimezone(UTC).isoformat(),
        "generated_at": generated.isoformat(),
        "forecast_periods": periods,
        "instruction": "These are forecasts, not current observations. Use each named local period and its high/low; do not invent a missing daytime high or current temperature.",
    }
