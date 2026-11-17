# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Reconcile my managed native Hermes jobs without erasing history or resuming paused jobs."""

import os
from pathlib import Path

from cron.jobs import create_job, list_jobs, parse_schedule, update_job

MANAGED_NAMES = {"a3-checkpoint", "a3-morning", "a3-recap", "a3-content", "a3-alerts"}


def definitions(owner):
    here = Path(__file__).resolve().parent
    jobs = [{
        "name": "a3-checkpoint", "schedule": "* * * * *", "prompt": None,
        "script": str(here / "checkpoint.py"), "no_agent": True, "deliver": "local",
        "enabled_toolsets": [], "timezone": "America/Los_Angeles", "catch_up": False,
    }]
    if not owner.isascii() or not owner.isdigit():
        return jobs
    for name, schedule, prompt in (
        ("a3-morning", "0 8 * * *",
         "Give my morning briefing using a3_calendar, a3_email and a3_weather. Include today's events, free gaps, weather and one-line unread/flagged email summaries. Report unavailable sources honestly; do not invent data."),
        ("a3-recap", "0 20 * * *",
         "Give my end-of-day recap using a3_activity and a3_calendar with days=2: completed tasks/messages, pending decisions and tomorrow's early meetings/deadlines. Do not invent activity or claim an unconfirmed send."),
        ("a3-content", "0 9 * * *",
         "Check a3_content_history, research a useful Agentic AI topic using a3_search, and write an original LinkedIn draft with source links. Run a3_review_content on its claim/source ledger before saving with a3_content_brief. Deliver for human review; never publish or invent research when search is unavailable."),
    ):
        jobs.append({
            "name": name, "schedule": schedule, "prompt": prompt, "script": None,
            "no_agent": False, "deliver": "telegram:" + owner,
            "enabled_toolsets": ["assignment3"], "timezone": "America/Los_Angeles",
            "catch_up": False,
        })
    jobs.append({
        "name": "a3-alerts", "schedule": "*/5 * * * *", "prompt": None,
        "script": str(here / "alerts.py"), "no_agent": True, "deliver": "local",
        "enabled_toolsets": [], "timezone": "America/Los_Angeles", "catch_up": False,
    })
    return jobs


def reconcile(owner):
    existing = {}
    for job in list_jobs(include_disabled=True):
        if job["name"] not in MANAGED_NAMES:
            continue
        if job["name"] in existing:
            raise RuntimeError("Duplicate managed schedule; review before startup")
        existing[job["name"]] = job
    specs = definitions(owner)
    active_names = {spec["name"] for spec in specs}
    changes = []
    # Without an owner, old restored notification jobs must not retain authority to send.
    for name, job in existing.items():
        if name not in active_names and job.get("enabled"):
            update_job(job["id"], {
                "enabled": False, "state": "paused", "paused_reason": "Class-only owner is missing",
            })
            changes.append((name, "paused"))
    for spec in specs:
        name = spec["name"]
        job = existing.get(name)
        if job is None:
            create_job(**spec)
            changes.append((name, "created"))
            continue
        updates = {}
        for key, desired in spec.items():
            if key == "name":
                continue
            current = job.get(key)
            compared = parse_schedule(desired) if key == "schedule" else desired
            if key in ("prompt", "script"):
                current, compared = current or "", compared or ""
            if current != compared:
                updates[key] = desired
        if updates:
            # No enabled/state/history fields are changed here. A pause remains a pause.
            if update_job(job["id"], updates) is None:
                raise RuntimeError("Managed schedule disappeared during startup")
            changes.append((name, "updated"))
    return changes


if __name__ == "__main__":
    for name, action in reconcile(os.environ.get("TELEGRAM_ALLOWED_USERS", "")):
        print(action, name)
