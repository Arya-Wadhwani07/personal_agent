# I developed this file with Codex assistance; see PROCESS_LOG.md.
import time
from dataclasses import replace
from types import SimpleNamespace

import httpx
import pytest

from personal_agent.broker import Broker
from personal_agent.integrations import Services
from personal_agent.notifications import Notifier
from personal_agent.state import PolicyError, Store


def test_delivery_claim_replay_unknown_and_recovery(store):
    store.queue_notifications([("a", "Synthetic alert", time.time() + 300)])
    assert store.claim_notification("a") == "Synthetic alert"
    assert store.claim_notification("a") is None
    store.recover_notifications()
    assert store.pending_notifications() == []
    assert (
        store.db.execute("SELECT status FROM notifications WHERE id='a'").fetchone()[0] == "unknown"
    )
    store.queue_notifications([("a", "Synthetic alert", time.time() + 300)])
    assert store.pending_notifications() == []


@pytest.mark.parametrize(
    "code,body,expected",
    [
        (200, {"ok": True, "result": {"message_id": 12}}, "sent"),
        (429, {"ok": False}, "pending"),
        (401, {"ok": False}, "pending"),
        (500, {}, "unknown"),
        (200, {"ok": True}, "unknown"),
        (200, {"ok": True, "result": ["malformed"]}, "unknown"),
        (200, {"ok": True, "result": {"message_id": False}}, "unknown"),
        (200, {"ok": True, "result": {"message_id": "unexpected"}}, "unknown"),
    ],
)
async def test_only_provider_ack_means_delivered(settings, code, body, expected):
    notifier = Notifier(SimpleNamespace(s=replace(settings, telegram_token="synthetic-token")))

    def response(request):
        assert request.url.host == "api.telegram.org"
        assert b'"chat_id":"1234"' in request.content
        return httpx.Response(code, json=body)

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
        state, identifier = await notifier.deliver(client, "Synthetic alert")
    assert state == expected
    assert bool(identifier) == (state == "sent")


async def test_content_review_revision_conflict_and_restart(settings, tmp_path):
    store = Store(tmp_path)
    services = Services(settings)
    broker = Broker(settings, store, services)
    draft = await broker.call(
        "a3_content_brief",
        {
            "topic": "Synthetic AI",
            "body": "My original draft.",
            "sources": ["https://example.org/source"],
        },
    )
    revision = store.content_items()[0]["revision"]
    store.review_content(draft["id"], revision, "revise", "My revised draft.")
    with pytest.raises(PolicyError, match="changed"):
        store.review_content(draft["id"], revision, "dismiss")
    store.close()
    restored = Store(tmp_path)
    item = restored.content_items()[0]
    assert item["body"] == "My revised draft."
    restored.review_content(draft["id"], item["revision"], "dismiss")
    assert restored.content_items()[0]["status"] == "dismissed"
    restored.close()
    await services.client.aclose()


def test_expired_notifications_are_not_sent(store):
    store.queue_notifications([("expired", "Old alert", time.time() - 1)])
    assert not store.pending_notifications()
    assert store.claim_notification("expired") is None


async def test_oversized_telegram_ack_is_unknown(settings):
    notifier = Notifier(SimpleNamespace(s=replace(settings, telegram_token="synthetic-token")))
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, content=b"x" * 65537))
    ) as client:
        assert await notifier.deliver(client, "Synthetic alert") == ("unknown", None)


@pytest.mark.parametrize("cancel_job", [False, True])
async def test_delivery_deadline_or_cancellation_never_retries_uncertain_send(
    settings, store, monkeypatch, cancel_job
):
    import asyncio

    from personal_agent import notifications as module

    monkeypatch.setattr(module, "DELIVERY_BATCH_SECONDS", 0.02 if not cancel_job else 10)
    store.queue_notifications([
        ("first", "First synthetic alert", time.time() + 300),
        ("second", "Second synthetic alert", time.time() + 300),
    ])
    async def call(name, arguments):
        return {"unavailable_sources": []}
    notifier = Notifier(SimpleNamespace(
        s=replace(settings, telegram_token="synthetic-token"), store=store, call=call
    ))
    started = asyncio.Event()
    async def slow_delivery(client, text):
        started.set()
        await asyncio.Event().wait()
    monkeypatch.setattr(notifier, "deliver", slow_delivery)
    task = asyncio.create_task(notifier.run())
    await asyncio.wait_for(started.wait(), 1)
    if cancel_job:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        result = await asyncio.wait_for(task, 1)
        assert result["status"] == "degraded"
        assert result["sent"] == 0
    assert not notifier.lock.locked()
    statuses = dict(store.db.execute("SELECT id,status FROM notifications").fetchall())
    assert statuses == {"first": "unknown", "second": "pending"}
    assert [item["id"] for item in store.pending_notifications()] == ["second"]


async def test_telegram_alert_escapes_untrusted_html_and_preserves_heading(settings):
    import json
    notifier = Notifier(SimpleNamespace(s=replace(settings, telegram_token="synthetic-token")))
    def response(request):
        payload = json.loads(request.content)
        assert payload["parse_mode"] == "HTML"
        assert payload["text"].startswith("<b>🔔 Monday · Alert</b>\n\n")
        assert "&lt;b&gt;Injected&lt;/b&gt; &amp;" in payload["text"]
        assert payload["text"].count("<b>") == 1
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 22}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
        assert await notifier.deliver(client, "<b>Injected</b> & synthetic") == ("sent", "22")
