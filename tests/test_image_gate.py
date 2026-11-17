# I developed this file with Codex assistance; see PROCESS_LOG.md.
import copy
import importlib.util
from datetime import date
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("image_gate", Path(__file__).parents[1] / "scripts/image_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
PROOF = {"schema": 1, "uid": 10001, "caps": 0, "no_new_privileges": True, "sqlite": "3.54.1",
         "acl_fixed_abi": True, "setuid_files": [], "perl_archive_tar_absent": True,
         "hermes_ws_boundary_rejects_attack": True, "public_websocket_routes": False,
         "removed_utilities": ["/usr/bin/mount", "/usr/bin/umount", "/usr/bin/nsenter", "/usr/bin/infocmp", "/usr/lib/systemd/systemd-homed"]}
REPORT = {"Metadata": {"ImageID": "synthetic-image"}, "Results": [{"Vulnerabilities": [
    {"VulnerabilityID": "CVE-test", "Severity": "HIGH", "PkgName": "synthetic", "InstalledVersion": "1"}]}]}
REVIEW = {"CVE-test": {"packages": {"synthetic": "1"}, "basis": "Synthetic test disposition",
                       "review_expires": "2026-11-24"}}


def test_unknown_changed_and_critical_findings_block():
    assert not gate.evaluate(REPORT, PROOF, REVIEW, today=date(2026, 11, 17))["blocked"]
    assert gate.evaluate(REPORT, PROOF, {}, today=date(2026, 11, 17))["blocked"]
    for field, value in (("Severity", "CRITICAL"), ("InstalledVersion", "2"), ("PkgName", "other")):
        report = copy.deepcopy(REPORT)
        report["Results"][0]["Vulnerabilities"][0][field] = value
        assert gate.evaluate(report, PROOF, REVIEW, today=date(2026, 11, 17))["blocked"]
    assert gate.evaluate(REPORT, PROOF, REVIEW, today=date(2026, 11, 25))["blocked"]


@pytest.mark.parametrize("change", [{"uid": 0}, {"caps": 1}, {"no_new_privileges": False},
    {"setuid_files": ["unexpected"]}, {"removed_utilities": []}, {"acl_fixed_abi": False},
    {"hermes_ws_boundary_rejects_attack": False}, {"public_websocket_routes": True}])
def test_profile_drift_invalidates_every_disposition(change):
    with pytest.raises(ValueError):
        gate.evaluate(REPORT, {**PROOF, **change}, REVIEW)
