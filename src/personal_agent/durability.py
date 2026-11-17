# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Generation-fenced, immutable SQLite snapshots in a dedicated GCS bucket.

A writer keeps its last manifest generation. A competing writer cannot overwrite an
acknowledged snapshot: its conditional manifest update fails and that writer stops.
Native databases are backed up individually; the bundle is not a cross-database transaction.
"""

import hashlib
import json
import sqlite3
import tempfile
import uuid
from pathlib import Path


class DurabilityError(Exception):
    pass


class GCSCheckpoint:
    def __init__(self, bucket, *, prefix="assignment3/"):
        self.bucket, self.prefix = bucket, prefix
        self.manifest = bucket.blob(prefix + "manifest.json")
        self.generation = 0

    def restore(self, directory: Path):
        from google.api_core.exceptions import NotFound

        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            self.manifest.reload(timeout=20)
        except NotFound:
            return
        self.generation = int(self.manifest.generation)
        raw = self.manifest.download_as_bytes(if_generation_match=self.generation, timeout=20)
        data = json.loads(raw)
        name = data["object"]
        if not name.startswith(self.prefix + "snapshots/") or data["bytes"] > 32 * 1024 * 1024:
            raise DurabilityError("Invalid state manifest")
        blob = self.bucket.blob(name)
        blob.reload(timeout=20)
        if blob.size != data["bytes"]:
            raise DurabilityError("State size mismatch")
        content = blob.download_as_bytes(timeout=20)
        if hashlib.sha256(content).hexdigest() != data["sha256"]:
            raise DurabilityError("State checksum mismatch")
        # Validate the whole bundle in a disposable directory before replacing live files.
        # Only the startup policy process calls restore; no gateway/database writer exists yet.
        with tempfile.TemporaryDirectory(dir=directory, prefix="restore-") as temporary:
            staged = Path(temporary)
            target = staged / "assistant.sqlite3"
            target.write_bytes(content)
            target.chmod(0o600)
            connection = sqlite3.connect(target)
            try:
                if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise DurabilityError("Restored database failed integrity check")
            finally:
                connection.close()
            if data.get("workspace"):
                from .workspace import restore

                record = data["workspace"]
                native = self.download_record(record, 64 * 1024 * 1024)
                restore(staged / "hermes", native)
            if data.get("network"):
                network = self.download_record(data["network"], 1024 * 1024)
                json.loads(network)  # Tailscale uses a JSON state store; reject corrupt state.
                (staged / "tailscaled.state").write_bytes(network)
            # Remove stale native snapshot-eligible files absent from the committed bundle.
            from .workspace import eligible

            native_home = directory / "hermes"
            if native_home.exists():
                for old in native_home.rglob("*"):
                    if old.is_file() and eligible(old.relative_to(native_home)):
                        if old.is_symlink() or not old.resolve().is_relative_to(
                            native_home.resolve()
                        ):
                            raise DurabilityError("Unsafe existing workspace path")
                        if not (staged / "hermes" / old.relative_to(native_home)).exists():
                            old.unlink()
            for source in sorted(staged.rglob("*")):
                if not source.is_file():
                    continue
                destination = directory / source.relative_to(staged)
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                if destination.is_symlink() or not destination.resolve().is_relative_to(
                    directory.resolve()
                ):
                    raise DurabilityError("Unsafe restore destination")
                source.chmod(0o600)
                source.replace(destination)

    def download_record(self, record, limit):
        if (
            not record["object"].startswith(self.prefix + "snapshots/")
            or not 0 <= record["bytes"] <= limit
        ):
            raise DurabilityError("Invalid snapshot manifest")
        blob = self.bucket.blob(record["object"])
        blob.reload(timeout=20)
        if blob.size != record["bytes"]:
            raise DurabilityError("Snapshot size mismatch")
        content = blob.download_as_bytes(timeout=30)
        if hashlib.sha256(content).hexdigest() != record["sha256"]:
            raise DurabilityError("Snapshot checksum mismatch")
        return content

    def commit(self, store):
        from google.api_core.exceptions import PreconditionFailed

        with tempfile.TemporaryDirectory(dir=store.path.parent, prefix="checkpoint-") as temporary:
            path = Path(temporary) / "state.sqlite3"
            store.snapshot(path)
            content = path.read_bytes()
        if len(content) > 32 * 1024 * 1024:
            raise DurabilityError("State quota exceeded")
        name = self.prefix + "snapshots/" + uuid.uuid4().hex + ".sqlite3"
        self.bucket.blob(name).upload_from_string(
            content, content_type="application/vnd.sqlite3", if_generation_match=0, timeout=30
        )
        from .workspace import capture

        native = capture(store.path.parent / "hermes")
        workspace = None
        if native:
            native_name = self.prefix + "snapshots/" + uuid.uuid4().hex + ".zip"
            self.bucket.blob(native_name).upload_from_string(
                native, content_type="application/zip", if_generation_match=0, timeout=30
            )
            workspace = {
                "object": native_name,
                "sha256": hashlib.sha256(native).hexdigest(),
                "bytes": len(native),
            }
        network = None
        state = store.path.parent / "tailscaled.state"
        if state.exists():
            if state.is_symlink() or state.stat().st_size > 1024 * 1024:
                raise DurabilityError("Invalid private network state")
            network_content = state.read_bytes()
            json.loads(network_content)
            network_name = self.prefix + "snapshots/" + uuid.uuid4().hex + ".network.json"
            self.bucket.blob(network_name).upload_from_string(
                network_content, content_type="application/json", if_generation_match=0, timeout=30
            )
            network = {
                "object": network_name,
                "sha256": hashlib.sha256(network_content).hexdigest(),
                "bytes": len(network_content),
            }
        payload = json.dumps(
            {
                "object": name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "schema": 3,
                "network": network,
                "workspace": workspace,
            }
        )
        try:
            self.manifest.upload_from_string(
                payload,
                content_type="application/json",
                if_generation_match=self.generation,
                timeout=30,
            )
        except PreconditionFailed as exc:
            raise DurabilityError(
                "Concurrent writer detected; stop and restore the committed state"
            ) from exc
        self.generation = int(self.manifest.generation)
