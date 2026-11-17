# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Translate Hermes's chat/tool transcript to the fixed OpenAI Responses contract."""

import json
import time


def text_content(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list) and all(
        isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str)
        for p in content
    ):
        return "\n".join(p["text"] for p in content)
    raise ValueError("Only text model input is supported")


def responses_request(payload, model):
    items = []
    for message in payload["messages"]:
        role = message["role"]
        text = text_content(message.get("content"))
        if role == "tool":
            items.append(
                {"type": "function_call_output", "call_id": message["tool_call_id"], "output": text}
            )
            continue
        if role not in {"system", "developer", "user", "assistant"}:
            raise ValueError("Unsupported message role")
        if text:
            items.append({"role": role, "content": text})
        for call in message.get("tool_calls", []):
            function = call["function"]
            args = function["arguments"]
            items.append(
                {
                    "type": "function_call",
                    "call_id": call["id"],
                    "name": function["name"],
                    "arguments": args if isinstance(args, str) else json.dumps(args),
                }
            )
    tools = []
    for tool in payload.get("tools", []):
        if tool.get("type") != "function":
            raise ValueError("Only assignment function tools are supported")
        function = tool["function"]
        tools.append(
            {
                "type": "function",
                "name": function["name"],
                "description": function.get("description", ""),
                "parameters": function["parameters"],
                "strict": False,
            }
        )
    body = {
        "model": model,
        "input": items,
        "store": False,
        "stream": False,
        "max_output_tokens": 4096,
        "truncation": "disabled",
    }
    if tools:
        body.update(tools=tools, tool_choice="auto", parallel_tool_calls=False)
    return body


def responses_completion(data, request_id):
    if data.get("status") != "completed" or data.get("error"):
        raise ValueError("incomplete_model_response")
    text, calls = [], []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    text.append(part["text"])
                elif part.get("type") == "refusal":
                    text.append(part["refusal"])
        elif item.get("type") == "function_call":
            calls.append(
                {
                    "id": item["call_id"],
                    "type": "function",
                    "function": {"name": item["name"], "arguments": item["arguments"]},
                }
            )
    message = {"role": "assistant", "content": "\n".join(text)}
    if calls:
        message["tool_calls"] = calls
    usage = data.get("usage") or {}
    return {
        "id": "chatcmpl-" + request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model"),
        "choices": [
            {"index": 0, "message": message, "finish_reason": "tool_calls" if calls else "stop"}
        ],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
        },
    }
