# I developed this file with Codex assistance; see PROCESS_LOG.md.
import json
import os
from unittest.mock import AsyncMock

from personal_agent.runtime import initialize

SAMPLE = "**☀️ Monday · Morning briefing**\n\n**Today**\n• 10:00–10:30 — Fictional review\n\n**Free time**\n• 09:00–10:00 and 10:30–17:00\n\n**Weather**\n• Sunny, 18°C; high 21°C / low 12°C\n\n**Inbox**\n• Synthetic teammate — Review due tomorrow."


def test_native_live_and_standalone_telegram_formatting_match():
    from plugins.platforms.telegram.adapter import TelegramAdapter
    from tools.send_message_senders import _telegram_format
    adapter = object.__new__(TelegramAdapter)
    live = adapter.format_message(SAMPLE)
    standalone, mode, _ = _telegram_format(SAMPLE)
    assert mode == "MarkdownV2"
    assert standalone == live
    assert "*Today*" in live and "• 10:00" in live
    assert "**" not in live
    assert "Cronjob Response" not in live


def test_actual_native_cron_delivery_omits_wrapper(settings, monkeypatch):
    import tools.send_message_tool as sender
    from cron import scheduler_delivery
    from gateway.config import GatewayConfig, Platform, PlatformConfig

    monkeypatch.setattr(os, "environ", os.environ.copy())
    home = initialize(settings)
    cfg = json.loads((home / "config.yaml").read_text())
    assert cfg["cron"]["wrap_response"] is False
    monkeypatch.setattr(scheduler_delivery._sched, "load_config", lambda: cfg)
    monkeypatch.setattr("gateway.config.load_gateway_config", lambda: GatewayConfig(
        platforms={Platform.TELEGRAM: PlatformConfig(enabled=True)}))
    send = AsyncMock(return_value={"success": True, "message_id": "123"})
    monkeypatch.setattr(sender, "_send_to_platform", send)
    job = {"id": "synthetic-job", "name": "a3-morning", "deliver": "telegram:1234"}
    assert scheduler_delivery._deliver_result(job, SAMPLE) is None
    assert send.await_count == 1
    assert SAMPLE in send.call_args.args or SAMPLE in send.call_args.kwargs.values()
    assert not any("Cronjob Response" in str(v) for v in send.call_args.args)
