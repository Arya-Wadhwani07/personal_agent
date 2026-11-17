# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Verify native Hermes delivery configuration, not only generated text."""

import os

from personal_agent.runtime import initialize


def test_telegram_home_uses_configured_owner(settings, monkeypatch):
    # Keep every environment mutation inside the monkeypatch lifetime.
    for key in (
        "HERMES_HOME",
        "HOME",
        "CODEX_HOME",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "API_SERVER_HOST",
        "API_SERVER_PORT",
        "API_SERVER_MODEL_NAME",
        "HERMES_NO_AUTO_UPDATE",
        "TELEGRAM_HOME_CHANNEL",
    ):
        monkeypatch.setenv(key, os.environ.get(key, ""))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "synthetic-token")
    initialize(settings)
    from gateway.config import Platform, load_gateway_config

    home = load_gateway_config().get_home_channel(Platform.TELEGRAM)
    assert home is not None
    assert home.chat_id == settings.telegram_user_id
