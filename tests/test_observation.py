# I developed this file with Codex assistance; see PROCESS_LOG.md.
import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("observation", Path(__file__).parents[1] / "scripts/observation.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)
GATE = {"ready": True, "frozen": False, "blockers": [], "project": "assignment3-515003", "instance": "assignment3-personal-agent"}
CHECKS = {**dict.fromkeys(obs.CHECKS, True), "image": "us-central1-docker.pkg.dev/assignment3-515003/a3/agent@sha256:" + "a"*64}
GATE["reviewed_image"] = CHECKS["image"]
START = datetime(2026, 11, 17, 20, tzinfo=UTC)


def test_observation_requires_every_live_acceptance_and_release_gate():
    for name in obs.CHECKS:
        with pytest.raises(ValueError):
            obs.create_manifest(GATE, {**CHECKS, name: False}, START)
    for change in ({"frozen": True}, {"ready": False}, {"blockers": ["missing test"]}):
        with pytest.raises(ValueError):
            obs.create_manifest({**GATE, **change}, CHECKS, START)
    with pytest.raises(ValueError):
        obs.create_manifest(GATE, {**CHECKS, "image": "latest"}, START)


def test_elapsed_time_alone_does_not_claim_heartbeat_coverage():
    manifest = obs.create_manifest(GATE, CHECKS, START)
    report = obs.summarize(manifest, [], START + timedelta(hours=48))
    assert report["48_hours_elapsed"] is True
    assert report["heartbeat_coverage_passes"] is False
    assert report["largest_heartbeat_gap_seconds"] == 48*3600


def test_gap_and_local_only_heartbeats_remain_visible():
    manifest = obs.create_manifest(GATE, CHECKS, START)
    logs = [{"jsonPayload": {"event": "heartbeat", "outcome": "durable",
                            "timestamp": (START + timedelta(minutes=i)).isoformat()}}
            for i in range(1, 11)]
    assert obs.summarize(manifest, logs, START+timedelta(minutes=11))["heartbeat_coverage_passes"]
    report = obs.summarize(manifest, logs, START+timedelta(minutes=15))
    assert not report["heartbeat_coverage_passes"] and report["largest_heartbeat_gap_seconds"] == 300
    for item in logs:
        item["jsonPayload"]["outcome"] = "local_only"
    assert obs.summarize(manifest, logs, START+timedelta(minutes=11))["durable_heartbeats"] == 0


def test_observation_cannot_claim_a_different_valid_image():
    replacement = CHECKS["image"].replace("a" * 64, "b" * 64)
    with pytest.raises(ValueError, match="reviewed release"):
        obs.create_manifest(GATE, {**CHECKS, "image": replacement}, START)
