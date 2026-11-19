# I developed this file with Codex assistance; see PROCESS_LOG.md.
import asyncio
import json
from dataclasses import replace

import httpx
import pytest

from personal_agent.routing import RouteError, Router
from personal_agent.state import Store

PRIVATE = {"messages": [{"role": "user", "content": "Confidential synthetic connection check"}]}


def result():
    return {"model": "gemma4:e2b", "done": True,
            "message": {"role": "assistant", "content": "Monday is here"}}


def make_router(settings, local, cloud_calls):
    def cloud(request):
        cloud_calls.append(True)
        raise AssertionError("Private context reached cloud")
    return Router(settings, store=Store(settings.state_dir),
                  cloud=httpx.AsyncClient(transport=httpx.MockTransport(cloud)),
                  local=httpx.AsyncClient(transport=httpx.MockTransport(local)))


@pytest.mark.parametrize("error", [httpx.ProxyError, httpx.ConnectError, httpx.ConnectTimeout])
async def test_transient_connection_recovery_preserves_private_route(settings, caplog, error):
    attempts, cloud = [], []
    def local(request):
        attempts.append(json.loads(request.content))
        if len(attempts) < 3:
            raise error("SYNTHETIC-SECRET-never-log-this")
        return httpx.Response(200, json=result())
    router = make_router(settings, local, cloud)
    caplog.set_level("INFO", logger="a3.audit")
    try:
        response = await router.complete(PRIVATE)
    finally:
        await router.close()
    assert response["model"] == "gemma4:e2b"
    assert len(attempts) == 3 and not cloud
    assert attempts[0] == attempts[1] == attempts[2]
    assert attempts[0]["options"]["num_ctx"] == 65536
    assert "SYNTHETIC-SECRET" not in caplog.text
    records = [json.loads(r.message) for r in caplog.records if r.name == "a3.audit"]
    retries = [r for r in records if r["event"] == "local_connection_retry"]
    assert [r["count"] for r in retries] == [1, 2]


async def test_persistent_connection_failure_stays_held(settings):
    attempts, cloud = [], []
    def local(request):
        attempts.append(True)
        raise httpx.ProxyError("synthetic offline")
    router = make_router(settings, local, cloud)
    try:
        with pytest.raises(RouteError, match="held"):
            await router.complete(PRIVATE)
    finally:
        await router.close()
    assert len(attempts) == 3 and not cloud


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.WriteTimeout,
                                   httpx.ReadError, httpx.RemoteProtocolError])
async def test_uncertain_inference_is_not_replayed(settings, error):
    attempts, cloud = [], []
    def local(request):
        attempts.append(True)
        raise error("synthetic failure after possible submission")
    router = make_router(settings, local, cloud)
    try:
        with pytest.raises(RouteError, match="held"):
            await router.complete(PRIVATE)
    finally:
        await router.close()
    assert len(attempts) == 1 and not cloud


@pytest.mark.parametrize("status,body", [(503, {}), (200, {"done": False})])
async def test_upstream_response_failure_is_not_replayed(settings, status, body):
    attempts, cloud = [], []
    def local(request):
        attempts.append(True)
        return httpx.Response(status, json=body)
    router = make_router(settings, local, cloud)
    try:
        with pytest.raises(RouteError, match="held"):
            await router.complete(PRIVATE)
    finally:
        await router.close()
    assert len(attempts) == 1 and not cloud


async def test_original_total_deadline_bounds_retry_backoff(settings):
    attempts, cloud = [], []
    def local(request):
        attempts.append(True)
        raise httpx.ProxyError("synthetic connection failure")
    router = make_router(replace(settings, timeout=1), local, cloud)
    try:
        async with asyncio.timeout(2):
            with pytest.raises(RouteError, match="held"):
                await router.complete(PRIVATE)
    finally:
        await router.close()
    assert len(attempts) == 2 and not cloud


async def test_cancellation_propagates_during_backoff(settings):
    attempted, cloud = asyncio.Event(), []
    def local(request):
        attempted.set()
        raise httpx.ProxyError("synthetic connection failure")
    router = make_router(settings, local, cloud)
    task = asyncio.create_task(router.complete(PRIVATE))
    try:
        await attempted.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        await router.close()
    assert not cloud
