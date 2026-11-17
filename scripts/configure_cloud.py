# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Upload project-local credential payloads without printing them; grant only per-secret access."""

import argparse
import json
import subprocess  # nosec B404
from pathlib import Path

from provision_cloud import DEPLOY, PROJECT, RUNTIME

NAMES = (
    "a3-api-key",
    "a3-internal-key",
    "a3-nvidia-key",
    "a3-telegram-token",
    "a3-google-client-secret",
    "a3-google-refresh-token",
    "a3-tavily-key",
    "a3-hermes-oauth",
    "a3-runtime-env",
    "a3-tailscale-auth-key",
)


def call(args):
    command = ["gcloud", *args, "--project=" + PROJECT, "--quiet"]
    return subprocess.run(  # noqa: S603  # nosec B603
        command,  # noqa: S603  # nosec B603
        capture_output=True,
        timeout=90,
    )  # noqa: S603  # nosec B603


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        print("Prepare/version these project secrets and grant runtime access:", ", ".join(NAMES))
        return
    folder = Path(".cache/cloud/staged-secrets")
    # Verify every payload before the first external mutation.
    for name in NAMES:
        path = folder / (name + ".txt")
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size < 1048576:
            raise SystemExit("Missing/invalid private payload: " + name)
    versions = {}
    for name in NAMES:
        path = folder / (name + ".txt")
        described = call(["secrets", "describe", name, "--format=json"])
        if described.returncode:
            if b"NOT_FOUND" not in described.stderr:
                raise SystemExit("Cannot inspect secret: " + name)
            result = call(
                ["secrets", "create", name, "--replication-policy=automatic", "--format=json"]
            )
            if result.returncode:
                raise SystemExit("Cannot create secret: " + name)
        existing = call(["secrets", "versions", "access", "latest", "--secret=" + name])
        if existing.returncode == 0 and existing.stdout == path.read_bytes():
            info = call(
                ["secrets", "versions", "describe", "latest", "--secret=" + name, "--format=json"]
            )
        else:
            if existing.returncode and b"NOT_FOUND" not in existing.stderr:
                raise SystemExit("Cannot inspect previous version: " + name)
            info = call(
                ["secrets", "versions", "add", name, "--data-file=" + str(path), "--format=json"]
            )
        if info.returncode:
            raise SystemExit("Cannot save secret version: " + name)
        versions[name] = json.loads(info.stdout)["name"].rsplit("/", 1)[-1]
        identity = DEPLOY if name == "a3-runtime-env" else RUNTIME
        result = call(
            [
                "secrets",
                "add-iam-policy-binding",
                name,
                "--member=serviceAccount:" + identity,
                "--role=roles/secretmanager.secretAccessor",
                "--format=json",
            ]
        )
        if result.returncode:
            raise SystemExit("Cannot grant scoped secret access: " + name)
        print("Versioned and scoped", name, flush=True)
    out = Path(".cache/cloud/secret-versions.json")
    out.write_text(json.dumps(versions, indent=2) + "\n")
    out.chmod(0o600)


if __name__ == "__main__":
    main()
