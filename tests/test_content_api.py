# I developed this file with Codex assistance; see PROCESS_LOG.md.
import httpx

from personal_agent.api import edge_app, internal_app
from personal_agent.broker import Broker
from personal_agent.integrations import Services


async def test_human_content_review_requires_auth_and_rejects_stale_revision(settings, store):
    services = Services(settings)
    broker = Broker(settings, store, services)
    draft = await broker.call(
        "a3_content_brief",
        {"topic": "Synthetic idea", "body": "My draft.", "sources": ["https://example.org/source"]},
    )
    internal = internal_app(settings, broker=broker)
    policy = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=internal), base_url="http://policy"
    )
    gateway = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200)), base_url="http://gateway"
    )
    edge = edge_app(settings, client=gateway, policy_client=policy)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=edge), base_url="http://browser"
    ) as client:
        assert (await client.get("/content")).status_code == 401
        headers = {"Authorization": "Bearer " + settings.api_key}
        item = (await client.get("/content", headers=headers)).json()["items"][0]
        payload = {"action": "revise", "revision": item["revision"], "body": "My human revision."}
        path = "/content/" + draft["id"] + "/review"
        assert (await client.post(path, headers=headers, json=payload)).status_code == 200
        assert (await client.post(path, headers=headers, json=payload)).status_code == 400
        assert (await client.post("/human/approve", headers=headers, json={})).status_code == 404
        assert store.content_items()[0]["body"] == "My human revision."
    await policy.aclose()
    await gateway.aclose()
    await services.client.aclose()
