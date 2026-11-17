# I developed this file with Codex assistance; see PROCESS_LOG.md.
import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("observation", Path(__file__).parents[1] / "scripts/observation.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)
GATE = {"region": "us-west1", "ready": True, "frozen": True, "blockers": [], "project": "assignment3-515003", "instance": "assignment3-personal-agent"}
CHECKS = {"region": "us-west1", **dict.fromkeys(obs.CHECKS, True), "image": "us-central1-docker.pkg.dev/assignment3-515003/a3/agent@sha256:" + "a"*64}
GATE["reviewed_image"] = CHECKS["image"]
START = datetime(2026, 11, 17, 20, tzinfo=UTC)


def test_observation_requires_every_live_acceptance_and_release_gate():
    for name in obs.CHECKS:
        with pytest.raises(ValueError):
            obs.create_manifest(GATE, {**CHECKS, name: False}, START)
    for change in ({"frozen": False}, {"ready": False}, {"blockers": ["missing test"]}):
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


def test_observation_records_actual_reviewed_instance_region():
    assert obs.create_manifest(GATE, CHECKS, START)["region"] == "us-west1"
    for region in (None, "us-central1", "us-west2"):
        with pytest.raises(ValueError, match="Observation region"):
            obs.create_manifest(GATE, {**CHECKS, "region": region}, START)
        with pytest.raises(ValueError, match="Observation region"):
            obs.create_manifest({**GATE, "region": region}, CHECKS, START)


def test_freeze_is_a_separate_pre_observation_step():
    unfrozen = {**GATE, "frozen": False}
    result = obs.freeze_gate(unfrozen)
    assert result["frozen"] is True
    assert unfrozen["frozen"] is False
    for change in ({"ready": False}, {"blockers": ["acceptance failure"]}):
        with pytest.raises(ValueError):
            obs.freeze_gate({**unfrozen, **change})


def test_start_does_not_modify_tracked_release_config(tmp_path, monkeypatch):
    import json
    import sys

    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir()
    gate_path = tmp_path / "config/release.json"
    gate_path.write_text(json.dumps(GATE))
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text(json.dumps(CHECKS))
    before = gate_path.read_bytes()
    monkeypatch.setattr(sys, "argv", ["observation.py", "--start", str(acceptance)])
    monkeypatch.setattr(obs, "MANIFEST", tmp_path / "evidence/manifest.json")
    calls = []
    monkeypatch.setattr(obs, "command", lambda args: calls.append(args) or "")
    obs.main()
    assert gate_path.read_bytes() == before
    assert json.loads(obs.MANIFEST.read_text())["region"] == "us-west1"
    assert len(calls) == 2
