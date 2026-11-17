# I developed this file with Codex assistance; see PROCESS_LOG.md.
import pytest

from personal_agent.content_review import example, public_reference, review


def test_claim_ledger_and_duplicate_history():
    data = example()
    result = review(data)
    assert result["status"] == "ready_for_human_review"
    assert result["publishing"] is False
    with pytest.raises(ValueError, match="history"):
        review({**data, "previous_topics": ["  A FICTIONAL team tests approval gates  "]})
    with pytest.raises(ValueError, match="listed source"):
        review({**data, "claims": [{"text": "approval gate", "source": 2}]})
    with pytest.raises(ValueError, match="exact text"):
        review({**data, "claims": [{"text": "invented claim", "source": 1}]})


@pytest.mark.parametrize("url", [
    "http://example.org", "file:///private", "https://localhost", "https://127.0.0.1",
    "https://169.254.169.254", "https://user:pass@example.org",
    "https://www.linkedin.com/feed", "https://example.org:8443", "https://[broken",
])
def test_disallowed_sources(url):
    with pytest.raises(ValueError):
        public_reference(url)
