# I developed this file with Codex assistance; see PROCESS_LOG.md.
import json
from dataclasses import replace

import httpx
import pytest

from personal_agent.routing import RouteError, Router, decide


def completion(model="nim-test"):
    return {
        "model": model,
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": "108"}]}],
    }


def local_result():
    return {"model": "gemma4:e2b", "message": {"role": "assistant", "content": "108"}, "done": True}


def clients(cloud, local):
    return {
        "cloud": httpx.AsyncClient(transport=httpx.MockTransport(cloud)),
        "local": httpx.AsyncClient(transport=httpx.MockTransport(local)),
    }


@pytest.mark.parametrize(
    "text,route,kind",
    [
        ("What is 12 times 9?", "local", "simple"),
        ("Explain step by step why the sky is blue.", "cloud", "reasoning"),
        ("This is confidential: say back online.", "local", "private"),
        ("a" * 12001, "cloud", "long_context"),
    ],
)
def test_task_selection(text, route, kind):
    actual = decide([{"role": "user", "content": text}])
    assert (actual.route, actual.task_type) == (route, kind)


async def test_private_never_cloud_even_when_local_fails(settings, caplog):
    calls = []

    def cloud(request):
        calls.append("cloud")
        return httpx.Response(200, json=completion())

    def local(request):
        raise httpx.ConnectError("synthetic offline")

    router = Router(settings, **clients(cloud, local))
    caplog.set_level("INFO", logger="a3.audit")
    with pytest.raises(RouteError, match="held"):
        await router.complete(
            {"messages": [{"role": "user", "content": "confidential locker code 999"}]}
        )
    assert calls == []
    assert "locker" not in caplog.text and "999" not in caplog.text
    assert '"outcome":"held"' in caplog.text


async def test_sticky_privacy(settings):
    calls = []

    def cloud(request):
        calls.append("cloud")
        return httpx.Response(200, json=completion())

    def local(request):
        return httpx.Response(200, json=local_result())

    result = await Router(settings, **clients(cloud, local)).complete(
        {
            "messages": [
                {"role": "user", "content": "This is confidential."},
                {"role": "assistant", "content": "Understood."},
                {"role": "user", "content": "Now analyze it step by step."},
            ]
        }
    )
    assert result["model"] == "gemma4:e2b" and not calls


async def test_laptop_off_cloud_continuity(settings):
    def local(request):
        raise httpx.ConnectError("offline")

    result = await Router(
        settings, **clients(lambda r: httpx.Response(200, json=completion()), local)
    ).complete({"messages": [{"role": "user", "content": "Hello"}]})
    assert result["model"] == "nim-test"


async def test_429_fallback_and_reversal(settings):
    calls = []

    def cloud(request):
        calls.append("cloud")
        return httpx.Response(200, json=completion())

    def local(request):
        payload = json.loads(request.content)
        assert payload["options"]["num_ctx"] == 65536
        assert payload["think"] is False
        return httpx.Response(200, json=local_result())

    payload = {"messages": [{"role": "user", "content": "Reason step by step"}]}
    result = await Router(replace(settings, simulate_429=True), **clients(cloud, local)).complete(
        payload
    )
    assert result["model"] == "gemma4:e2b" and not calls
    result = await Router(settings, **clients(cloud, local)).complete(payload)
    assert result["model"] == "nim-test" and calls == ["cloud"]


async def test_empty_model_response_is_failure(settings):
    def empty(request):
        return httpx.Response(200, json={"model": "nim", "choices": [{"message": {"content": ""}}]})

    with pytest.raises(RouteError, match="incomplete"):
        await Router(settings, **clients(empty, empty)).complete(
            {"messages": [{"role": "user", "content": "Reason deeply"}]}
        )


def test_native_ollama_message_conversion():
    from personal_agent.routing import ollama_messages

    original = [
        {"role": "user", "content": [{"type": "text", "text": "Synthetic"}]},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"function": {"name": "a3_memory", "arguments": '{"action":"read"}'}}],
        },
    ]
    converted = ollama_messages(original)
    assert converted[0]["content"] == "Synthetic"
    assert converted[1]["tool_calls"][0]["function"]["arguments"] == {"action": "read"}
    assert isinstance(original[0]["content"], list)
