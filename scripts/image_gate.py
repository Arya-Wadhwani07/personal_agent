# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Fail closed on unknown/expired image findings; retain the complete scanner report."""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path


def evaluate(report, proof, dispositions, *, today=None):
    today = today or date.today()
    if (proof.get("schema") != 1 or proof.get("uid", 0) == 0 or proof.get("caps") != 0
        or proof.get("no_new_privileges") is not True or proof.get("sqlite") != "3.54.1"
        or proof.get("acl_fixed_abi") is not True or proof.get("setuid_files") != []
        or proof.get("perl_archive_tar_absent") is not True
        or proof.get("hermes_ws_boundary_rejects_attack") is not True
        or proof.get("public_websocket_routes") is not False):
        raise ValueError("Runtime profile does not support the reviewed dispositions")
    required = {"/usr/bin/mount", "/usr/bin/umount", "/usr/bin/nsenter", "/usr/bin/infocmp",
                "/usr/lib/systemd/systemd-homed"}
    if not required.issubset(proof.get("removed_utilities", [])):
        raise ValueError("Missing component-absence evidence")
    if not isinstance(report.get("Results"), list) or not report.get("Metadata", {}).get("ImageID"):
        raise ValueError("Missing complete image scanner report")
    blocked, dispositioned = [], []
    for result in report["Results"]:
        for finding in result.get("Vulnerabilities", []) or []:
            if finding.get("Severity") not in {"HIGH", "CRITICAL"}:
                continue
            identifier = finding["VulnerabilityID"]
            review = dispositions.get(identifier, {})
            matches = (finding["Severity"] != "CRITICAL"
                       and review.get("packages", {}).get(finding["PkgName"]) == finding["InstalledVersion"]
                       and review.get("basis")
                       and date.fromisoformat(review.get("review_expires", "1970-01-01")) >= today)
            (dispositioned if matches else blocked).append({"id": identifier, "package": finding["PkgName"]})
    return {"image_id": report["Metadata"]["ImageID"], "blocked": blocked,
            "profile_dispositions": dispositioned, "raw_scan_preserved": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("proof", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    proof = json.loads(args.proof.read_text())
    expected = hashlib.sha256(Path("scripts/image_profile.py").read_bytes()).hexdigest()
    if proof.get("checker_sha256") != expected:
        raise SystemExit("Image proof does not use the current reviewed checker")
    result = evaluate(json.loads(args.report.read_text()), proof,
                      json.loads(Path("config/image-dispositions.json").read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("Release-blocking findings:", len(result["blocked"]),
          "Profile-specific dispositions:", len(result["profile_dispositions"]))
    raise SystemExit(1 if result["blocked"] else 0)


if __name__ == "__main__":
    main()
