# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Synthetic local inference evidence; no cloud fallback or personal data."""

import json
import os
import time

import httpx

base = os.environ.get("OLLAMA_TEST_BASE", "http://host.docker.internal:11434")
cases = [
    ("arithmetic", "What is 12 times 9?"),
    ("reasoning", "Explain step by step why the sky is blue in at most three sentences."),
    ("private", 'This is confidential: say "back online" in three words.'),
]
with httpx.Client(timeout=180, trust_env=False) as client:
    for task_type, prompt in cases:
        start = time.monotonic()
        response = client.post(
            base + "/api/chat",
            json={
                "model": "gemma4:e2b",
                "stream": False,
                "think": False,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"num_ctx": 65536, "num_predict": 128, "temperature": 0.2},
            },
        )
        response.raise_for_status()
        data = response.json()
        print(
            json.dumps(
                {
                    "task_type": task_type,
                    "model": data.get("model"),
                    "elapsed_seconds": round(time.monotonic() - start, 3),
                    "reply": data.get("message", {}).get("content"),
                    "prompt_tokens": data.get("prompt_eval_count"),
                    "output_tokens": data.get("eval_count"),
                    "done_reason": data.get("done_reason"),
                }
            ),
            flush=True,
        )
    data = client.get(base + "/api/ps").json()
    print(
        json.dumps(
            {
                "served_models": [
                    {
                        "name": m["name"],
                        "context_length": m.get("context_length"),
                        "size": m.get("size"),
                        "size_vram": m.get("size_vram"),
                    }
                    for m in data.get("models", [])
                ]
            }
        )
    )
