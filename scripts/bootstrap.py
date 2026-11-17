# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Fetch and verify the pinned upstream source; run only inside the project container."""

import hashlib
import io
import pathlib
import time
import urllib.error
import urllib.request
import zipfile

URL = "https://codeload.github.com/NousResearch/hermes-agent/zip/refs/tags/v0.22.7"
SHA256 = "65a4813be23033f843cb6bb9f1f6561ee5a8dde7e014f48a94bd924c9ad763ab"
MAX_ARCHIVE = 150_000_000


def download(opener=None, sleep=None):
    opener = opener or urllib.request.urlopen
    sleep = sleep or time.sleep
    for attempt in range(4):
        try:
            with opener(URL, timeout=60) as response:  # nosec B310
                archive = response.read(MAX_ARCHIVE + 1)
        except (urllib.error.URLError, TimeoutError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (
                429, 500, 502, 503, 504
            ):
                exc.close()
                raise RuntimeError("Upstream archive download was refused") from None
            if attempt == 3:
                if isinstance(exc, urllib.error.HTTPError):
                    exc.close()
                raise RuntimeError("Upstream archive unavailable after four attempts") from None
            delay = 2 ** (attempt + 1)
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After", "") if exc.headers else ""
                if retry_after.isdigit():
                    delay = max(delay, min(int(retry_after), 60))
                exc.close()
            print(f"Temporary upstream download failure; retrying in {delay}s", flush=True)
            sleep(delay)
            continue
        # A retry never weakens integrity checks or switches to an unpinned archive.
        if len(archive) > MAX_ARCHIVE or hashlib.sha256(archive).hexdigest() != SHA256:
            raise RuntimeError("Upstream archive integrity check failed")
        return archive
    raise AssertionError("Unreachable download state")


def main():
    root = pathlib.Path(".cache/vendor").resolve()
    archive = download()
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        if sum(x.file_size for x in source.infolist()) > 600_000_000:
            raise RuntimeError("Archive expansion exceeds bounds")
        for member in source.infolist():
            if not (root / member.filename).resolve().is_relative_to(root):
                raise RuntimeError("Unsafe archive member")
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError("Archive symlinks are not allowed")
        root.mkdir(parents=True, exist_ok=True)
        source.extractall(root)  # validated member paths and size above
    print("Verified Hermes v0.22.7 source")


if __name__ == "__main__":
    main()
