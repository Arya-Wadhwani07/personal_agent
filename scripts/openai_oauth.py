# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Hermes's own browser PKCE login, with a container-to-loopback TCP relay."""

import argparse
import os
import select
import socket
import socketserver
import threading
from pathlib import Path


class CallbackRelay(socketserver.BaseRequestHandler):
    def handle(self):
        # Docker publishes host 127.0.0.1:1455 to container :1456; Hermes binds :1455.
        with socket.create_connection(("127.0.0.1", 1455), timeout=10) as upstream:
            peers = (self.request, upstream)
            while True:
                ready, _, _ = select.select(peers, [], [], 30)
                if not ready:
                    return
                for source in ready:
                    data = source.recv(16384)
                    if not data:
                        return
                    (upstream if source is self.request else self.request).sendall(data)


class RelayServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = False

    def handle_error(self, request, client_address):
        # Callback query/code must never appear in an exception dump.
        print("Browser callback relay failed; retry sign-in.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("local", "cloud"), default="local")
    args = parser.parse_args()
    root = Path("/workspace")
    state = root / ("state" if args.profile == "local" else "secrets/cloud-oauth")
    home = state / "hermes"
    os.umask(0o077)
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.environ.update(
        HOME=str(state), HERMES_HOME=str(home), CODEX_HOME=str(state / "unused-codex")
    )
    from hermes_cli.auth_codex import _save_codex_tokens
    from hermes_cli.auth_codex_browser import _codex_browser_login

    with RelayServer(("0.0.0.0", 1456), CallbackRelay) as relay:  # noqa: S104  # nosec B104
        threading.Thread(target=relay.serve_forever, daemon=True).start()
        try:
            # Call the pinned native browser flow directly: never fall back to USC-blocked device codes.
            credentials = _codex_browser_login(open_browser=False, timeout_seconds=600)
            _save_codex_tokens(credentials["tokens"], credentials.get("last_refresh"))
            print(
                "Hermes browser OAuth saved privately for " + args.profile + ". No tokens printed."
            )
        except Exception:
            raise SystemExit(
                "OpenAI browser authorization did not complete; no token details printed."
            ) from None
        finally:
            relay.shutdown()


if __name__ == "__main__":
    main()
