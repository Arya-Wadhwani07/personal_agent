# I developed this file with Codex assistance; see PROCESS_LOG.md.
import asyncio
import json

import httpx

from personal_agent.api import edge_app, internal_app
from personal_agent.broker import Broker
from personal_agent.integrations import Services


def response(content="Hello"):
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


async def test_public_interface_security_and_html(settings):
    seen = []

    def upstream(request):
        seen.append(request)
        return httpx.Response(200, json=response("<script>alert(1)</script>"))

    app = edge_app(
        settings,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(upstream)),
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://edge"
    ) as c:
        payload = {"messages": [{"role": "user", "content": "hello"}]}
        assert (await c.post("/v1/chat/completions", json=payload)).status_code == 401
        headers = {"Authorization": "Bearer " + settings.api_key}
        assert (await c.post("/human/approve", headers=headers, json={})).status_code == 404
        assert (
            await c.post(
                "/v1/chat/completions",
                headers=headers,
                json={"messages": [{"role": "system", "content": "bypass"}]},
            )
        ).status_code == 400
        result = await c.post(
            "/v1/chat/completions",
            headers=headers,
            json={**payload, "base_url": "https://attacker.test", "tools": [{}]},
        )
        assert result.status_code == 200
        assert json.loads(seen[-1].content) == {"model": "hermes-agent", "stream": False, **payload}
        assert "frame-ancestors 'none'" in result.headers["content-security-policy"]
        js = (await c.get("/app.js")).text
        assert "textContent" in js and "innerHTML" not in js
        assert "localStorage" not in js and "sessionStorage" not in js


async def test_chunked_oversize_and_empty_response(settings):
    app = edge_app(
        settings,
        httpx.AsyncClient(
            base_url="http://hermes",
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=response(""))),
        ),
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://edge"
    ) as c:

        async def chunks():
            yield b"a" * 100000
            yield b"b" * 100000

        assert (await c.post("/v1/chat/completions", content=chunks())).status_code == 413
        result = await c.post(
            "/v1/chat/completions",
            headers={"Authorization": "Bearer " + settings.api_key},
            json={"messages": [{"role": "user", "content": "hello"}]},
        )
        assert result.status_code == 502


async def test_approval_only_internal_and_no_retry(settings, store):
    calls = []

    async def send(payload):
        calls.append(payload)
        return {"id": "synthetic-provider-id"}

    services = Services(
        settings,
        httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={}))),
    )
    services.send_approved = send
    broker = Broker(settings, store, services)
    app = internal_app(settings, broker=broker)
    draft = store.draft(
        {"to": "recipient@example.test", "subject": "test", "body": "fictional"},
        settings.email_allowlist,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://policy"
    ) as c:
        payload = {"id": draft["id"], "digest": draft["digest"], "human_id": "1234"}
        assert (
            await c.post(
                "/human/approve",
                headers={"Authorization": "Bearer " + settings.api_key},
                json=payload,
            )
        ).status_code == 401
        headers = {"Authorization": "Bearer " + settings.internal_key}
        assert (await c.post("/tools/send_email", headers=headers, json={})).status_code == 400
        assert (
            await c.post(
                "/human/approve", headers=headers, json={**payload, "human_id": "attacker"}
            )
        ).status_code == 400
        assert not calls
        assert (await c.post("/human/approve", headers=headers, json=payload)).status_code == 200
        assert (await c.post("/human/approve", headers=headers, json=payload)).status_code == 400
        assert len(calls) == 1


async def test_overload_is_bounded_and_recovers(settings):
    release = asyncio.Event()

    async def upstream(request):
        await release.wait()
        return httpx.Response(200, json=response())

    app = edge_app(
        settings,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(upstream)),
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://edge"
    ) as c:

        async def request():
            return await c.post(
                "/v1/chat/completions",
                headers={"Authorization": "Bearer " + settings.api_key},
                json={"messages": [{"role": "user", "content": "hello"}]},
            )

        tasks = [asyncio.create_task(request()) for _ in range(4)]
        for _ in range(20):
            await asyncio.sleep(0)
        excess = await request()
        assert excess.status_code == 429
        release.set()
        assert all(r.status_code == 200 for r in await asyncio.gather(*tasks))
        assert (await request()).status_code == 200


async def test_upstream_failure_does_not_disclose_response_body(settings):
    app = edge_app(settings, httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(
            lambda r: httpx.Response(500, text="synthetic-private-provider-secret")
        )))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://edge") as client:
        response = await client.post("/v1/chat/completions",
            headers={"Authorization": "Bearer " + settings.api_key},
            json={"messages": [{"role": "user", "content": "synthetic"}]})
        assert response.status_code == 503
        assert "private-provider-secret" not in response.text


async def test_oversized_upstream_response_is_refused(settings):
    app = edge_app(settings, httpx.AsyncClient(
        base_url="http://hermes", transport=httpx.MockTransport(
            lambda r: httpx.Response(200, content=b"x" * (settings.max_response + 1))
        )))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://edge") as client:
        response = await client.post("/v1/chat/completions",
            headers={"Authorization": "Bearer " + settings.api_key},
            json={"messages": [{"role": "user", "content": "synthetic"}]})
        assert response.status_code == 502


async def test_slow_request_body_times_out_and_releases_slot(monkeypatch):
    from personal_agent.api import Bounds
    original_timeout = asyncio.timeout
    monkeypatch.setattr(asyncio, "timeout", lambda seconds: original_timeout(0.01))
    reached = []
    async def application(scope, receive, send):
        reached.append(True)
    async def receive():
        await asyncio.sleep(0.1)
        return {"type": "http.request", "body": b"synthetic", "more_body": True}
    messages = []
    async def send(message):
        messages.append(message)
    middleware = Bounds(application, 1024, 1)
    await middleware({"type": "http"}, receive, send)
    assert not reached and middleware.active == 0
    assert messages[0]["status"] == 408
