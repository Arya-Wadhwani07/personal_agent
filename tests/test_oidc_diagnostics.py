# I developed this file with Codex assistance; see PROCESS_LOG.md.
import base64
import importlib.util
import io
import json
from pathlib import Path

import pytest


@pytest.fixture
def diagnostic():
    spec = importlib.util.spec_from_file_location("oidc_diag", Path(__file__).parents[1] / "scripts/oidc_diagnostics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_only_allowlisted_claims_are_printed(diagnostic, monkeypatch, capsys):
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "https://pipelines.actions.githubusercontent.com/test?api=1")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "private-request-credential")
    claims = {"repository_id": "123", "ref": "refs/heads/main", "unselected_secret": "never-print-this"}
    token = "header." + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=") + ".private-signature"
    class Opener:
        def open(self, request, timeout):
            assert request.get_header("Authorization") == "Bearer private-request-credential"
            assert "audience=projects%2F1043695272988" in request.full_url
            return io.BytesIO(json.dumps({"value": token}).encode())
    def build(handler):
        assert handler().redirect_request(None, None, 302, None, None, "https://attacker.test") is None
        return Opener()
    monkeypatch.setattr(diagnostic.urllib.request, "build_opener", build)
    diagnostic.main()
    output = capsys.readouterr().out
    assert json.loads(output)["repository_id"] == "123"
    for secret in (token, "private-request-credential", "never-print-this", "private-signature"):
        assert secret not in output


@pytest.mark.parametrize("url", ["http://pipelines.actions.githubusercontent.com/test", "https://attacker.test", "file:///secret"])
def test_unexpected_endpoint_is_rejected_before_reading_token(diagnostic, monkeypatch, url):
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", url)
    monkeypatch.delenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", raising=False)
    with pytest.raises(SystemExit, match="Unexpected"):
        diagnostic.main()
