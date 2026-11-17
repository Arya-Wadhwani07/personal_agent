# I developed this file with Codex assistance; see PROCESS_LOG.md.
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import httpx
import pytest

from personal_agent.integrations import Services
from personal_agent.routing import Router
from personal_agent.state import PolicyError, Store


def test_quota_is_atomic_and_survives_reopen(tmp_path):
    store = Store(tmp_path)

    def attempt(_):
        try:
            store.reserve_call("tavily", 5)
            return True
        except PolicyError:
            return False

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(attempt, range(16))) == 5
    store.close()
    restored = Store(tmp_path)
    with pytest.raises(PolicyError, match="exhausted"):
        restored.reserve_call("tavily", 5)
    # A different provider has its own explicitly configured quota.
    assert restored.reserve_call("nvidia", 1) == 1
    restored.close()


async def test_search_cannot_bypass_disabled_or_consumed_quota(settings, store):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        s = replace(settings, tavily_key="synthetic", search_call_limit=1)
        service = Services(replace(s, paid_calls=False), client, store=store)
        with pytest.raises(PolicyError):
            await service.search("synthetic")
        assert not calls
        service.s = s
        with pytest.raises(PolicyError):
            await service.search("synthetic")
        with pytest.raises(PolicyError, match="exhausted"):
            await service.search("synthetic")
        assert len(calls) == 1  # A failed/uncertain attempt is never refunded.


async def test_durable_failure_prevents_external_spend(settings, tmp_path):
    class BrokenCheckpoint:
        def commit(self, store):
            raise OSError("synthetic storage outage")

    store = Store(tmp_path, checkpoint=BrokenCheckpoint())

    def forbidden(request):
        pytest.fail("No network request before durable reservation")

    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as client:
        service = Services(replace(settings, tavily_key="synthetic"), client, store=store)
        with pytest.raises(PolicyError, match="Durable commit failed"):
            await service.search("synthetic")
    store.close()


async def test_exhausted_cloud_quotas_can_fall_back_to_local(settings, store):
    calls = []

    def respond(request):
        calls.append(request.url.host)
        assert request.url.host == "host.docker.internal"
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": "gemma4:e2b",
                "message": {"role": "assistant", "content": "Synthetic reply"},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        router = Router(
            replace(settings, openai_call_limit=0, nvidia_call_limit=0),
            cloud=client,
            local=client,
            store=store,
        )
        result = await router.complete(
            {"messages": [{"role": "user", "content": "Compare fictional plans"}]}
        )
        assert result["model"] == "gemma4:e2b" and len(calls) == 1


@pytest.mark.parametrize("limit", [-1, 1001, True, 1.5])
def test_invalid_quota_configuration_fails_closed(settings, limit):
    with pytest.raises(ValueError):
        replace(settings, search_call_limit=limit)
