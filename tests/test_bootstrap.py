# I developed this file with Codex assistance; see PROCESS_LOG.md.
import hashlib
import importlib.util
import io
import urllib.error
from pathlib import Path

import pytest


@pytest.fixture
def bootstrap():
    spec = importlib.util.spec_from_file_location(
        "a3_bootstrap_test", Path(__file__).parents[1] / "scripts/bootstrap.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("status", [429, 503])
async def test_retry_temporary_download_with_same_pin(bootstrap, status):
    payload = b"synthetic archive bytes"
    bootstrap.SHA256 = hashlib.sha256(payload).hexdigest()
    calls, delays = [], []
    def opener(url, timeout):
        calls.append((url, timeout))
        if len(calls) == 1:
            raise urllib.error.HTTPError(url, status, "synthetic", {"Retry-After": "3"}, None)
        return io.BytesIO(payload)
    assert bootstrap.download(opener, delays.append) == payload
    assert calls == [(bootstrap.URL, 60)] * 2
    assert delays == [3]


def test_retry_exhaustion_is_bounded(bootstrap):
    calls, delays = [], []
    def opener(url, timeout):
        calls.append(url)
        raise urllib.error.HTTPError(url, 429, "synthetic", {"Retry-After": "99999"}, None)
    with pytest.raises(RuntimeError, match="four attempts"):
        bootstrap.download(opener, delays.append)
    assert len(calls) == 4
    assert delays == [60, 60, 60]


def test_permanent_refusal_does_not_retry(bootstrap):
    def opener(url, timeout):
        raise urllib.error.HTTPError(url, 403, "PRIVATE PROVIDER DETAILS", {}, None)
    delays = []
    with pytest.raises(RuntimeError, match="download was refused") as result:
        bootstrap.download(opener, delays.append)
    assert "PRIVATE" not in str(result.value)
    assert delays == []


def test_corrupt_archive_does_not_retry_or_extract(bootstrap):
    delays = []
    with pytest.raises(RuntimeError, match="integrity check failed"):
        bootstrap.download(lambda *args, **kwargs: io.BytesIO(b"tampered"), delays.append)
    assert delays == []


def test_transport_error_recovers_with_backoff(bootstrap):
    payload = b"synthetic archive bytes"
    bootstrap.SHA256 = hashlib.sha256(payload).hexdigest()
    attempts, delays = [], []
    def opener(url, timeout):
        attempts.append(url)
        if len(attempts) < 3:
            raise urllib.error.URLError("PRIVATE CONNECTION DETAILS")
        return io.BytesIO(payload)
    assert bootstrap.download(opener, delays.append) == payload
    assert delays == [2, 4]
