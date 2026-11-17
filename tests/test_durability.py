# I developed this file with Codex assistance; see PROCESS_LOG.md.
import pytest
from google.api_core.exceptions import NotFound, PreconditionFailed

from personal_agent.durability import GCSCheckpoint
from personal_agent.state import PolicyError, Store


class FakeBucket:
    def __init__(self):
        self.data = {}
        self.counter = 0

    def blob(self, name):
        bucket = self

        class Blob:
            generation = 0
            size = 0

            def reload(self, **kwargs):
                if name not in bucket.data:
                    raise NotFound("missing")
                self.generation, content = bucket.data[name]
                self.size = len(content)

            def download_as_bytes(self, if_generation_match=None, **kwargs):
                generation, content = bucket.data[name]
                if if_generation_match is not None and generation != if_generation_match:
                    raise PreconditionFailed("stale")
                return content

            def upload_from_string(self, content, if_generation_match, **kwargs):
                actual = bucket.data.get(name, (0, b""))[0]
                if actual != if_generation_match:
                    raise PreconditionFailed("stale")
                bucket.counter += 1
                self.generation = bucket.counter
                bucket.data[name] = (
                    self.generation,
                    content.encode() if isinstance(content, str) else content,
                )

        return Blob()


def test_durable_ack_restore_and_stale_writer_fails_closed(tmp_path):
    bucket = FakeBucket()
    first = GCSCheckpoint(bucket)
    store = Store(tmp_path / "first", checkpoint=first)
    store.remember("fictional-name", "Alex")
    second = GCSCheckpoint(bucket)
    second.restore(tmp_path / "second")
    replica = Store(tmp_path / "second", checkpoint=second)
    assert replica.recall() == {"fictional-name": "Alex"}
    store.remember("fictional-team", "Bluebird")
    with pytest.raises(PolicyError, match="Durable commit failed"):
        replica.remember("fictional-team", "stale")
    with pytest.raises(PolicyError, match="unavailable"):
        replica.remember("another", "blocked")
    recovered = GCSCheckpoint(bucket)
    recovered.restore(tmp_path / "third")
    third = Store(tmp_path / "third")
    assert third.recall()["fictional-team"] == "Bluebird"
    for item in (store, replica, third):
        item.close()


def test_storage_failure_prevents_email_send_claim_ack(tmp_path):
    class Fails:
        def commit(self, store):
            raise OSError("synthetic unavailable storage")

    store = Store(tmp_path, checkpoint=Fails())
    with pytest.raises(PolicyError, match="Durable commit failed"):
        store.draft(
            {"to": "r@example.test", "subject": "fictional", "body": "test"}, ("r@example.test",)
        )
    assert store.poisoned
    store.close()
