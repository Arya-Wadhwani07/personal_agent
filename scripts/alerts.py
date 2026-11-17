# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Native Hermes cron entry; trusted delivery happens inside the policy broker."""

import os

import httpx

with httpx.Client(timeout=120, trust_env=False) as client:
    response = client.post(
        "http://127.0.0.1:8090/jobs/alerts",
        headers={"Authorization": "Bearer " + os.environ["A3_INTERNAL_KEY"]},
    )
    if response.status_code != 200:
        raise SystemExit("Alert run failed; inspect sanitized service status")
print("[SILENT]")
