# I developed this file with Codex assistance; see PROCESS_LOG.md.
from dataclasses import replace

import httpx

from personal_agent.api import internal_app
from personal_agent.broker import Broker
from personal_agent.integrations import Services


async def test_cloud_readiness_does_not_confuse_restore_health_with_auth(settings, store):
    s = replace(settings, primary_auth="oauth", bucket="synthetic-bucket")
    services = Services(s)
    app = internal_app(s, broker=Broker(s, store, services))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test",
                                 headers={"Authorization": "Bearer " + s.internal_key}) as client:
        assert (await client.get("/health")).status_code == 200
        assert (await client.get("/ready")).status_code == 503
        home = s.state_dir / "hermes"
        home.mkdir()
        (home / "auth-durability.ready").write_text("synthetic ready")
        assert (await client.get("/ready")).status_code == 200
        (home / "auth-durability.failed").write_text("synthetic failure")
        assert (await client.get("/ready")).status_code == 503
    await services.client.aclose()
