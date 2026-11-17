# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Fetch and verify the pinned upstream source; run only inside the project container."""

import hashlib
import io
import pathlib
import urllib.request
import zipfile

URL = "https://codeload.github.com/NousResearch/hermes-agent/zip/refs/tags/v0.22.7"
SHA256 = "65a4813be23033f843cb6bb9f1f6561ee5a8dde7e014f48a94bd924c9ad763ab"
ROOT = pathlib.Path(".cache/vendor").resolve()
ROOT.mkdir(parents=True, exist_ok=True)
with urllib.request.urlopen(URL, timeout=60) as response:  # nosec B310
    archive = response.read(150_000_001)
if len(archive) > 150_000_000 or hashlib.sha256(archive).hexdigest() != SHA256:
    raise RuntimeError("Upstream archive integrity check failed")
with zipfile.ZipFile(io.BytesIO(archive)) as source:
    if sum(x.file_size for x in source.infolist()) > 600_000_000:
        raise RuntimeError("Archive expansion exceeds bounds")
    for member in source.infolist():
        if not (ROOT / member.filename).resolve().is_relative_to(ROOT):
            raise RuntimeError("Unsafe archive member")
        if (member.external_attr >> 16) & 0o170000 == 0o120000:
            raise RuntimeError("Archive symlinks are not allowed")
    source.extractall(ROOT)  # validated member paths and size above
print("Verified Hermes v0.22.7 source")
