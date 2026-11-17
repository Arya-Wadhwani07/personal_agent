# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Print only non-secret identity claims; never print or persist an OIDC token."""
import base64
import json
import os
import urllib.parse
import urllib.request

FIELDS = ("repository", "repository_id", "repository_owner_id", "ref", "sub", "workflow_ref", "environment")


def main():
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname.endswith(".actions.githubusercontent.com"):
        raise SystemExit("Unexpected GitHub token issuer endpoint")
    audience = "projects/1043695272988/locations/global/workloadIdentityPools/a3-github/providers/github"
    url += ("&" if parsed.query else "?") + urllib.parse.urlencode({"audience": audience})
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(request, timeout=20) as response:  # nosec B310
        raw = response.read(1048577)
    if len(raw) > 1048576:
        raise SystemExit("Oversized identity response")
    token = json.loads(raw)["value"]
    payload = token.split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    # This is diagnostic decoding, not JWT verification or an authorization decision.
    print(json.dumps({k: claims.get(k) for k in FIELDS}, indent=2))


if __name__ == "__main__":
    main()
