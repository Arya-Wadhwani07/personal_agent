# I developed this file with Codex assistance; see PROCESS_LOG.md.
import copy
import json
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
from test_durability import FakeBucket

from personal_agent.auth_checkpoint import (
    OBJECT,
    AuthCheckpointError,
    CloudAuthCheckpoint,
    assert_auth_ready,
)


def native_auth():
    return {
        "version": 1,
        "providers": {
            "openai-codex": {
                "tokens": {
                    "access_token": "synthetic-access-old",
                    "refresh_token": "synthetic-refresh-old",
                }
            }
        },
        "credential_pool": {
            "openai-codex": [
                {
                    "source": "manual:device_code",
                    "access_token": "synthetic-access-old",
                    "refresh_token": "synthetic-refresh-old",
                }
            ]
        },
    }


def checkpoint(tmp_path, bucket=None):
    bucket = bucket or FakeBucket()
    bootstrap = tmp_path / "bootstrap.json"
    bootstrap.write_text(json.dumps(native_auth()))
    store = CloudAuthCheckpoint(bucket, tmp_path / "state/hermes")
    store.restore(bootstrap)
    return store, bucket


def test_bootstrap_private_restore_and_separate_object(tmp_path):
    store, bucket = checkpoint(tmp_path)
    assert store.path.stat().st_mode & 0o777 == 0o600
    assert_auth_ready(tmp_path / "state")
    assert list(bucket.data) == [OBJECT]
    # A stale bootstrap cannot overwrite the committed remote grant.
    store.auth["providers"]["openai-codex"]["tokens"]["access_token"] = "newer-synthetic"
    store.put("ready", store.auth)
    replacement = CloudAuthCheckpoint(bucket, tmp_path / "replacement/hermes")
    replacement.restore(tmp_path / "bootstrap.json")
    assert (
        replacement.auth["providers"]["openai-codex"]["tokens"]["access_token"] == "newer-synthetic"
    )


def test_native_refresh_has_write_ahead_marker_and_survives_before_local_save(tmp_path):
    store, bucket = checkpoint(tmp_path)

    def native(access, refresh, **kwargs):
        assert json.loads(bucket.data[OBJECT][1])["phase"] == "refresh_pending"
        return {
            "access_token": "synthetic-access-new",
            "refresh_token": "synthetic-refresh-new",
            "last_refresh": "2026-11-17T10:00:00Z",
        }

    store.refresh(native, "synthetic-access-old", "synthetic-refresh-old")
    # Simulate an instance replacement before Hermes's subsequent local save.
    replacement = CloudAuthCheckpoint(bucket, tmp_path / "replacement/hermes")
    replacement.restore()
    assert all(
        r["refresh_token"] == "synthetic-refresh-new"
        for r in [
            replacement.auth["providers"]["openai-codex"]["tokens"],
            replacement.auth["credential_pool"]["openai-codex"][0],
        ]
    )


def test_ambiguous_native_refresh_blocks_reuse_and_ignores_old_bootstrap(tmp_path):
    store, bucket = checkpoint(tmp_path)
    calls = []

    def interrupted(*args, **kwargs):
        calls.append(1)
        raise TimeoutError("synthetic refresh may already have rotated")

    with pytest.raises(AuthCheckpointError):
        store.refresh(interrupted, "synthetic-access-old", "synthetic-refresh-old")
    with pytest.raises(AuthCheckpointError):
        store.refresh(interrupted, "synthetic-access-old", "synthetic-refresh-old")
    assert len(calls) == 1
    with pytest.raises(AuthCheckpointError):
        assert_auth_ready(tmp_path / "state")
    with pytest.raises(AuthCheckpointError, match="Interrupted"):
        CloudAuthCheckpoint(bucket, tmp_path / "replacement/hermes").restore(
            tmp_path / "bootstrap.json"
        )


def test_competing_writer_cannot_start_second_native_refresh(tmp_path):
    first, bucket = checkpoint(tmp_path)
    second = CloudAuthCheckpoint(bucket, tmp_path / "second/hermes")
    second.restore()
    first.put("refresh_pending", first.auth)
    calls = []
    with pytest.raises(AuthCheckpointError):
        second.refresh(
            lambda *a, **k: calls.append(1), "synthetic-access-old", "synthetic-refresh-old"
        )
    assert calls == []


def test_stale_save_cannot_roll_back_rotated_grant(tmp_path):
    store, bucket = checkpoint(tmp_path)
    old = copy.deepcopy(store.auth)
    store.refresh(
        lambda *a, **k: {"access_token": "new-access", "refresh_token": "new-refresh"},
        "synthetic-access-old",
        "synthetic-refresh-old",
    )
    with pytest.raises(AuthCheckpointError):
        store.save(old, lambda *a, **k: None)
    assert (
        json.loads(bucket.data[OBJECT][1])["auth"]["providers"]["openai-codex"]["tokens"][
            "refresh_token"
        ]
        == "new-refresh"
    )


def test_native_save_hook_uses_durable_store_without_refreshing(tmp_path, monkeypatch):
    store, bucket = checkpoint(tmp_path)
    from hermes_cli import auth, auth_codex

    monkeypatch.setenv("HERMES_HOME", str(store.home))
    original_save = auth._save_auth_store
    original_refresh = auth.refresh_codex_oauth_pure
    direct_refresh = auth_codex.refresh_codex_oauth_pure
    try:
        store.install()
        data = copy.deepcopy(store.auth)
        data["active_provider"] = "openai-codex"
        result = auth._save_auth_store(data)
        assert Path(result) == store.path
        assert json.loads(bucket.data[OBJECT][1])["auth"]["active_provider"] == "openai-codex"
    finally:
        auth._save_auth_store = original_save
        auth.refresh_codex_oauth_pure = original_refresh
        auth_codex.refresh_codex_oauth_pure = direct_refresh


def test_cross_profile_save_is_rejected(tmp_path):
    store, _ = checkpoint(tmp_path)
    with pytest.raises(AuthCheckpointError):
        store.save(store.auth, lambda *a, **k: None, target_path=tmp_path / "other/auth.json")


@pytest.mark.asyncio
async def test_cloud_proxy_refuses_inference_without_ready_auth(settings, store):
    from personal_agent.api import internal_app
    from personal_agent.broker import Broker
    from personal_agent.integrations import Services

    settings = replace(settings, primary_auth="oauth", bucket="synthetic-bucket")
    broker = Broker(settings, store, Services(settings))
    app = internal_app(settings, broker=broker)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/codex/responses",
            headers={"x-a3-internal": settings.internal_key, "x-a3-session": "synthetic"},
            json={},
        )
    assert response.status_code == 503
    await broker.services.client.aclose()


def test_actual_hermes_refresh_and_save_chain_uses_adapter(tmp_path, monkeypatch):
    store, bucket = checkpoint(tmp_path)
    from hermes_cli import auth, auth_codex

    monkeypatch.setenv("HERMES_HOME", str(store.home))
    calls = []

    def native_transport(access, refresh, **kwargs):
        calls.append(refresh)
        assert json.loads(bucket.data[OBJECT][1])["phase"] == "refresh_pending"
        return {
            "access_token": "transport-new-access",
            "refresh_token": "transport-new-refresh",
            "last_refresh": "2026-11-17T10:00:00Z",
        }

    monkeypatch.setattr(auth, "refresh_codex_oauth_pure", native_transport)
    # Register originals with monkeypatch so install()'s mutations are restored.
    monkeypatch.setattr(auth, "_save_auth_store", auth._save_auth_store)
    monkeypatch.setattr(auth_codex, "refresh_codex_oauth_pure", auth_codex.refresh_codex_oauth_pure)
    store.install()
    old = dict(native_auth()["providers"]["openai-codex"]["tokens"])
    refreshed = auth._refresh_codex_auth_tokens(old, 20)
    assert calls == ["synthetic-refresh-old"]
    assert refreshed["refresh_token"] == "transport-new-refresh"
    persisted = json.loads(store.path.read_text())
    assert (
        persisted["providers"]["openai-codex"]["tokens"]["refresh_token"] == "transport-new-refresh"
    )
    assert json.loads(bucket.data[OBJECT][1])["phase"] == "ready"


def test_failure_after_native_rotation_retains_pending_marker(tmp_path):
    store, bucket = checkpoint(tmp_path)
    original = store.blob.upload_from_string

    def fail_new_ready(content, **kwargs):
        record = json.loads(content)
        if (
            record["phase"] == "ready"
            and record["auth"]["providers"]["openai-codex"]["tokens"]["refresh_token"] == "rotated"
        ):
            raise OSError("synthetic cloud write failure")
        return original(content, **kwargs)

    store.blob.upload_from_string = fail_new_ready
    with pytest.raises(AuthCheckpointError):
        store.refresh(
            lambda *a, **k: {"access_token": "rotated-access", "refresh_token": "rotated"},
            "synthetic-access-old",
            "synthetic-refresh-old",
        )
    assert json.loads(bucket.data[OBJECT][1])["phase"] == "refresh_pending"
    with pytest.raises(AuthCheckpointError, match="Interrupted"):
        CloudAuthCheckpoint(bucket, tmp_path / "replacement/hermes").restore()


def test_container_cron_keeps_native_auth_hooks_in_process(monkeypatch):
    from tools.process_registry import restart_safe_gateway_child_argv

    monkeypatch.delenv("INVOCATION_ID", raising=False)
    dispatch = restart_safe_gateway_child_argv(
        ["python", "-m", "cron.scheduler"],
        unit_suffix="synthetic-test",
        require_restart_safe_scope=False,
    )
    assert dispatch.mode == "in_process"
