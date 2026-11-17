# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Exercise child-exit and termination behavior with isolated process doubles."""
import asyncio
from types import SimpleNamespace

import pytest

from personal_agent import runtime


@pytest.mark.parametrize("shutdown", ["child_failure", "signal"])
async def test_supervisor_stops_all_children(settings, monkeypatch, shutdown):
    children, handlers = [], []
    class Process:
        def __init__(self, role):
            self.role, self.returncode = role, None
            self.stopped = asyncio.Event()
        async def wait(self):
            if self.role == "seed":
                self.returncode = 0
                return 0
            if self.role == "gateway" and shutdown == "child_failure":
                self.returncode = 1
                return 1
            await self.stopped.wait()
            return self.returncode
        def terminate(self):
            self.returncode = -15
            self.stopped.set()
        def kill(self):
            self.returncode = -9
            self.stopped.set()
    async def spawn(*command):
        role = ("seed" if command[-1].endswith("seed_jobs.py") else
                "gateway" if command[-1].endswith("gateway_launcher") else command[-1])
        process = Process(role)
        children.append(process)
        if role == "edge" and shutdown == "signal":
            asyncio.get_running_loop().call_soon(handlers[0])
        return process
    class Health:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, url, **kwargs):
            assert url == "http://127.0.0.1:8090/health"
            return SimpleNamespace(status_code=200)
    monkeypatch.setattr(runtime.Settings, "from_env", lambda: settings)
    monkeypatch.setattr(runtime, "initialize", lambda s: None)
    monkeypatch.setattr(runtime.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(asyncio.get_running_loop(), "add_signal_handler",
                        lambda sig, handler: handlers.append(handler))
    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: Health())
    assert await runtime.serve() == (1 if shutdown == "child_failure" else 0)
    assert [p.role for p in children] == ["policy", "seed", "gateway", "edge"]
    assert all(p.returncode is not None for p in children)
