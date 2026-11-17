# I developed this file with Codex assistance; see PROCESS_LOG.md.
import os

import pytest

from personal_agent.settings import Settings

os.environ.setdefault("HERMES_HOME", "/tmp/a3-hermes-tests")
os.environ.setdefault("HOME", "/tmp/a3-test-home")


@pytest.fixture
def settings(tmp_path):
    return Settings(
        api_key="public-test-key-" + "a" * 32,
        internal_key="internal-test-key-" + "b" * 32,
        state_dir=tmp_path,
        primary_key="synthetic-openai-key",
        primary_model="synthetic-openai-model",
        paid_calls=True,
        search_call_limit=10,
        nvidia_call_limit=10,
        openai_call_limit=10,
        cloud_key="synthetic-cloud-key",
        email_allowlist=("recipient@example.test",),
        telegram_user_id="1234",
    )


@pytest.fixture
def store(tmp_path):
    from personal_agent.state import Store

    instance = Store(tmp_path)
    yield instance
    instance.close()
