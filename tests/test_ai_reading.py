# I developed this file with Codex assistance; see PROCESS_LOG.md.
import asyncio
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from personal_agent import integrations
from personal_agent.integrations import Services
from personal_agent.recommendations import linkedin_post_reference
from personal_agent.state import PolicyError


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/in/someone",
        "https://www.linkedin.com/login",
        "https://linkedin.com.evil.test/posts/ai",
        "http://www.linkedin.com/posts/ai",
        "https://user@www.linkedin.com/posts/ai",
        "https://127.0.0.1/posts/ai",
        "https://www.linkedin.com/posts/a\nInjected",
    ],
)
def test_reading_rejects_non_post_or_unsafe_links(url):
    with pytest.raises(ValueError):
        linkedin_post_reference(url)


async def test_reading_is_one_daily_search_with_durable_cache_and_duplicate_filter(
    settings, store, monkeypatch
):
    now = [datetime(2026, 11, 18, 5, tzinfo=UTC)]

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now[0]

    monkeypatch.setattr(integrations, "datetime", Clock)
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url == "https://api.tavily.com/search"
        payload = json.loads(request.content)
        assert payload["include_domains"] == ["linkedin.com"]
        assert payload["include_raw_content"] is False
        assert payload["search_depth"] == "basic"
        return httpx.Response(
            200,
            json={
                "results": [
                    None,
                    {
                        "url": "https://www.linkedin.com/in/author",
                        "title": "AI profile",
                        "content": "AI",
                    },
                    {
                        "url": "https://www.linkedin.com/posts/author_agents-evaluation-activity-123?tracking=1",
                        "title": "AI agent evaluation",
                        "content": "A synthetic team tests agent reliability.",
                    },
                    {
                        "url": "https://www.linkedin.com/posts/author_agentic-safety-activity-456",
                        "title": "Agentic AI safety",
                        "content": "A synthetic review of approval gates.",
                    },
                ]
            },
        )

    s = replace(settings, tavily_key="synthetic-search", paid_calls=True, search_call_limit=5)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        service = Services(s, client, store=store)
        first, again = await asyncio.gather(service.ai_reading(), service.ai_reading())
        assert first == again and len(calls) == 1
        assert first["local_date"] == "2026-11-17"
        assert "?tracking" not in first["post"]["url"]
        assert "not verified" in first["evidence"]
        assert await Services(s, client, store=store).ai_reading() == first
        now[0] += timedelta(days=1)
        second = await service.ai_reading()
        assert second["post"]["url"] != first["post"]["url"] and len(calls) == 2
        now[0] += timedelta(days=1)
        missing = await service.ai_reading()
        assert missing["status"] == "unavailable" and len(calls) == 3
        assert "post" not in missing


async def test_reading_requires_budget_and_treats_empty_results_honestly(settings, store):
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"results": []}))
    ) as client:
        with pytest.raises(PolicyError):
            await Services(settings, client, store=store).ai_reading()
        s = replace(settings, tavily_key="synthetic-search", paid_calls=True, search_call_limit=5)
        result = await Services(s, client, store=store).ai_reading()
        assert result["status"] == "unavailable"
