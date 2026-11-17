# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Install native Hermes cron jobs once, using a synthetic Telegram destination."""

import os

from cron.jobs import create_job, list_jobs

owner = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
existing = {job["name"] for job in list_jobs()}
if "a3-checkpoint" not in existing:
    from pathlib import Path

    create_job(
        name="a3-checkpoint",
        schedule="* * * * *",
        prompt=None,
        script=str(Path(__file__).with_name("checkpoint.py").resolve()),
        no_agent=True,
        deliver="local",
        timezone="America/Los_Angeles",
        catch_up=False,
    )
if not owner.isdigit():
    raise SystemExit(0)  # State heartbeat works before class-only messaging is configured.

jobs = [
    (
        "a3-morning",
        "0 8 * * *",
        "Give my morning briefing using calendar, email and weather. Include events, free gaps, weather and one-line unread/flagged email summaries.",
    ),
    (
        "a3-recap",
        "0 20 * * *",
        "Give my end-of-day recap using a3_activity and tomorrow's calendar: completed tasks/messages, pending decisions and early meetings/deadlines. Do not invent activity.",
    ),
    (
        "a3-content",
        "0 9 * * *",
        "Check content history, research a useful Agentic AI topic using a3_search, write an original LinkedIn draft with source links, and save using a3_content_brief. Deliver for review, never publish.",
    ),
]
for name, schedule, prompt in jobs:
    if name not in existing:
        create_job(
            name=name,
            schedule=schedule,
            prompt=prompt,
            deliver="telegram:" + owner,
            enabled_toolsets=["assignment3"],
            timezone="America/Los_Angeles",
            catch_up=False,
        )
        print("Created", name)

if "a3-alerts" not in existing:
    from pathlib import Path

    create_job(
        name="a3-alerts",
        schedule="*/5 * * * *",
        prompt=None,
        script=str(Path(__file__).with_name("alerts.py").resolve()),
        no_agent=True,
        deliver="local",
        timezone="America/Los_Angeles",
        catch_up=False,
    )
