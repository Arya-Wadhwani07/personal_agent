# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Single-process transactional state, exact-payload approvals, and durable snapshots."""

import hashlib
import json
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path


class PolicyError(Exception):
    pass


class Store:
    def __init__(self, directory: Path, checkpoint=None):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = directory / "assistant.sqlite3"
        self.checkpoint = checkpoint
        self.poisoned = False
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS private_sessions (id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS drafts (id TEXT PRIMARY KEY, payload TEXT NOT NULL, digest TEXT NOT NULL,
          expires REAL NOT NULL, status TEXT NOT NULL, approved_by TEXT, provider_id TEXT);
        CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, item TEXT NOT NULL, at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS content (id TEXT PRIMARY KEY, topic TEXT NOT NULL, body TEXT NOT NULL,
          sources TEXT NOT NULL, status TEXT NOT NULL, at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS notifications (id TEXT PRIMARY KEY, body TEXT NOT NULL, expires REAL NOT NULL, status TEXT NOT NULL, provider_id TEXT, updated REAL NOT NULL);
        """)
        self.path.chmod(0o600)

    @contextmanager
    def transaction(self):
        with self.lock:
            if self.poisoned:
                raise PolicyError(
                    "Durable state is unavailable; stop and restore before further changes"
                )
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield self.db
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
            if self.checkpoint:
                try:
                    self.checkpoint.commit(self)
                except Exception as exc:
                    self.poisoned = True
                    raise PolicyError("Durable commit failed; no action is acknowledged") from exc

    def private_session(self, identifier, mark=False):
        if not isinstance(identifier, str) or not identifier or len(identifier) > 200:
            raise PolicyError("Trusted session identity is required")
        self.assert_available()
        with self.lock:
            existing = self.db.execute(
                "SELECT 1 FROM private_sessions WHERE id=?", (identifier,)
            ).fetchone()
        if mark and not existing:
            with self.transaction() as db:
                db.execute("INSERT OR IGNORE INTO private_sessions VALUES (?)", (identifier,))
        return bool(existing or mark)

    def remember(self, key, value):
        if not key or len(key) > 80 or len(value) > 2000:
            raise PolicyError("Memory size exceeds policy")
        with self.transaction() as db:
            db.execute(
                "INSERT INTO memory VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated=excluded.updated",
                (key, value, time.time()),
            )

    def recall(self):
        self.assert_available()
        with self.lock:
            return dict(self.db.execute("SELECT key,value FROM memory ORDER BY key"))

    def draft(self, payload, allowlist, ttl=900):
        recipient = payload["to"].strip().lower()
        if recipient not in allowlist or any(c in recipient for c in "\r\n,;"):
            raise PolicyError("Recipient is not on the class-only allowlist")
        subject, body = payload["subject"], payload["body"]
        if any(c in subject for c in "\r\n") or len(subject) > 200 or len(body) > 12000:
            raise PolicyError("Invalid email bounds")
        payload = {"to": recipient, "subject": subject, "body": body}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        identifier = secrets.token_urlsafe(18)
        with self.transaction() as db:
            db.execute(
                "INSERT INTO drafts VALUES (?,?,?,?,?,?,?)",
                (identifier, canonical, digest, time.time() + ttl, "pending", None, None),
            )
        return {"id": identifier, "payload": payload, "digest": digest, "status": "pending"}

    def pending(self, identifier):
        self.assert_available()
        with self.lock:
            row = self.db.execute(
                "SELECT payload,digest,expires,status FROM drafts WHERE id=?", (identifier,)
            ).fetchone()
        if not row or row[2] < time.time() or row[3] != "pending":
            raise PolicyError("Draft is unavailable, expired, or already consumed")
        return {"id": identifier, "payload": json.loads(row[0]), "digest": row[1]}

    def claim_send(self, identifier, digest, human_id, allowed_human, allowlist):
        if not allowed_human or human_id != allowed_human:
            raise PolicyError("Explicit approval from the configured Telegram owner is required")
        with self.transaction() as db:
            row = db.execute(
                "SELECT payload,digest,expires,status FROM drafts WHERE id=?", (identifier,)
            ).fetchone()
            if (
                not row
                or row[2] < time.time()
                or row[3] != "pending"
                or not secrets.compare_digest(row[1], digest)
            ):
                raise PolicyError("Approval is stale, changed, or already consumed")
            payload = json.loads(row[0])
            if payload["to"] not in allowlist:
                raise PolicyError("Recipient no longer allowed")
            # Commit intent before any network I/O; an uncertain send can never be blindly retried.
            db.execute(
                "UPDATE drafts SET status='sending',approved_by=? WHERE id=?",
                (human_id, identifier),
            )
            return payload

    def finish_send(self, identifier, provider_id=None):
        with self.transaction() as db:
            db.execute(
                "UPDATE drafts SET status=?,provider_id=? WHERE id=? AND status='sending'",
                ("sent" if provider_id else "unknown", provider_id, identifier),
            )
            db.execute(
                "INSERT INTO activity(kind,item,at) VALUES(?,?,?)",
                ("email_sent" if provider_id else "email_unknown", identifier, time.time()),
            )

    def activity(self, since):
        with self.lock:
            return [
                {"kind": r[0], "item": r[1], "at": r[2]}
                for r in self.db.execute(
                    "SELECT kind,item,at FROM activity WHERE at>=? ORDER BY at", (since,)
                )
            ]

    def assert_available(self):
        if self.poisoned:
            raise PolicyError("Durable state is unavailable; restore before continuing")

    def queue_notifications(self, candidates):
        now = time.time()
        with self.transaction() as db:
            for identifier, body, expires in candidates:
                db.execute(
                    "INSERT OR IGNORE INTO notifications VALUES(?,?,?,'pending',NULL,?)",
                    (identifier, body, expires, now),
                )
            db.execute(
                "UPDATE notifications SET status='expired',updated=? WHERE expires<? AND status='pending'",
                (now, now),
            )

    def pending_notifications(self):
        self.assert_available()
        with self.lock:
            return [
                {"id": r[0], "body": r[1]}
                for r in self.db.execute(
                    "SELECT id,body FROM notifications WHERE status='pending' AND expires>? ORDER BY updated LIMIT 10",
                    (time.time(),),
                )
            ]

    def claim_notification(self, identifier):
        with self.transaction() as db:
            row = db.execute(
                "SELECT body,status,expires FROM notifications WHERE id=?", (identifier,)
            ).fetchone()
            if not row or row[1] != "pending" or row[2] <= time.time():
                return None
            db.execute(
                "UPDATE notifications SET status='sending',updated=? WHERE id=?",
                (time.time(), identifier),
            )
            return row[0]

    def finish_notification(self, identifier, status, provider_id=None):
        if status not in {"sent", "unknown", "pending"}:
            raise PolicyError("Invalid delivery state")
        with self.transaction() as db:
            changed = db.execute(
                "UPDATE notifications SET status=?,provider_id=?,updated=? WHERE id=? AND status='sending'",
                (status, provider_id, time.time(), identifier),
            ).rowcount
            if changed:
                db.execute(
                    "INSERT INTO activity(kind,item,at) VALUES(?,?,?)",
                    ("notification_" + status, identifier, time.time()),
                )

    def recover_notifications(self):
        with self.transaction() as db:
            db.execute(
                "UPDATE notifications SET status='unknown',updated=? WHERE status='sending'",
                (time.time(),),
            )

    def content_items(self):
        self.assert_available()
        with self.lock:
            rows = self.db.execute(
                "SELECT id,topic,body,sources,status FROM content ORDER BY at DESC LIMIT 20"
            ).fetchall()
        return [
            {
                "id": r[0],
                "topic": r[1],
                "body": r[2],
                "sources": json.loads(r[3]),
                "status": r[4],
                "revision": hashlib.sha256((r[2] + r[4]).encode()).hexdigest(),
            }
            for r in rows
        ]

    def review_content(self, identifier, revision, action, body=None):
        if action not in {"revise", "dismiss", "copied"}:
            raise PolicyError("Unknown review action")
        with self.transaction() as db:
            row = db.execute("SELECT body,status FROM content WHERE id=?", (identifier,)).fetchone()
            if not row or not secrets.compare_digest(
                hashlib.sha256((row[0] + row[1]).encode()).hexdigest(), str(revision)
            ):
                raise PolicyError("Draft changed; refresh before reviewing")
            if action == "revise":
                if not isinstance(body, str) or not 1 <= len(body.strip()) <= 3000:
                    raise PolicyError("Draft must contain 1–3000 characters")
                db.execute(
                    "UPDATE content SET body=?,status='review' WHERE id=?",
                    (body.strip(), identifier),
                )
            elif action == "dismiss":
                db.execute("UPDATE content SET status='dismissed' WHERE id=?", (identifier,))
            db.execute(
                "INSERT INTO activity(kind,item,at) VALUES(?,?,?)",
                ("content_" + action, identifier, time.time()),
            )
        return {
            "status": "review"
            if action == "revise"
            else "dismissed"
            if action == "dismiss"
            else "copied"
        }

    def snapshot(self, destination: Path):
        with self.lock:
            target = sqlite3.connect(destination)
            try:
                self.db.backup(target)
            finally:
                target.close()

    def close(self):
        self.db.close()
