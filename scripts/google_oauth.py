# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Interactive class-only Google consent; run inside the isolated setup container."""

import argparse
import json
import os
from pathlib import Path

import httpx
from dotenv import set_key
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events.readonly",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--class-email", required=True)
    parser.add_argument("--client", default="/workspace/secrets/google-client.json")
    parser.add_argument("--env-file", default="/workspace/.env")
    args = parser.parse_args()
    root = Path("/workspace").resolve()
    client_path = Path(args.client).resolve()
    target = Path(args.env_file).resolve()
    if not client_path.is_relative_to(root / "secrets") or target != root / ".env":
        raise SystemExit("OAuth files must stay in the assigned project paths")
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_path), SCOPES, autogenerate_code_verifier=True
    )
    original_fetch_token = flow.fetch_token
    flow.fetch_token = lambda **kwargs: original_fetch_token(timeout=20, **kwargs)
    # Only the container listener binds broadly; Docker must publish 127.0.0.1:8765.
    credentials = flow.run_local_server(
        host="127.0.0.1",
        bind_addr="0.0.0.0",  # noqa: S104  # nosec B104
        port=8765,
        open_browser=False,
        timeout_seconds=600,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message="Open this consent URL in my browser:\n{url}",
        success_message="A3 Google callback received. Return to chat for token-save verification.",
    )
    with httpx.Client(timeout=20, trust_env=False) as client:
        response = client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/profile",
            headers={"Authorization": "Bearer " + credentials.token},
        )
        response.raise_for_status()
        if response.json().get("emailAddress", "").lower() != args.class_email.lower():
            raise SystemExit(
                "Account mismatch. No credentials were saved; revoke this unintended consent."
            )
    if not credentials.refresh_token:
        raise SystemExit("No refresh token returned; review offline consent and retry")
    os.umask(0o077)
    target.touch(mode=0o600, exist_ok=True)
    target.chmod(0o600)
    config = json.loads(client_path.read_text())["installed"]
    for name, value in {
        "GOOGLE_CLIENT_ID": config["client_id"],
        "GOOGLE_CLIENT_SECRET": config["client_secret"],
        "GOOGLE_REFRESH_TOKEN": credentials.refresh_token,
    }.items():
        set_key(str(target), name, value, quote_mode="always")
    print("Saved Google configuration privately to .env; no tokens were printed.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit(
            "Google authorization failed or timed out; no credential details printed. Restart consent."
        ) from None
