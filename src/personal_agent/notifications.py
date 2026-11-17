# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Trusted scheduled delivery. No model tool can choose a recipient or invoke this path."""

import asyncio
import json
import time

import httpx

from .audit import emit
from .state import PolicyError

DELIVERY_BATCH_SECONDS = 55


class Notifier:
    def __init__(self, broker):
        self.broker = broker
        self.lock = asyncio.Lock()

    async def run(self):
        if self.lock.locked():
            return {"status": "already_running", "sent": 0}
        async with self.lock:
            s = self.broker.s
            if not s.telegram_token or not s.telegram_user_id.isdigit():
                raise PolicyError("Class-only Telegram notification destination is not configured")
            collection = await self.broker.call("a3_alerts", {})
            sent = 0
            budget_exhausted = False
            deadline = time.monotonic() + DELIVERY_BATCH_SECONDS
            async with httpx.AsyncClient(
                timeout=20, trust_env=False, follow_redirects=False
            ) as client:
                for item in self.broker.store.pending_notifications():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        budget_exhausted = True
                        break
                    text = self.broker.store.claim_notification(item["id"])
                    if text is None:
                        continue
                    try:
                        async with asyncio.timeout(remaining):
                            status, provider_id = await self.deliver(client, text)
                    except TimeoutError:
                        # A cancelled HTTP request may already have reached Telegram.
                        status, provider_id = "unknown", None
                        budget_exhausted = True
                    except asyncio.CancelledError:
                        self.broker.store.finish_notification(item["id"], "unknown", None)
                        raise
                    self.broker.store.finish_notification(item["id"], status, provider_id)
                    emit("delivery", component="telegram_alert", outcome=status)
                    sent += status == "sent"
            outcome = (
                "degraded"
                if collection.get("unavailable_sources") or budget_exhausted
                else "completed"
            )
            emit("job", job="a3-alerts", outcome=outcome, count=sent)
            return {"status": outcome, "sent": sent, "at": time.time()}

    async def deliver(self, client, text):
        s = self.broker.s
        try:
            async with asyncio.timeout(25):
                async with client.stream(
                    "POST",
                    "https://api.telegram.org/bot" + s.telegram_token + "/sendMessage",
                    json={
                        "chat_id": s.telegram_user_id,
                        "text": text[:3500],
                        "disable_web_page_preview": True,
                    },
                ) as response:
                    if response.status_code in (400, 401, 403, 429):
                        return "pending", None
                    if response.status_code != 200:
                        return "unknown", None
                    raw = bytearray()
                    async for chunk in response.aiter_bytes():
                        raw.extend(chunk)
                        if len(raw) > 65536:
                            return "unknown", None
                data = json.loads(raw)
                if not isinstance(data, dict):
                    return "unknown", None
            result = data.get("result")
            identifier = result.get("message_id") if isinstance(result, dict) else None
            if data.get("ok") is True and type(identifier) is int and identifier > 0:
                return "sent", str(identifier)
            return ("pending", None) if data.get("ok") is False else ("unknown", None)
        except httpx.HTTPError, ValueError, TypeError, TimeoutError:
            return "unknown", None
