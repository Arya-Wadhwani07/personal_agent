# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Native Hermes cron heartbeat: checkpoint state and emit a silent operational event."""

import os

import httpx

with httpx.Client(timeout=90, trust_env=False) as client:
    response = client.post(
        "http://127.0.0.1:8090/checkpoint",
        headers={"Authorization": "Bearer " + os.environ["A3_INTERNAL_KEY"]},
    )
if response.status_code != 200:
    raise SystemExit("Checkpoint failed; inspect the operational evidence")
print("[SILENT]")
