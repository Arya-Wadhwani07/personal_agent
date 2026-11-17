# I developed this file with Codex assistance; see PROCESS_LOG.md.
from datetime import UTC, date, datetime

from personal_agent.calendar_view import availability, local_window

DAY = date(2026, 11, 17)
ZONE = "America/Los_Angeles"


def event(start, end):
    return {"start": {"dateTime": f"2026-11-17T{start}:00-08:00"},
            "end": {"dateTime": f"2026-11-17T{end}:00-08:00"}}


def test_overlaps_and_outside_window_do_not_create_false_gaps():
    result = availability([event("08:00", "10:00"), event("09:30", "11:00"),
                           event("14:00", "19:00")], DAY, ZONE)
    assert result["gaps_status"] == "complete"
    assert result["free_gaps"] == [{"start": "2026-11-17T11:00:00-08:00",
                                    "end": "2026-11-17T14:00:00-08:00"}]


def test_all_day_events_and_transparent_entries():
    all_day = {"start": {"date": "2026-11-17"}, "end": {"date": "2026-11-18"}}
    assert availability([all_day], DAY, ZONE)["free_gaps"] == []
    view = availability([{**all_day, "transparency": "transparent"}], DAY, ZONE)
    assert view["free_gaps"] == [view["availability_window"]]


def test_incomplete_or_malformed_data_never_claims_availability():
    for events, truncated in (([], True), ([{"start": {"date": "2026-11-17"}}], False),
                              ([event("12:00", "11:00")], False)):
        result = availability(events, DAY, ZONE, truncated=truncated)
        assert result["gaps_status"] == "unavailable"
        assert result["free_gaps"] == []


def test_local_calendar_day_ends_at_midnight_even_across_dst():
    start, end = local_window(datetime(2026, 11, 1, 16, tzinfo=UTC), 1, ZONE)
    assert start.isoformat() == "2026-11-01T00:00:00-07:00"
    assert end.isoformat() == "2026-11-02T00:00:00-08:00"
    assert (end.astimezone(UTC)-start.astimezone(UTC)).total_seconds() == 25*3600
