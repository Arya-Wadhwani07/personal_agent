# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Real Hermes process + plugin + policy server; model/network services are synthetic."""

import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest


@pytest.mark.parametrize("auth_mode", ["api_key", "oauth"])
def test_real_gateway_tool_turn(tmp_path, auth_mode):
    calls = []

    class Ollama(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append(data)
            if not any(m.get("role") == "tool" for m in data["messages"]):
                message = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {"function": {"name": "a3_memory", "arguments": {"action": "read"}}}
                    ],
                }
            else:
                message = {"role": "assistant", "content": "Synthetic memory checked successfully."}
            body = json.dumps({"model": "gemma4:e2b", "message": message, "done": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Ollama)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = {
        **os.environ,
        "A3_STATE_DIR": str(tmp_path / "state"),
        "API_SERVER_KEY": "synthetic-public-" + "a" * 32,
        "A3_INTERNAL_KEY": "synthetic-internal-" + "b" * 32,
        "NVIDIA_API_KEY": "",
        "A3_PRIMARY_AUTH": auth_mode,
        "A3_OPENAI_MODEL": "synthetic-oauth-model",
        "HERMES_HOME": str(tmp_path / "state" / "hermes"),
        "OLLAMA_URL": f"http://127.0.0.1:{server.server_port}/api/chat",
        "TELEGRAM_BOT_TOKEN": "",
        "TELEGRAM_ALLOWED_USERS": "",
    }
    if auth_mode == "oauth":
        subprocess.run(
            [
                sys.executable,
                "-c",
                "from hermes_cli.auth_codex import _save_codex_tokens; "
                "_save_codex_tokens({'access_token':'synthetic-oauth-access','refresh_token':'synthetic-oauth-refresh'})",
            ],
            env=env,
            check=True,
            capture_output=True,
        )
    log_path = tmp_path / "gateway.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "personal_agent.runtime"],
            env=env,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
        try:
            with httpx.Client(
                base_url="http://127.0.0.1:8080", timeout=60, trust_env=False
            ) as client:
                deadline = time.monotonic() + 45
                ready = False
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        break
                    try:
                        if client.get("/health").status_code == 200:
                            ready = True
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                assert ready, log_path.read_text()[-10000:]
                response = client.post(
                    "/v1/chat/completions",
                    headers={"Authorization": "Bearer " + env["API_SERVER_KEY"]},
                    json={
                        "messages": [
                            {"role": "user", "content": "Read my fictional saved preferences."}
                        ]
                    },
                )
                assert response.status_code == 200, (response.text, log_path.read_text()[-10000:])
                assert (
                    "Synthetic memory checked"
                    in response.json()["choices"][0]["message"]["content"]
                )
                assert len(calls) >= 2
                tool_results = [
                    m for call in calls for m in call["messages"] if m.get("role") == "tool"
                ]
                assert tool_results and not any(
                    "error" in str(m.get("content", "")).lower() for m in tool_results
                ), tool_results
                tools = {x["function"]["name"] for x in calls[0].get("tools", [])}
                assert "a3_memory" in tools
                assert not tools.intersection(
                    {"terminal", "execute_code", "send_message", "delegate_task"}
                )
        finally:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            server.shutdown()
            server.server_close()
