# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Prepare private project config without printing credentials."""

import argparse
import os
import secrets
from pathlib import Path

import httpx
from dotenv import dotenv_values, set_key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "telegram-id"])
    args = parser.parse_args()
    root = Path("/workspace")
    target = root / ".env"
    os.umask(0o077)
    if args.action == "init":
        if not target.exists():
            target.write_text((root / ".env.example").read_text())
        target.chmod(0o600)
        values = dotenv_values(target)
        for name in ("API_SERVER_KEY", "A3_INTERNAL_KEY"):
            if not values.get(name) or values[name].startswith("REPLACE_"):
                set_key(str(target), name, secrets.token_urlsafe(32), quote_mode="always")
        (root / "secrets").mkdir(exist_ok=True, mode=0o700)
        print("Private .env prepared; keys were generated without printing them.")
    else:
        token = dotenv_values(target).get("TELEGRAM_BOT_TOKEN")
        if not token:
            raise SystemExit("Set the class-only Telegram token in .env first")
        with httpx.Client(timeout=20, trust_env=False) as client:
            response = client.get(
                "https://api.telegram.org/bot" + token + "/getUpdates",
                params={"limit": 10, "timeout": 0},
            )
            if response.status_code != 200:
                raise SystemExit("Telegram setup check failed; no credentials printed")
            ids = {
                item.get("message", {}).get("from", {}).get("id")
                for item in response.json().get("result", [])
            }
            print(
                "Pending sender IDs:",
                ", ".join(str(i) for i in ids if i is not None)
                or "none; send /start to the bot first",
            )


if __name__ == "__main__":
    main()
