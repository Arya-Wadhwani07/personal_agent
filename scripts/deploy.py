# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Fail-closed release plan. Cloud resources are never created by normal CI."""

import argparse
import json
import os
import re
import shlex
import subprocess  # nosec B404
from decimal import Decimal, InvalidOperation
from pathlib import Path


def command(env, gate):
    if gate.get("frozen"):
        raise ValueError("Observation/grading freeze blocks deployment")
    if gate.get("ready") is not True or gate.get("blockers"):
        raise ValueError("Release is blocked: " + "; ".join(gate.get("blockers", [])))
    project = env.get("A3_GCP_PROJECT", "")
    region = env.get("A3_REGION", "")
    image = env.get("A3_IMAGE", "")
    if not re.fullmatch(r"[a-z][a-z0-9-]{4,61}[a-z0-9]", project):
        raise ValueError("Explicit GCP project required")
    if not re.fullmatch(r"[a-z]+-[a-z]+[0-9]", region):
        raise ValueError("Supported Instance region must be selected and verified")
    if project != gate.get("project"):
        raise ValueError("Deployment project differs from the reviewed release gate")
    try:
        requested = Decimal(str(env.get("A3_BUDGET_USD", "0")))
        approved = Decimal(str(gate.get("budget_usd", "0")))
    except (InvalidOperation, ValueError):
        raise ValueError("Finite approved spending limit required") from None
    if not requested.is_finite() or not approved.is_finite() or not 0 < requested <= approved:
        raise ValueError("Declared budget must be positive and within the approved ceiling")
    # This validates release authorization; it is not a cloud billing hard cap.
    # Actual usage monitoring and a funded availability window remain release gates.
    if not re.fullmatch(
        r"[a-z0-9.-]+-docker.pkg.dev/" + re.escape(project) + r"/[a-z0-9/_-]+@sha256:[a-f0-9]{64}",
        image,
    ):
        raise ValueError("Reviewed project-owned Artifact Registry image digest required")
    primary_auth = gate.get("primary_auth")
    if primary_auth != "oauth":
        raise ValueError("This reviewed release profile requires Hermes OAuth")
    secrets = [
        "API_SERVER_KEY=a3-api-key:latest",
        "A3_INTERNAL_KEY=a3-internal-key:latest",
        "NVIDIA_API_KEY=a3-nvidia-key:latest",
        "TELEGRAM_BOT_TOKEN=a3-telegram-token:latest",
        "GOOGLE_CLIENT_SECRET=a3-google-client-secret:latest",
        "GOOGLE_REFRESH_TOKEN=a3-google-refresh-token:latest",
        "TAVILY_API_KEY=a3-tavily-key:latest",
        "TS_AUTHKEY=a3-tailscale-auth-key:latest",
    ]
    version = str(gate.get("oauth_secret_version", ""))
    if not re.fullmatch(r"[1-9][0-9]*", version):
        raise ValueError("Pinned cloud OAuth bootstrap secret version required")
    secrets.append("/run/a3-oauth/auth.json=a3-hermes-oauth:" + version)
    return [
        "gcloud",
        "beta",
        "run",
        "instances",
        "deploy",
        gate["instance"],
        "--project",
        project,
        "--region",
        region,
        "--image",
        image,
        "--port",
        "8080",
        "--cpu",
        gate["cpu"],
        "--memory",
        gate["memory"],
        "--restart-policy",
        "on-failure",
        "--startup-probe",
        "httpGet.path=/health,httpGet.port=8080,timeoutSeconds=5,periodSeconds=10,failureThreshold=24",
        "--service-account",
        "a3-runtime@" + project + ".iam.gserviceaccount.com",
        "--env-vars-file",
        "config/cloud-env.yaml",
        "--set-secrets",
        ",".join(secrets),
        "--no-invoker-iam-check",
        "--quiet",
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        cmd = command(os.environ, json.loads(Path("config/release.json").read_text()))
    except (ValueError, KeyError) as exc:
        raise SystemExit(str(exc)) from None
    if args.execute:
        # No shell interpolation; identifiers/digest are validated above.
        subprocess.run(cmd, check=True, timeout=600)  # noqa: S603  # nosec B603
    else:
        print(shlex.join(cmd))


if __name__ == "__main__":
    main()
