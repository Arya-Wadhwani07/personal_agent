# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Durable storage around native Hermes OAuth; Hermes alone performs authentication.

A write-ahead refresh marker prevents replay of an old single-use refresh token after
an ambiguous crash. A pending marker requires a fresh, explicit cloud sign-in.
This is a pinned Hermes storage adapter, not a custom OAuth implementation.
"""

import copy
import json
import os
import tempfile
import threading
from pathlib import Path

LIMIT = 1024 * 1024
OBJECT = "assignment3/credentials/hermes-oauth.json"


class AuthCheckpointError(RuntimeError):
    pass


def token_records(auth):
    provider = auth.get("providers", {}).get("openai-codex", {})
    tokens = provider.get("tokens")
    records = [tokens] if isinstance(tokens, dict) else []
    pool = auth.get("credential_pool", {}).get("openai-codex", [])
    if isinstance(pool, list):
        records.extend(item for item in pool if isinstance(item, dict))
    return records


def validate(auth):
    if not isinstance(auth, dict):
        raise AuthCheckpointError("Native cloud authentication is invalid")
    try:
        tokens = auth["providers"]["openai-codex"]["tokens"]
        if not all(
            isinstance(tokens.get(k), str) and tokens[k] for k in ("access_token", "refresh_token")
        ):
            raise ValueError
        if len(json.dumps(auth).encode()) > LIMIT:
            raise ValueError
        token_records(auth)
    except KeyError, TypeError, AttributeError, ValueError:
        raise AuthCheckpointError("Native cloud authentication is invalid") from None


def refresh_tokens(auth):
    return {item["refresh_token"] for item in token_records(auth) if item.get("refresh_token")}


def assert_auth_ready(state_dir):
    home = state_dir / "hermes"
    if (home / "auth-durability.failed").exists() or not (home / "auth-durability.ready").is_file():
        raise AuthCheckpointError("Cloud authentication recovery is required")


class CloudAuthCheckpoint:
    def __init__(self, bucket, home: Path):
        self.blob = bucket.blob(OBJECT)
        self.home = home
        self.path = home / "auth.json"
        self.generation = 0
        self.auth = None
        self.poisoned = False
        self.lock = threading.RLock()

    def fail(self):
        self.poisoned = True
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        marker = self.home / "auth-durability.failed"
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write("Cloud authentication recovery is required.\n")
        (self.home / "auth-durability.ready").unlink(missing_ok=True)

    def put(self, phase, auth):
        if self.poisoned:
            raise AuthCheckpointError("Cloud authentication recovery is required")
        validate(auth)
        payload = json.dumps({"schema": 1, "phase": phase, "auth": auth})
        if len(payload.encode()) > LIMIT:
            raise AuthCheckpointError("Native cloud authentication exceeds its quota")
        try:
            self.blob.upload_from_string(
                payload,
                content_type="application/json",
                if_generation_match=self.generation,
                timeout=20,
            )
            self.generation = int(self.blob.generation)
        except Exception:
            self.fail()
            raise AuthCheckpointError("Cloud authentication checkpoint failed") from None

    def restore(self, bootstrap: Path | None = None):
        from google.api_core.exceptions import NotFound

        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.home.is_symlink() or self.path.is_symlink():
            raise AuthCheckpointError("Unsafe authentication storage path")
        try:
            self.blob.reload(timeout=20)
        except NotFound:
            if bootstrap is None or bootstrap.is_symlink() or not bootstrap.is_file():
                raise AuthCheckpointError("Separate cloud Hermes sign-in is required") from None
            if bootstrap.stat().st_size > LIMIT:
                raise AuthCheckpointError("Native cloud authentication exceeds its quota") from None
            self.auth = json.loads(bootstrap.read_bytes())
            validate(self.auth)
            self.put("ready", self.auth)
        else:
            if not 0 < self.blob.size <= LIMIT:
                raise AuthCheckpointError("Invalid authentication checkpoint size")
            self.generation = int(self.blob.generation)
            content = self.blob.download_as_bytes(if_generation_match=self.generation, timeout=20)
            record = json.loads(content)
            if record.get("schema") != 1 or record.get("phase") != "ready":
                self.fail()
                raise AuthCheckpointError(
                    "Interrupted OAuth refresh requires a fresh cloud sign-in"
                )
            self.auth = record.get("auth")
            validate(self.auth)
        with tempfile.NamedTemporaryFile(
            mode="w", dir=self.home, prefix=".auth-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(self.auth, stream)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            temporary.chmod(0o600)
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)
        (self.home / "auth-durability.failed").unlink(missing_ok=True)
        (self.home / "auth-durability.ready").write_text("Native cloud authentication restored.\n")

    def save(self, auth, native_save, target_path=None):
        with self.lock:
            try:
                if target_path is not None and Path(target_path).resolve() != self.path.resolve():
                    raise AuthCheckpointError("Cross-profile cloud authentication write refused")
                validate(auth)
                # Runtime metadata updates cannot roll back a newer refresh grant.
                if refresh_tokens(auth) != refresh_tokens(self.auth):
                    raise AuthCheckpointError("Stale cloud authentication write refused")
                self.put("ready", auth)
                result = native_save(auth, target_path=target_path)
                self.auth = copy.deepcopy(auth)
                return result
            except Exception:
                self.fail()
                raise AuthCheckpointError("Cloud authentication persistence failed") from None

    def refresh(self, native_refresh, access_token, refresh_token, **kwargs):
        with self.lock:
            try:
                if self.poisoned or refresh_token not in refresh_tokens(self.auth):
                    raise AuthCheckpointError("Stale cloud refresh refused")
                # Reserve this generation before the native framework contacts OpenAI.
                self.put("refresh_pending", self.auth)
                result = native_refresh(access_token, refresh_token, **kwargs)
                if not all(
                    isinstance(result.get(k), str) and result[k]
                    for k in ("access_token", "refresh_token")
                ):
                    raise AuthCheckpointError("Native refresh returned incomplete credentials")
                updated = copy.deepcopy(self.auth)
                for item in token_records(updated):
                    if item.get("refresh_token") == refresh_token:
                        item.update(
                            access_token=result["access_token"],
                            refresh_token=result["refresh_token"],
                        )
                        if result.get("last_refresh"):
                            item["last_refresh"] = result["last_refresh"]
                provider = updated["providers"]["openai-codex"]
                if provider["tokens"].get("refresh_token") == result["refresh_token"]:
                    provider["last_refresh"] = result.get(
                        "last_refresh", provider.get("last_refresh")
                    )
                # Persist the rotated grant before returning it to the native caller.
                self.put("ready", updated)
                self.auth = updated
                return result
            except Exception:
                self.fail()
                raise AuthCheckpointError(
                    "Cloud OAuth refresh could not be durably confirmed"
                ) from None

    def install(self):
        from hermes_cli import auth, auth_codex

        native_save = auth._save_auth_store
        native_refresh = auth.refresh_codex_oauth_pure

        def save(data, target_path=None):
            return self.save(data, native_save, target_path)

        def refresh(access_token, refresh_token, **kwargs):
            return self.refresh(native_refresh, access_token, refresh_token, **kwargs)

        # These are the pinned framework's public/patchable facade and direct helper.
        # Install before importing gateway/credential-pool consumers.
        auth._save_auth_store = save
        auth.refresh_codex_oauth_pure = refresh
        auth_codex.refresh_codex_oauth_pure = refresh
