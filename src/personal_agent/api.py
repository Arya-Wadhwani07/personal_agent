# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Separate public edge and loopback policy APIs with bounded ingress/egress."""

import asyncio
import json
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from .audit import emit
from .broker import Broker
from .integrations import Services
from .routing import RouteError, Router
from .settings import Settings
from .state import PolicyError, Store

STATIC = Path(__file__).parent / "static"


class Bounds:
    def __init__(self, app, limit, inflight):
        self.app, self.limit, self.inflight = app, limit, inflight
        self.active = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        if self.active >= self.inflight:
            return await JSONResponse({"error": "Server busy; retry shortly"}, 429)(
                scope, receive, send
            )
        self.active += 1
        try:
            size = 0
            chunks = []
            # Buffer at most the configured bound, including chunked requests; deadline prevents slowloris.
            async with asyncio.timeout(10):
                while True:
                    part = await receive()
                    if part["type"] == "http.disconnect":
                        return
                    size += len(part.get("body", b""))
                    if size > self.limit:
                        return await JSONResponse({"error": "Request too large"}, 413)(
                            scope, receive, send
                        )
                    chunks.append(part.get("body", b""))
                    if not part.get("more_body", False):
                        break
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
                return await receive()

            async def secure_send(message):
                if message["type"] == "http.response.start":
                    message.setdefault("headers", []).extend(
                        [
                            (b"x-content-type-options", b"nosniff"),
                            (b"referrer-policy", b"no-referrer"),
                            (b"cache-control", b"no-store"),
                            (
                                b"content-security-policy",
                                b"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
                            ),
                        ]
                    )
                await send(message)

            await self.app(scope, bounded_receive, secure_send)
        except TimeoutError:
            await JSONResponse({"error": "Request timed out"}, 408)(scope, receive, send)
        finally:
            self.active -= 1


def authorized(request, key):
    value = request.headers.get("authorization", "")
    return secrets.compare_digest(value, "Bearer " + key)


async def body(request):
    try:
        value = await request.json()
    except (ValueError, UnicodeError) as exc:
        raise PolicyError("Invalid JSON") from exc
    if not isinstance(value, dict):
        raise PolicyError("Expected a JSON object")
    return value


def base_app(s, lifespan=None):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.add_middleware(Bounds, limit=s.max_body, inflight=s.max_inflight)

    @app.exception_handler(PolicyError)
    async def policy_error(request, exc):
        return JSONResponse({"error": str(exc)}, status_code=400)

    @app.exception_handler(RouteError)
    async def route_error(request, exc):
        return JSONResponse({"error": exc.code}, status_code=exc.status)

    @app.exception_handler(httpx.HTTPError)
    async def upstream_error(request, exc):
        return JSONResponse({"error": "Service unavailable"}, status_code=503)

    @app.exception_handler(KeyError)
    @app.exception_handler(TypeError)
    async def shape_error(request, exc):
        return JSONResponse({"error": "Invalid input or service response"}, status_code=400)

    return app


def internal_app(s: Settings, *, router=None, broker=None):
    router = router or Router(s)
    if broker is None:
        checkpoint = None
        if s.bucket:
            from google.cloud import storage

            from .durability import GCSCheckpoint

            checkpoint = GCSCheckpoint(storage.Client().bucket(s.bucket))
            checkpoint.restore(s.state_dir)
        broker = Broker(s, Store(s.state_dir, checkpoint=checkpoint), Services(s))

    @asynccontextmanager
    async def lifespan(app):
        yield
        await router.close()
        await broker.services.client.aclose()
        broker.store.close()

    from .notifications import Notifier

    notifier = Notifier(broker)
    broker.store.recover_notifications()
    app = base_app(s, lifespan)

    @app.middleware("http")
    async def auth(request, call_next):
        if request.url.path == "/codex/responses":
            if s.primary_auth != "oauth" or not secrets.compare_digest(
                request.headers.get("x-a3-internal", ""), s.internal_key
            ):
                return JSONResponse({"error": "Unauthorized"}, 401)
        elif not authorized(request, s.internal_key):
            return JSONResponse({"error": "Unauthorized"}, 401)
        return await call_next(request)

    @app.get("/health")
    async def health():
        broker.store.assert_available()
        return {"status": "policy_ready"}

    @app.post("/checkpoint")
    async def checkpoint():
        with broker.store.transaction():
            pass
        emit("heartbeat", component="state", outcome="durable" if s.bucket else "local_only")
        return {"status": "checkpointed", "durable": bool(s.bucket)}

    @app.post("/jobs/alerts")
    async def alerts():
        return await notifier.run()

    @app.get("/content")
    async def content_list():
        return {"items": broker.store.content_items()}

    @app.post("/content/{identifier}/review")
    async def content_review(identifier: str, request: Request):
        payload = await body(request)
        return broker.store.review_content(
            identifier, payload.get("revision"), payload.get("action"), payload.get("body")
        )

    @app.post("/codex/responses")
    async def oauth_inference(request: Request):
        from .oauth_proxy import OAuthRouter, chat_payload, response_from_chat, response_wire
        from .routing import Decision, decide

        payload = await body(request)
        transcript = chat_payload(payload)
        decision = decide(transcript["messages"])
        if broker.store.private_session(request.headers.get("x-a3-session"), decision.private):
            decision = Decision("local", "private_session", "private", True)
        adapter = OAuthRouter(router, payload, request.headers)
        try:
            result = await adapter.complete(transcript, decision)
        except RouteError as exc:
            if not exc.code.startswith("Private request held:"):
                raise
            result = {"model": "policy-held", "choices": [{"message": {"content": exc.code}}]}
        wire, media = response_wire(response_from_chat(result), payload.get("stream", False))
        return Response(wire, media_type=media)

    @app.post("/v1/chat/completions")
    async def inference(request: Request):
        payload = await body(request)
        messages = payload.get("messages")
        if (
            not isinstance(messages, list)
            or not messages
            or any(not isinstance(m, dict) for m in messages)
        ):
            raise PolicyError("Messages are required")
        if payload.get("stream"):
            raise PolicyError("Use non-streaming model calls")
        try:
            return await router.complete(payload)
        except RouteError as exc:
            if exc.code.startswith("Private request held:"):
                # A completed policy hold is not a retryable provider outage.
                return {
                    "id": "policy-held",
                    "object": "chat.completion",
                    "model": "policy-held",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": exc.code},
                            "finish_reason": "stop",
                        }
                    ],
                }
            raise

    @app.post("/tools/{name}")
    async def tool(name: str, request: Request):
        envelope = await body(request)
        result = await broker.call(
            name, envelope.get("arguments", {}), user_task=envelope.get("user_task", "")
        )
        emit("tool", component=name, outcome="success")
        return result

    @app.get("/drafts/{identifier}")
    async def draft(identifier: str):
        return broker.store.pending(identifier)

    @app.post("/human/approve")
    async def approve(request: Request):
        payload = await body(request)
        identifier = payload["id"]
        message = broker.store.claim_send(
            identifier,
            payload["digest"],
            payload["human_id"],
            s.telegram_user_id,
            s.email_allowlist,
        )
        try:
            result = await broker.services.send_approved(message)
            provider_id = result.get("id")
            if not provider_id:
                raise PolicyError("Email send outcome unknown; do not resend")
        except Exception:
            broker.store.finish_send(identifier)
            emit("email", outcome="unknown", component="approval")
            raise PolicyError(
                "Email send outcome unknown; inspect Gmail before taking further action"
            ) from None
        broker.store.finish_send(identifier, provider_id)
        emit("email", outcome="sent", component="approval")
        return {"status": "sent"}

    return app


def edge_app(s: Settings, client=None, policy_client=None):
    client = client or httpx.AsyncClient(
        base_url="http://127.0.0.1:8081", timeout=150, follow_redirects=False, trust_env=False
    )

    policy_client = policy_client or httpx.AsyncClient(
        base_url="http://127.0.0.1:8090", timeout=30, follow_redirects=False, trust_env=False
    )

    @asynccontextmanager
    async def lifespan(app):
        yield
        await client.aclose()
        await policy_client.aclose()

    app = base_app(s, lifespan)

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/app.js")
    async def js():
        return FileResponse(STATIC / "app.js", media_type="text/javascript")

    @app.get("/app.css")
    async def css():
        return FileResponse(STATIC / "app.css", media_type="text/css")

    @app.get("/health")
    async def health():
        try:
            response = await client.get("/health", timeout=3)
            policy = await policy_client.get(
                "/health", timeout=3, headers={"Authorization": "Bearer " + s.internal_key}
            )
            ok = response.status_code == 200 and policy.status_code == 200
        except httpx.HTTPError:
            ok = False
        return JSONResponse({"status": "ready" if ok else "unavailable"}, 200 if ok else 503)

    async def content_proxy(request, path, method):
        if not authorized(request, s.api_key):
            return JSONResponse({"error": "Unauthorized"}, 401)
        payload = await body(request) if method == "POST" else None
        async with asyncio.timeout(30):
            async with policy_client.stream(
                method, path, json=payload, headers={"Authorization": "Bearer " + s.internal_key}
            ) as response:
                if response.status_code != 200:
                    return JSONResponse(
                        {"error": "Draft unavailable or changed; refresh and try again"}, 400
                    )
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > s.max_response:
                        raise RouteError("Content response exceeded size limit", 502)
        return json.loads(raw)

    @app.get("/content")
    async def content(request: Request):
        return await content_proxy(request, "/content", "GET")

    @app.post("/content/{identifier}/review")
    async def content_review(identifier: str, request: Request):
        if len(identifier) != 24 or any(c not in "0123456789abcdef" for c in identifier):
            raise PolicyError("Invalid draft identifier")
        return await content_proxy(request, "/content/" + identifier + "/review", "POST")

    @app.post("/v1/chat/completions")
    async def chat(request: Request):
        if not authorized(request, s.api_key):
            return JSONResponse({"error": "Unauthorized"}, 401)
        payload = await body(request)
        messages = payload.get("messages")
        if not isinstance(messages, list) or not 1 <= len(messages) <= 100:
            raise PolicyError("Expected 1–100 chat messages")
        for message in messages:
            if (
                not isinstance(message, dict)
                or message.get("role") not in ("user", "assistant")
                or not isinstance(message.get("content"), str)
            ):
                raise PolicyError("Only plain user/assistant chat messages are accepted")
        if messages[-1]["role"] != "user" or not messages[-1]["content"].strip():
            raise PolicyError("A nonempty user message is required")
        # Never forward arbitrary model overrides, system prompts, headers, or admin paths.
        forwarded = {"model": "hermes-agent", "stream": False, "messages": messages}
        headers = {"Authorization": "Bearer " + s.api_key}
        async with asyncio.timeout(150):
            async with client.stream(
                "POST", "/v1/chat/completions", json=forwarded, headers=headers
            ) as response:
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > s.max_response:
                        raise RouteError("Agent response exceeded size limit", 502)
                if response.status_code != 200:
                    return JSONResponse(
                        {"error": "Agent unavailable; check private service status"}, 503
                    )
                try:
                    result = json.loads(raw)
                    content = result["choices"][0]["message"]["content"]
                    if not isinstance(content, str) or not content.strip():
                        raise ValueError("empty")
                except ValueError, KeyError, IndexError, TypeError:
                    return JSONResponse({"error": "Agent returned no usable reply"}, 502)
        emit("message", component="browser", outcome="success")
        return {"choices": [{"message": {"role": "assistant", "content": content}}]}

    return app
