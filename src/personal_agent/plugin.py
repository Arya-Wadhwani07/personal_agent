# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Hermes v0.22.7 plugin: narrow tools and a human-only Telegram approval callback."""

import json
import os
import threading
from collections import OrderedDict

import httpx

from .broker import TOOLS

# Native dispatch can omit user_task. Bind authorization to the request's actual
# latest user message, never a model-supplied tool argument or retrieved result.
_SESSION_TASKS = OrderedDict()
_TASK_LOCK = threading.Lock()


def remember_user_request(request, session_id):
    if not session_id:
        return
    messages = request.get("messages", request.get("input", []))
    task = ""
    if isinstance(messages, list):
        for message in reversed(messages):
            if not isinstance(message, dict) or message.get("role") != "user":
                continue
            content = message.get("content", "")
            if isinstance(content, list):
                content = "\n".join(
                    part.get("text", "") for part in content
                    if isinstance(part, dict) and part.get("type") in ("text", "input_text")
                    and isinstance(part.get("text"), str)
                )
            if isinstance(content, str) and len(content) <= 16384:
                task = content
            break
    with _TASK_LOCK:
        _SESSION_TASKS[str(session_id)] = task
        _SESSION_TASKS.move_to_end(str(session_id))
        while len(_SESSION_TASKS) > 128:
            _SESSION_TASKS.popitem(last=False)


def authorized_user_task(session_id):
    with _TASK_LOCK:
        return _SESSION_TASKS.get(str(session_id), "")


def rpc(method, path, payload=None):
    try:
        with httpx.Client(base_url="http://127.0.0.1:8090", trust_env=False, timeout=90) as client:
            response = client.request(
                method,
                path,
                json=payload,
                headers={"Authorization": "Bearer " + os.environ["A3_INTERNAL_KEY"]},
            )
        if response.status_code != 200:
            return {"error": "Policy/service rejected the request; no action confirmed"}
        return response.json()
    except httpx.HTTPError, ValueError, KeyError:
        return {"error": "Policy service unavailable; no action confirmed"}


def guard(tool_name=None, function_name=None, **kwargs):
    name = tool_name or function_name
    if name not in TOOLS:
        return {"action": "block", "message": "Only the class-only assistant tools are allowed."}
    return None


def inference_headers(request, session_id="", **kwargs):
    remember_user_request(request, session_id)
    request = dict(request)
    request["extra_headers"] = {
        **request.get("extra_headers", {}),
        "x-a3-internal": os.environ["A3_INTERNAL_KEY"],
        "x-a3-session": str(session_id),
    }
    if os.environ.get("A3_PRIMARY_AUTH", "oauth") == "oauth":
        request["extra_headers"].update(
            {"originator": "hermes-agent", "user-agent": "HermesAgent/0.22.7"}
        )
    return {"request": request}


def register(ctx):
    ctx.register_middleware("llm_request", inference_headers)
    for name, (description, properties) in TOOLS.items():

        def handler(args, _name=name, **kwargs):
            return json.dumps(
                rpc(
                    "POST",
                    "/tools/" + _name,
                    {"arguments": args, "user_task": authorized_user_task(kwargs.get("session_id", ""))},
                )
            )

        required = {
            "a3_draft_email": ["to", "subject", "body"],
            "a3_search": ["query"],
            "a3_content_brief": ["topic", "body", "sources"],
            "a3_review_content": ["draft"],
            "a3_memory": ["action"],
        }.get(name, [])
        ctx.register_tool(
            name=name,
            toolset="assignment3",
            description=description,
            schema={
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
            handler=handler,
        )
    ctx.register_hook("pre_tool_call", guard)
    ctx.register_platform_handler("telegram", telegram_handlers)


def telegram_handlers(native, adapter):
    import asyncio

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import ApplicationHandlerStop, CallbackQueryHandler, CommandHandler

    owner = os.environ.get("TELEGRAM_ALLOWED_USERS", "")

    async def review(update, context):
        if not update.effective_user or str(update.effective_user.id) != owner:
            raise ApplicationHandlerStop
        if not context.args or len(context.args[0]) > 32:
            await update.effective_message.reply_text("Use /review followed by the draft ID.")
            raise ApplicationHandlerStop
        draft = await asyncio.to_thread(rpc, "GET", "/drafts/" + context.args[0])
        if "payload" not in draft:
            await update.effective_message.reply_text("Draft unavailable or expired.")
            raise ApplicationHandlerStop
        p = draft["payload"]
        # Plain text, never HTML or Markdown from untrusted mail/model data.
        text = (
            "Review this exact email:\nTo: "
            + p["to"]
            + "\nSubject: "
            + p["subject"]
            + "\n\n"
            + p["body"]
        )
        if len(text) > 3800:
            await update.effective_message.reply_text(
                "Draft is too long for a single approval view. Ask for a shorter draft."
            )
            raise ApplicationHandlerStop
        await update.effective_message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Approve and send this email", callback_data="a3:send:" + draft["id"]
                        ),
                        InlineKeyboardButton("Cancel", callback_data="a3:cancel"),
                    ]
                ]
            ),
        )
        raise ApplicationHandlerStop

    async def callback(update, context):
        query = update.callback_query
        if not update.effective_user or str(update.effective_user.id) != owner:
            await query.answer("Not authorized", show_alert=True)
            raise ApplicationHandlerStop
        await query.answer()
        if query.data == "a3:cancel":
            await query.edit_message_reply_markup(reply_markup=None)
            raise ApplicationHandlerStop
        identifier = query.data.removeprefix("a3:send:")
        draft = await asyncio.to_thread(rpc, "GET", "/drafts/" + identifier)
        if "digest" not in draft:
            await query.message.reply_text("Draft expired or already consumed.")
            raise ApplicationHandlerStop
        result = await asyncio.to_thread(
            rpc,
            "POST",
            "/human/approve",
            {
                "id": identifier,
                "digest": draft["digest"],
                "human_id": str(update.effective_user.id),
            },
        )
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "Email sent."
            if result.get("status") == "sent"
            else "Send not confirmed. Check Gmail; do not blindly retry."
        )
        raise ApplicationHandlerStop

    native.add_handler(CommandHandler("review", review), group=-20)
    native.add_handler(CallbackQueryHandler(callback, pattern=r"^a3:(send:|cancel$)"), group=-20)
