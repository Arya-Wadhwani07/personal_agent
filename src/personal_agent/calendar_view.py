# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Compute explicit synthetic-profile availability; never infer gaps from incomplete data."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


def availability(events, day, timezone, *, truncated=False):
    zone = ZoneInfo(timezone)
    start = datetime.combine(day, time(9), zone)
    end = datetime.combine(day, time(17), zone)
    result = {"timezone": timezone, "local_date": day.isoformat(),
              "availability_window": {"start": start.isoformat(), "end": end.isoformat()},
              "free_gaps": [], "gaps_status": "unavailable"}
    if truncated:
        return result
    busy = []
    try:
        for event in events:
            if event.get("status") == "cancelled" or event.get("transparency") == "transparent":
                continue
            def point(value):
                if value.get("dateTime"):
                    stamp = datetime.fromisoformat(value["dateTime"].replace("Z", "+00:00"))
                    if stamp.tzinfo is None:
                        stamp = stamp.replace(tzinfo=ZoneInfo(value.get("timeZone", timezone)))
                    return stamp.astimezone(zone)
                return datetime.combine(date.fromisoformat(value["date"]), time.min, zone)
            a, b = point(event["start"]), point(event["end"])
            if b <= a:
                raise ValueError("Invalid event interval")
            a, b = max(a, start), min(b, end)
            if a < b:
                busy.append((a, b))
    except (AttributeError, KeyError, TypeError, ValueError):
        return result
    cursor = start
    for a, b in sorted(busy):
        if a > cursor:
            result["free_gaps"].append({"start": cursor.isoformat(), "end": a.isoformat()})
        cursor = max(cursor, b)
    if cursor < end:
        result["free_gaps"].append({"start": cursor.isoformat(), "end": end.isoformat()})
    result["gaps_status"] = "complete"
    return result


def local_window(now, days, timezone):
    zone = ZoneInfo(timezone)
    day = now.astimezone(zone).date()
    return (datetime.combine(day, time.min, zone),
            datetime.combine(day + timedelta(days=days), time.min, zone))


def meeting_alert(event, timezone):
    """Keep the event's exact local time in trusted alerts, independent of model wording."""
    zone = ZoneInfo(timezone)

    def point(value):
        stamp = datetime.fromisoformat(value["dateTime"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=ZoneInfo(value.get("timeZone", timezone)))
        return stamp.astimezone(zone)

    start = point(event["start"])
    start_text = start.strftime("%a, %b %d · %I:%M %p %Z (UTC%z)")
    try:
        end = point(event.get("end") or {})
        end_text = end.strftime("%a, %b %d · %I:%M %p %Z (UTC%z)") if end.timestamp() > start.timestamp() else "unavailable"
    except (KeyError, TypeError, ValueError):
        end_text = "unavailable"
    title = str(event.get("summary") or "Untitled meeting")[:300]
    return start, f"Meeting soon: {title}\nStarts: {start_text}\nEnds: {end_text}\nTimezone: {timezone}"
