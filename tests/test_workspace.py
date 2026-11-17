# I developed this file with Codex assistance; see PROCESS_LOG.md.
import io
import sqlite3
import zipfile

import pytest

from personal_agent.workspace import capture, restore


def test_native_database_and_schedule_restore_without_credentials(tmp_path):
    home = tmp_path / "home"
    (home / "cron").mkdir(parents=True)
    (home / "memories").mkdir()
    (home / "cron/jobs.json").write_text('{"jobs":[{"name":"fictional-briefing"}]}')
    (home / "memories/MEMORY.md").write_text("My fictional team is Bluebird.")
    (home / ".env").write_text("NOT_FOR_SNAPSHOT=synthetic")
    (home / "auth.json").write_text('{"token":"synthetic-not-for-snapshot"}')
    db = sqlite3.connect(home / "state.db")
    db.execute("CREATE TABLE messages(body TEXT)")
    db.execute("INSERT INTO messages VALUES('fictional message')")
    db.commit()
    archive = capture(home)
    restored = tmp_path / "restored"
    restore(restored, archive)
    assert not (restored / ".env").exists()
    assert not (restored / "auth.json").exists()
    assert "Bluebird" in (restored / "memories/MEMORY.md").read_text()
    check = sqlite3.connect(restored / "state.db")
    assert check.execute("SELECT body FROM messages").fetchone()[0] == "fictional message"
    assert check.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    db.close()
    check.close()


def test_workspace_rejects_traversal(tmp_path):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("../escape.md", "invalid")
    with pytest.raises(ValueError):
        restore(tmp_path / "target", output.getvalue())


def test_workspace_rejects_symlink(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (tmp_path / "outside.md").write_text("fictional")
    (home / "SOUL.md").symlink_to(tmp_path / "outside.md")
    with pytest.raises(ValueError):
        capture(home)
