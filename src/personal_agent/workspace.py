# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Bounded native Hermes snapshots; each SQLite database uses its online backup API."""

import io
import sqlite3
import tempfile
import time
import zipfile
from pathlib import Path

LIMIT = 64 * 1024 * 1024
DIRECTORIES = {"memories", "memory", "sessions", "cron", "workspace"}
SUFFIXES = {".md", ".json", ".jsonl", ".db", ".sqlite", ".sqlite3"}
ROOT_FILES = {"SOUL.md", "USER.md", "AGENTS.md", "IDENTITY.md"}


def eligible(relative):
    if relative.name.startswith(".") or relative.suffix not in SUFFIXES:
        return False
    if len(relative.parts) == 1:
        return relative.name in ROOT_FILES or relative.suffix in {".db", ".sqlite", ".sqlite3"}
    return relative.parts[0] in DIRECTORIES and not any(
        part in {"logs", "cache", "credentials", "secrets"} or part.startswith(".")
        for part in relative.parts
    )


def capture(home: Path):
    output = io.BytesIO()
    total = 0
    if not home.exists():
        return b""
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        paths = sorted(p for p in home.rglob("*") if p.is_file() and eligible(p.relative_to(home)))
        if len(paths) > 10000:
            raise ValueError("Workspace file count exceeds limit")
        for path in paths:
            if path.is_symlink() or not path.resolve().is_relative_to(home.resolve()):
                raise ValueError("Workspace symlinks are refused")
            if path.stat().st_size > LIMIT:
                raise ValueError("Workspace file exceeds limit")
            if path.suffix in {".db", ".sqlite", ".sqlite3"}:
                with tempfile.TemporaryDirectory(dir=home.parent, prefix="native-backup-") as temp:
                    target = Path(temp) / "database.sqlite3"
                    source = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
                    destination = sqlite3.connect(target)
                    deadline = time.monotonic() + 10

                    def progress(status, remaining, count, deadline=deadline):
                        if time.monotonic() > deadline:
                            raise TimeoutError("Native database checkpoint deadline exceeded")

                    try:
                        source.backup(destination, pages=64, progress=progress, sleep=0.01)
                    finally:
                        destination.close()
                        source.close()
                    content = target.read_bytes()
            else:
                for _ in range(3):
                    before = path.stat()
                    content = path.read_bytes()
                    after = path.stat()
                    if (before.st_ino, before.st_size, before.st_mtime_ns) == (
                        after.st_ino,
                        after.st_size,
                        after.st_mtime_ns,
                    ):
                        break
                else:
                    raise ValueError("Native file changed during checkpoint")
            total += len(content)
            if total > LIMIT:
                raise ValueError("Workspace snapshot exceeds quota")
            archive.writestr(path.relative_to(home).as_posix(), content)
    return output.getvalue()


def restore(home: Path, content: bytes):
    if not content:
        return
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        members = archive.infolist()
        if len(members) > 10000 or sum(m.file_size for m in members) > LIMIT:
            raise ValueError("Workspace archive exceeds limits")
        for member in members:
            relative = Path(member.filename)
            target = (home / relative).resolve()
            if (
                relative.is_absolute()
                or not target.is_relative_to(home.resolve())
                or not eligible(relative)
            ):
                raise ValueError("Unsafe workspace archive member")
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Workspace archive symlink refused")
        for member in members:
            target = home / member.filename
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_bytes(archive.read(member))
            target.chmod(0o600)
