# I developed this file with Codex assistance; see PROCESS_LOG.md.
import json
from dataclasses import replace

import httpx
import pytest

from personal_agent.api import internal_app
from personal_agent.broker import Broker
from personal_agent.integrations import Services
from personal_agent.oauth_proxy import OAuthRouter, chat_payload, response_from_chat, response_wire
from personal_agent.routing import Router
from personal_agent.state import Store


def completion():
    return {
        "id": "r",
        "model": "synthetic-oauth-model",
        "status": "completed",
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "Cloud reply"}]}
        ],
    }


@pytest.mark.asyncio
async def test_oauth_forwards_platform_auth_only_to_fixed_endpoint(settings):
    seen = []

    def upstream(request):
        seen.append(request)
        return httpx.Response(
            200,
            text="data: "
            + json.dumps({"type": "response.completed", "response": completion()})
            + "\n\n",
        )

    s = replace(
        settings, primary_auth="oauth", primary_model="synthetic-oauth-model", paid_calls=False
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
    base = Router(s, cloud=client, local=client)
    body = {
        "model": s.primary_model,
        "input": [{"role": "user", "content": "Compare two study plans"}],
    }
    adapter = OAuthRouter(
        base,
        body,
        {"authorization": "Bearer synthetic-platform-token", "x-a3-internal": s.internal_key},
    )
    result = await adapter.complete(chat_payload(body))
    assert result["model"] == s.primary_model
    assert len(seen) == 1
    assert str(seen[0].url) == "https://chatgpt.com/backend-api/codex/responses"
    assert seen[0].headers["authorization"] == "Bearer synthetic-platform-token"
    assert "x-a3-internal" not in seen[0].headers
    assert json.loads(seen[0].content)["store"] is False
    await base.close()


@pytest.mark.asyncio
async def test_oauth_private_session_survives_compaction_and_restart(settings):
    s = replace(settings, primary_auth="oauth")
    seen = []

    def offline(request):
        seen.append(str(request.url))
        raise httpx.ConnectError("synthetic failure")

    upstream = httpx.AsyncClient(transport=httpx.MockTransport(offline))
    router = Router(s, cloud=upstream, local=upstream)
    for text in ("This is confidential", "Compare the options in my compacted conversation"):
        store = Store(s.state_dir)
        broker = Broker(s, store, Services(s, client=upstream))
        app = internal_app(s, router=router, broker=broker)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://policy"
        ) as client:
            headers = {
                "x-a3-internal": s.internal_key,
                "x-a3-session": "persistent-session",
                "authorization": "Bearer synthetic-oauth",
            }
            denied = await client.post(
                "/codex/responses", json={}, headers={"authorization": "Bearer " + s.internal_key}
            )
            assert denied.status_code == 401
            response = await client.post(
                "/codex/responses",
                headers=headers,
                json={"input": [{"role": "user", "content": text}]},
            )
            assert response.status_code == 200
            assert "Private request held" in response.text
        store.close()
    assert len(seen) == 2
    assert all(url == s.local_url for url in seen)
    await router.close()


def test_tool_identity_roundtrip():
    chat = {
        "model": "gemma4:e2b",
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "id": "call_test",
                            "function": {"name": "a3_memory", "arguments": '{"action":"read"}'},
                        }
                    ]
                }
            }
        ],
    }
    response = response_from_chat(chat)
    wire, media = response_wire(response, True)
    assert media == "text/event-stream" and "response.completed" in wire
    transcript = chat_payload(
        {
            "input": response["output"]
            + [{"type": "function_call_output", "call_id": "call_test", "output": "{}"}]
        }
    )
    assert transcript["messages"][0]["tool_calls"][0]["id"] == "call_test"
    assert transcript["messages"][1]["tool_call_id"] == "call_test"
