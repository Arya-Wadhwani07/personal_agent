# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Public indexed LinkedIn references only; this module never fetches a post."""

import re
from urllib.parse import urlsplit, urlunsplit


def linkedin_post_reference(value):
    if not isinstance(value, str) or len(value) > 1000 or any(c.isspace() for c in value):
        raise ValueError("Invalid post reference")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ("linkedin.com", "www.linkedin.com")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
    ):
        raise ValueError("Only public LinkedIn post links are accepted")
    if not re.fullmatch(
        r"/(posts/[A-Za-z0-9_.%:/-]+|feed/update/urn:li:activity:[0-9]+/?)", parsed.path
    ):
        raise ValueError("Profiles, searches and login pages are not posts")
    return urlunsplit(("https", "www.linkedin.com", parsed.path.rstrip("/"), "", ""))
