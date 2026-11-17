# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Bounded synthetic ASGI load/stress probe; no network services or paid APIs."""

import asyncio
import json
import statistics
import time

import httpx

from personal_agent.api import edge_app
from personal_agent.settings import Settings


async def main():
    s = Settings(
        api_key="synthetic-public-" + "a" * 32, internal_key="synthetic-internal-" + "b" * 32
    )

    async def upstream(request):
        await asyncio.sleep(0.02)
        return httpx.Response(200, json={"choices": [{"message": {"content": "synthetic reply"}}]})

    app = edge_app(
        s, httpx.AsyncClient(base_url="http://mock", transport=httpx.MockTransport(upstream))
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:

        async def phase(name, concurrency, count):
            semaphore = asyncio.Semaphore(concurrency)
            latencies = []
            statuses = []

            async def one():
                async with semaphore:
                    start = time.perf_counter()
                    response = await client.post(
                        "/v1/chat/completions",
                        headers={"Authorization": "Bearer " + s.api_key},
                        json={"messages": [{"role": "user", "content": "synthetic"}]},
                    )
                    latencies.append((time.perf_counter() - start) * 1000)
                    statuses.append(response.status_code)

            async with asyncio.timeout(60):
                await asyncio.gather(*(one() for _ in range(count)))
            if any(code not in (200, 429) for code in statuses):
                raise RuntimeError("Unexpected load failure")
            if name in ("representative", "recovery") and any(code != 200 for code in statuses):
                raise RuntimeError(f"{name} load rejected")
            return {
                "phase": name,
                "requests": count,
                "concurrency": concurrency,
                "status_counts": {str(code): statuses.count(code) for code in set(statuses)},
                "p95_ms": round(statistics.quantiles(latencies, n=100)[94], 3),
            }

        reports = [
            await phase("representative", 4, 100),
            await phase("stress", 32, 256),
            await phase("recovery", 1, 10),
        ]
        print(
            json.dumps({"transport": "ASGI", "upstream": "mocked 20ms latency", "results": reports})
        )


if __name__ == "__main__":
    asyncio.run(main())
