# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Start and export a genuine observation interval; never accept a backdated start."""
import argparse
import json
import re
import subprocess  # nosec B404
from datetime import UTC, datetime
from pathlib import Path

CHECKS = ("security_gate", "cloud_reply", "gemma_private_link", "google_read", "telegram_reply",
          "scheduled_delivery", "durable_restart", "grader_ui", "cost_review")
MANIFEST = Path("evidence/observation/manifest.json")


def create_manifest(gate, acceptance, now=None):
    if gate.get("ready") is not True or gate.get("blockers") or gate.get("frozen"):
        raise ValueError("A ready, approved release is required before observation")
    if any(acceptance.get(k) is not True for k in CHECKS):
        raise ValueError("All live acceptance checks must pass first")
    image = acceptance.get("image", "")
    expected = r"us-central1-docker.pkg.dev/assignment3-515003/a3/agent@sha256:[a-f0-9]{64}"
    if not re.fullmatch(expected, image):
        raise ValueError("The observed immutable release digest is required")
    return {"schema": 1, "started_at": (now or datetime.now(UTC)).isoformat(),
            "required_hours": 48, "project": gate["project"], "instance": gate["instance"],
            "region": "us-central1", "image": image, "cloud_model": "gpt-6.1-sol",
            "local_model": "gemma4:e2b", "acceptance": {k: True for k in CHECKS}}


def summarize(manifest, logs, now=None):
    start = datetime.fromisoformat(manifest["started_at"])
    end = now or datetime.now(UTC)
    beats = []
    events = {}
    for record in logs:
        payload = record.get("jsonPayload", {})
        kind = payload.get("event", "")
        events[kind] = events.get(kind, 0) + 1
        if kind == "heartbeat" and payload.get("outcome") == "durable":
            point = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
            if start <= point <= end:
                beats.append(point)
    points = [start, *sorted(set(beats)), end]
    gap = max((b-a).total_seconds() for a, b in zip(points, points[1:], strict=False))
    elapsed = (end-start).total_seconds()
    return {"started_at": start.isoformat(), "collected_at": end.isoformat(),
            "elapsed_hours": elapsed/3600, "durable_heartbeats": len(beats),
            "largest_heartbeat_gap_seconds": gap, "events": events,
            "48_hours_elapsed": elapsed >= 48*3600,
            "heartbeat_coverage_passes": bool(beats) and gap <= 180,
            "note": "Heartbeat coverage is not proof of every feature or absence of platform restarts; review lifecycle logs and live grading checks separately."}


def command(args):
    invocation = ["gcloud", *args, "--project=assignment3-515003", "--quiet"]
    result = subprocess.run(invocation,  # noqa: S603  # nosec B603
                            capture_output=True, text=True, timeout=120)  # noqa: S603,S607  # nosec B603,B607
    if result.returncode:
        raise RuntimeError("Observation cloud operation failed; no success recorded")
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--start", type=Path, metavar="LIVE_ACCEPTANCE_JSON")
    actions.add_argument("--collect", action="store_true")
    args = parser.parse_args()
    if args.start:
        gate_path = Path("config/release.json")
        gate = json.loads(gate_path.read_text())
        manifest = create_manifest(gate, json.loads(args.start.read_text()))
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("x") as stream:
            json.dump(manifest, stream, indent=2)
        # Freeze before any asynchronous export; failure remains visibly frozen for recovery.
        gate["frozen"] = True
        gate_path.write_text(json.dumps(gate, indent=2) + "\n")
        stamp = manifest["started_at"].replace(":", "-")
        command(["storage", "cp", str(MANIFEST), "gs://assignment3-515003-a3-state/evidence/" + stamp + "/manifest.json"])
        command(["logging", "write", "a3-observation", json.dumps(manifest), "--payload-type=json"])
        print("Observation started at", manifest["started_at"], "UTC; deployment is frozen")
    else:
        manifest = json.loads(MANIFEST.read_text())
        query = ('resource.type="cloud_run_instance" AND resource.labels.instance_name="'
                 + manifest["instance"] + '" AND timestamp>="' + manifest["started_at"]
                 + '" AND jsonPayload.event:*')
        raw = command(["logging", "read", query, "--order=asc", "--limit=20000", "--format=json"])
        logs = json.loads(raw)
        if len(logs) >= 20000:
            raise RuntimeError("Export reached its limit; use paginated export before claiming interval coverage")
        (MANIFEST.parent / "events.json").write_text(raw)
        report = summarize(manifest, logs)
        (MANIFEST.parent / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
