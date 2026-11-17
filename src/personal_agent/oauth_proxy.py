# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Route platform-authenticated Responses requests; never acquire or refresh OAuth tokens."""

import json
import time
import uuid

import httpx

from .audit import emit
from .providers import responses_completion
from .routing import RouteError, Router


def chat_payload(body):
    messages = []
    if body.get("instructions"):
        messages.append({"role": "system", "content": body["instructions"]})
    items = body.get("input", [])
    if isinstance(items, str):
        items = [{"role": "user", "content": items}]
    for item in items:
        kind = item.get("type", "message")
        if kind == "message":
            content = item.get("content", "")
            if isinstance(content, list):
                if any(p.get("type") not in ("input_text", "output_text") for p in content):
                    raise RouteError("Only text inputs are supported", 400)
                content = "\n".join(p["text"] for p in content)
            messages.append({"role": item["role"], "content": content})
        elif kind == "function_call":
            messages.append(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": item["call_id"],
                            "type": "function",
                            "function": {"name": item["name"], "arguments": item["arguments"]},
                        }
                    ],
                }
            )
        elif kind == "function_call_output":
            messages.append(
                {"role": "tool", "tool_call_id": item["call_id"], "content": item["output"]}
            )
        elif kind != "reasoning":
            raise RouteError("Unsupported Responses input", 400)
    if not messages:
        raise RouteError("Messages are required", 400)
    tools = []
    for tool in body.get("tools", []):
        if tool.get("type") != "function" or not tool.get("name", "").startswith("a3_"):
            raise RouteError("Only assignment tools are supported", 400)
        tools.append(
            {
                "type": "function",
                "function": {
                    k: tool[k] for k in ("name", "description", "parameters") if k in tool
                },
            }
        )
    return {"messages": messages, "tools": tools}


def response_from_chat(chat):
    message = chat["choices"][0]["message"]
    output = []
    if message.get("content"):
        output.append(
            {
                "id": "msg_" + uuid.uuid4().hex,
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": message["content"], "annotations": []}],
            }
        )
    for call in message.get("tool_calls", []):
        output.append(
            {
                "id": "fc_" + uuid.uuid4().hex,
                "type": "function_call",
                "status": "completed",
                "call_id": call["id"],
                **call["function"],
            }
        )
    return {
        "id": "resp_" + uuid.uuid4().hex,
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "error": None,
        "incomplete_details": None,
        "model": chat["model"],
        "output": output,
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
        "usage": None,
    }


def response_wire(data, stream):
    if not stream:
        return json.dumps(data), "application/json"
    # Hermes's Responses accumulator accepts a complete terminal frame, including tool calls.
    events = [
        {"type": "response.created", "response": {**data, "status": "in_progress", "output": []}}
    ]
    events += [
        {"type": "response.output_item.done", "output_index": i, "item": item}
        for i, item in enumerate(data["output"])
    ]
    events.append({"type": "response.completed", "response": data})
    return "".join(
        "event: " + e["type"] + "\ndata: " + json.dumps({**e, "sequence_number": i}) + "\n\n"
        for i, e in enumerate(events)
    ), "text/event-stream"


class OAuthRouter(Router):
    """Per-request adapter with shared clients; credentials exist only for this request."""

    def __init__(self, parent, body, headers):
        super().__init__(parent.s, cloud=parent.cloud, local=parent.local, store=parent.store)
        self.original = body
        self.forward_headers = {
            k: headers[k]
            for k in (
                "authorization",
                "chatgpt-account-id",
                "x-openai-internal-codex-residency",
                "session_id",
                "openai-beta",
                "originator",
                "user-agent",
            )
            if k in headers
        }

    async def _call(self, route, payload, request_id, decision, reason):
        if route != "cloud":
            return await super()._call(route, payload, request_id, decision, reason)
        started, outcome, actual = time.monotonic(), "failure", None
        try:
            if self.s.simulate_429 or self.s.simulate_primary_429:
                raise RouteError("rate_limited", 429)
            # Hermes supplied the credential. No auth-file reads or OAuth token exchange here.
            if not self.forward_headers.get("authorization", "").startswith("Bearer "):
                raise RouteError("Hermes OAuth authentication required", 401)
            body = dict(self.original)
            if body.get("model") != self.s.primary_model or not self.s.primary_model:
                raise RouteError("Configured OAuth model mismatch", 400)
            body.update(store=False, stream=True)
            body.setdefault("instructions", "")
            for key in ("max_output_tokens", "temperature", "top_p", "truncation"):
                body.pop(key, None)
            done_items, terminal, buffered, total = [], None, b"", 0
            async with self.cloud.stream(
                "POST",
                "https://chatgpt.com/backend-api/codex/responses",
                json=body,
                headers=self.forward_headers,
            ) as response:
                if response.status_code != 200:
                    code = (
                        "rate_limited"
                        if response.status_code == 429
                        else "transient_upstream"
                        if response.status_code >= 500
                        else "provider_rejected"
                    )
                    raise RouteError(code, 429 if response.status_code == 429 else 502)
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > self.s.max_response:
                        raise RouteError("response_too_large", 502)
                    buffered += chunk
                    while b"\n" in buffered:
                        line, buffered = buffered.split(b"\n", 1)
                        if not line.startswith(b"data:"):
                            continue
                        raw = line[5:].strip()
                        if raw == b"[DONE]":
                            continue
                        event = json.loads(raw)
                        if event.get("type") == "response.output_item.done":
                            done_items.append(event["item"])
                        if event.get("type") in (
                            "response.completed",
                            "response.failed",
                            "response.incomplete",
                        ):
                            terminal = event["response"]
                    if terminal is not None:
                        break
            if terminal is None:
                raise RouteError("incomplete_model_response", 502)
            if terminal.get("output") is None:
                terminal["output"] = done_items
            result = responses_completion(terminal, request_id)
            actual = result.get("model")
            message = result["choices"][0]["message"]
            if not actual or not (message.get("content") or message.get("tool_calls")):
                raise RouteError("empty_model_response", 502)
            outcome = "success"
            return result
        except (httpx.HTTPError, TimeoutError) as exc:
            raise RouteError("model_unavailable") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise RouteError("invalid_oauth_response", 502) from exc
        finally:
            emit(
                "routing",
                request_id=request_id,
                route="cloud",
                provider="openai-oauth",
                requested_model=self.s.primary_model,
                reason=reason,
                model=actual,
                outcome=outcome,
                task_type=decision.task_type,
                latency_ms=round((time.monotonic() - started) * 1000),
            )
