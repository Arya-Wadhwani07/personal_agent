# I developed this file with Codex assistance; see PROCESS_LOG.md.
from concurrent.futures import ThreadPoolExecutor

import pytest

from personal_agent.state import PolicyError

PAYLOAD = {
    "to": "recipient@example.test",
    "subject": "Synthetic meeting",
    "body": "A fictional test message.",
}


def test_approval_bound_to_owner_payload_and_allowlist(store):
    draft = store.draft(PAYLOAD, ("recipient@example.test",))
    for human, digest, allowed in [
        ("attacker", draft["digest"], ("recipient@example.test",)),
        ("1234", "changed", ("recipient@example.test",)),
        ("1234", draft["digest"], ()),
    ]:
        with pytest.raises(PolicyError):
            store.claim_send(draft["id"], digest, human, "1234", allowed)
    assert (
        store.claim_send(draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",))
        == PAYLOAD
    )
    with pytest.raises(PolicyError):
        store.claim_send(draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",))


def test_expiry_and_header_injection(store):
    draft = store.draft(PAYLOAD, ("recipient@example.test",), ttl=-1)
    with pytest.raises(PolicyError):
        store.claim_send(draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",))
    with pytest.raises(PolicyError):
        store.draft(
            {**PAYLOAD, "subject": "Hello\r\nBcc: stranger@example.test"},
            ("recipient@example.test",),
        )
    with pytest.raises(PolicyError):
        store.draft({**PAYLOAD, "to": "stranger@example.test"}, ("recipient@example.test",))


def test_concurrent_approval_exactly_one_claim(store):
    draft = store.draft(PAYLOAD, ("recipient@example.test",))

    def attempt(_):
        try:
            store.claim_send(
                draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",)
            )
            return True
        except PolicyError:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(attempt, range(16))) == 1


def test_unknown_outcome_cannot_retry_after_restart(store, tmp_path):
    from personal_agent.state import Store

    draft = store.draft(PAYLOAD, ("recipient@example.test",))
    store.claim_send(draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",))
    store.finish_send(draft["id"])
    other = Store(tmp_path)
    try:
        with pytest.raises(PolicyError):
            other.claim_send(
                draft["id"], draft["digest"], "1234", "1234", ("recipient@example.test",)
            )
    finally:
        other.close()


def test_snapshot_and_concurrent_memory(store, tmp_path):
    import sqlite3

    def save(i):
        store.remember("synthetic-" + str(i), "fictional preference " + str(i))

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(save, range(100)))
    target = tmp_path / "snapshot.sqlite3"
    store.snapshot(target)
    db = sqlite3.connect(target)
    assert db.execute("SELECT count(*) FROM memory").fetchone()[0] == 100
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    db.close()
