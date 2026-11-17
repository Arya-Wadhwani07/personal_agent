# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Task-aware inference boundary shared by all Hermes channels and scheduled runs."""

import asyncio
import time
import uuid
from dataclasses import dataclass

import httpx

from .audit import emit
from .providers import responses_completion, responses_request
from .settings import Settings
from .state import PolicyError


class RouteError(Exception):
    def __init__(self, code: str, status: int = 503):
        self.code, self.status = code, status
        super().__init__(code)


@dataclass(frozen=True)
class Decision:
    route: str
    reason: str
    task_type: str
    private: bool


def decide(messages: list[dict]) -> Decision:
    # Sticky privacy: earlier private user turns can remain in the model context.
    user_text = " ".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
    text = user_text.casefold()
    sensitive_tools = {
        "a3_email",
        "a3_calendar",
        "a3_memory",
        "a3_activity",
        "a3_alerts",
        "a3_draft_email",
    }
    if any(
        c.get("function", {}).get("name") in sensitive_tools
        for m in messages
        for c in m.get("tool_calls", [])
        if isinstance(c, dict)
    ):
        return Decision("local", "private_tool_context", "private", True)
    if any(
        word in text for word in ("confidential", "private", "secret", "locker code", "password")
    ):
        return Decision("local", "private_context", "private", True)
    if len(user_text) > 12000:
        return Decision("cloud", "long_context", "long_context", False)
    if any(
        word in text for word in ("step by step", "reason", "compare", "analy", "research", "plan")
    ):
        return Decision("cloud", "reasoning_depth", "reasoning", False)
    return Decision("local", "simple_task", "simple", False)


async def bounded_json(client: httpx.AsyncClient, url: str, *, limit: int, **kwargs):
    async with client.stream("POST", url, **kwargs) as response:
        if response.status_code != 200:
            code = (
                "rate_limited"
                if response.status_code == 429
                else "transient_upstream"
                if response.status_code >= 500
                else "provider_rejected"
            )
            raise RouteError(code, 429 if response.status_code == 429 else 502)
        raw = bytearray()
        async for chunk in response.aiter_bytes():
            raw.extend(chunk)
            if len(raw) > limit:
                raise RouteError("response_too_large", 502)
        import json

        try:
            result = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise RouteError("invalid_upstream_json", 502) from exc
        if not isinstance(result, dict):
            raise RouteError("invalid_upstream_shape", 502)
        return result


def ollama_messages(messages):
    import copy
    import json

    result = copy.deepcopy(messages)
    for message in result:
        content = message.get("content")
        if isinstance(content, list):
            if any(not isinstance(part, dict) or part.get("type") != "text" for part in content):
                raise RouteError("Unsupported local message content", 400)
            message["content"] = "\n".join(part.get("text", "") for part in content)
        elif content is None:
            message["content"] = ""
        for call in message.get("tool_calls", []):
            arguments = call.get("function", {}).get("arguments")
            if isinstance(arguments, str):
                try:
                    call["function"]["arguments"] = json.loads(arguments)
                except ValueError as exc:
                    raise RouteError("Invalid tool arguments", 400) from exc
    return result


class Router:
    def __init__(self, settings: Settings, *, cloud=None, local=None, store=None):
        self.s = settings
        self.store = store
        self.cloud = cloud or httpx.AsyncClient(
            timeout=settings.timeout, trust_env=False, follow_redirects=False
        )
        self.local = local or httpx.AsyncClient(
            timeout=settings.timeout,
            trust_env=False,
            follow_redirects=False,
            proxy=settings.local_proxy or None,
        )

    async def close(self):
        await self.cloud.aclose()
        await self.local.aclose()

    async def _call(self, route, payload, request_id, decision, reason):
        started = time.monotonic()
        model = (
            self.s.local_model
            if route == "local"
            else self.s.primary_model
            if route == "cloud"
            else self.s.cloud_model
        )
        provider = "ollama" if route == "local" else "openai" if route == "cloud" else "nvidia"
        actual_model = None
        outcome = "failure"
        try:
            if route != "local":
                if self.s.simulate_429 or (route == "cloud" and self.s.simulate_primary_429):
                    raise RouteError("rate_limited", 429)
                if not self.s.paid_calls:
                    raise RouteError("Paid API calls are disabled pending budget configuration")
                key = self.s.primary_key if route == "cloud" else self.s.cloud_key
                if not key or not model:
                    raise RouteError("cloud_not_configured")
                if route == "cloud":
                    body = responses_request(payload, model)
                    url = self.s.primary_url
                else:
                    body = {
                        k: payload[k] for k in ("messages", "tools", "tool_choice") if k in payload
                    }
                    body.update(model=model, stream=False, max_tokens=2048)
                    url = self.s.cloud_url
                if self.store is None:
                    raise RouteError("paid_quota_unconfigured")
                try:
                    self.store.reserve_call(
                        provider,
                        self.s.openai_call_limit if route == "cloud" else self.s.nvidia_call_limit,
                    )
                except PolicyError as exc:
                    raise RouteError("paid_quota_exhausted") from exc
                data = await bounded_json(
                    self.cloud,
                    url,
                    limit=self.s.max_response,
                    headers={"Authorization": "Bearer " + key},
                    json=body,
                )
                actual_model = data.get("model")
                if route == "cloud":
                    try:
                        data = responses_completion(data, request_id)
                    except (ValueError, KeyError, TypeError) as exc:
                        raise RouteError("incomplete_model_response", 502) from exc
                choices = data.get("choices")
                if not isinstance(choices, list) or not choices:
                    raise RouteError("empty_model_response", 502)
                choice = choices[0].get("message", {})
                if choices[0].get("finish_reason") in ("length", "content_filter"):
                    raise RouteError("incomplete_model_response", 502)
                if not choice.get("content") and not choice.get("tool_calls"):
                    raise RouteError("empty_model_response", 502)
                if not isinstance(actual_model, str) or not actual_model:
                    raise RouteError("missing_model_identity", 502)
                outcome = "success"
                return data
            body = {k: payload[k] for k in ("messages", "tools") if k in payload}
            body["messages"] = ollama_messages(payload["messages"])
            body.update(
                model=model,
                stream=False,
                think=False,
                options={"num_ctx": 65536, "num_predict": 2048, "temperature": 0.2},
            )
            data = await bounded_json(
                self.local, self.s.local_url, limit=self.s.max_response, json=body
            )
            if data.get("done") is not True or data.get("done_reason") == "length":
                raise RouteError("incomplete_model_response", 502)
            actual_model = data.get("model")
            message = data.get("message", {})
            if not actual_model or (not message.get("content") and not message.get("tool_calls")):
                raise RouteError("empty_model_response", 502)
            for tool in message.get("tool_calls", []):
                import json

                tool.setdefault("id", "call_" + uuid.uuid4().hex)
                tool["type"] = "function"
                args = tool.get("function", {}).get("arguments", {})
                if isinstance(args, dict):
                    tool["function"]["arguments"] = json.dumps(args)
            outcome = "success"
            return {
                "id": "chatcmpl-" + request_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": actual_model,
                "choices": [
                    {
                        "index": 0,
                        "message": message,
                        "finish_reason": "tool_calls" if message.get("tool_calls") else "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                },
            }
        except (httpx.HTTPError, TimeoutError) as exc:
            raise RouteError("model_unavailable") from exc
        finally:
            emit(
                "routing",
                request_id=request_id,
                route="local" if route == "local" else "cloud",
                provider=provider,
                requested_model=model,
                reason=reason,
                model=actual_model,
                outcome=outcome,
                task_type=decision.task_type,
                latency_ms=round((time.monotonic() - started) * 1000),
            )

    async def complete(self, payload, decision=None):
        request_id = uuid.uuid4().hex
        decision = decision or decide(payload["messages"])
        transient = {
            "rate_limited",
            "transient_upstream",
            "model_unavailable",
            "paid_quota_exhausted",
        }
        attempted_local = False

        async def attempt(route, reason):
            async with asyncio.timeout(self.s.timeout if decision.private else self.s.timeout / 3):
                return await self._call(route, payload, request_id, decision, reason)

        try:
            # Shared total deadline, at most one call per provider, no oscillation.
            async with asyncio.timeout(self.s.timeout):
                if decision.route == "local":
                    attempted_local = True
                    try:
                        return await attempt("local", decision.reason)
                    except RouteError, TimeoutError:
                        if decision.private:
                            raise
                try:
                    return await attempt(
                        "cloud", decision.reason if not attempted_local else "local_unavailable"
                    )
                except RouteError as exc:
                    if exc.code not in transient:
                        raise
                except TimeoutError:
                    pass
                try:
                    return await attempt("nvidia", "primary_unavailable")
                except RouteError as exc:
                    if exc.code not in transient:
                        raise
                except TimeoutError:
                    pass
                if not attempted_local:
                    return await attempt("local", "cloud_chain_unavailable")
                raise RouteError("All eligible providers unavailable")
        except (RouteError, TimeoutError) as exc:
            if decision.private:
                emit(
                    "routing",
                    request_id=request_id,
                    route="held",
                    reason="private_local_unavailable",
                    model=None,
                    outcome="held",
                    task_type=decision.task_type,
                )
                raise RouteError(
                    "Private request held: local Gemma is unavailable. Nothing was sent to cloud."
                ) from exc
            if isinstance(exc, TimeoutError):
                raise RouteError("Inference deadline exceeded") from exc
            raise
