# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Restore the separate cloud grant, install native persistence, then run Hermes."""

import os
from pathlib import Path

from .audit import emit
from .settings import Settings


def main():
    os.umask(0o077)
    settings = Settings.from_env()
    if settings.bucket and settings.primary_auth == "oauth":
        from google.cloud import storage

        from .auth_checkpoint import CloudAuthCheckpoint

        try:
            if os.environ.get("INVOCATION_ID"):
                raise RuntimeError(
                    "Cloud auth adapter requires the single-process container gateway"
                )
            checkpoint = CloudAuthCheckpoint(
                storage.Client().bucket(settings.bucket), settings.state_dir / "hermes"
            )
            filename = os.environ.get("A3_OAUTH_BOOTSTRAP_FILE")
            checkpoint.restore(Path(filename) if filename else None)
            checkpoint.install()
        except Exception:
            emit("auth_recovery", component="gateway", outcome="blocked")
            raise SystemExit(
                "Cloud authentication recovery failed; fresh sign-in may be required."
            ) from None
    from gateway.run import main as native_main

    native_main()


if __name__ == "__main__":
    main()
