# I developed this file with Codex assistance; see PROCESS_LOG.md.
import json

import pytest
from test_durability import FakeBucket

from personal_agent.durability import DurabilityError, GCSCheckpoint
from personal_agent.state import Store


def test_bundle_replaces_stale_state_and_restores_private_identity(tmp_path):
    bucket = FakeBucket()
    source = tmp_path / "source"
    source.mkdir()
    (source / "tailscaled.state").write_text('{"synthetic_identity":"class-only"}')
    (source / "hermes").mkdir()
    (source / "hermes/SOUL.md").write_text("My saved fictional profile.")
    checkpoint = GCSCheckpoint(bucket)
    store = Store(source, checkpoint)
    store.remember("fictional-team", "Bluebird")
    store.close()
    target = tmp_path / "target"
    stale = Store(target)
    stale.remember("fictional-team", "stale")
    stale.close()
    GCSCheckpoint(bucket).restore(target)
    restored = Store(target)
    assert restored.recall() == {"fictional-team": "Bluebird"}
    assert (
        json.loads((target / "tailscaled.state").read_text())["synthetic_identity"] == "class-only"
    )
    assert (target / "hermes/SOUL.md").read_text() == "My saved fictional profile."
    restored.close()


def test_corrupt_bundle_does_not_replace_existing_database(tmp_path):
    bucket = FakeBucket()
    store = Store(tmp_path / "source", GCSCheckpoint(bucket))
    store.remember("fictional", "valid")
    store.close()
    manifest = json.loads(bucket.data["assignment3/manifest.json"][1])
    record = manifest["object"]
    gen, data = bucket.data[record]
    bucket.data[record] = gen, data[:-1] + b"x"
    target = tmp_path / "target"
    old = Store(target)
    old.remember("old", "preserved")
    old.close()
    with pytest.raises(DurabilityError):
        GCSCheckpoint(bucket).restore(target)
    preserved = Store(target)
    assert preserved.recall() == {"old": "preserved"}
    preserved.close()


def test_bootstrap_snapshot_gets_missing_profile_after_restore(settings, monkeypatch):
    import os

    from personal_agent.runtime import initialize

    monkeypatch.setattr(os, "environ", os.environ.copy())
    bucket = FakeBucket()
    source = settings.state_dir.parent / "preflight"
    store = Store(source, GCSCheckpoint(bucket))
    store.reserve_call("tavily", 50)
    store.close()
    home = initialize(settings)
    GCSCheckpoint(bucket).restore(settings.state_dir)
    assert not (home / "SOUL.md").exists()
    initialize(settings)
    assert "fictional class-only profile" in (home / "SOUL.md").read_text()
    assert "Alex Chen" in (home / "memories/USER.md").read_text()
    (home / "SOUL.md").write_text("My saved fictional preference.")
    initialize(settings)
    assert (home / "SOUL.md").read_text() == "My saved fictional preference."
