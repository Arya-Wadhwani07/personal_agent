# Monday — Verification Record

I record results with their environment and artifact. This page is evidence about those checks, not a blanket claim about every deployment or future operating interval.

## Source and application checks

| Check | Recorded result | Scope |
| --- | --- | --- |
| Regression | **213 tests passed in 23.71 seconds** on November 17. | Offline Docker, disposable state, 4 CPUs/4 GiB. |
| Static review | Ruff and Bandit passed on the reviewed source; repeat on each release. | Source checks, not proof of no vulnerabilities. |
| Browser | Chromium chat, content review, unsafe-text handling, error recovery, mobile layout and sign-out tests passed. | Model replies mocked; interface behavior exercised. |
| Telegram rendering | Synthetic preview accepted with six bold entities in MarkdownV2. | Actual Telegram delivery and parser; no claim about every generated message. |
| Injection boundaries | Three distinct injected-action cases blocked without external calls or persistent writes. | Actual policy layer; model interpretation simulated. |
| Weather freshness and recovery | Live Open-Meteo check returned today's data; offline tests cover next day, local midnight/DST, null/stale values, transient retry, rate limits and recovery. | No long-duration provider-availability guarantee. |
| Local-outage failover | Real native/public gateway reached `gpt-6.1-sol` through OAuth with an unreachable test Ollama endpoint; public reply in 2.87 s. Private request held without cloud inference; after recovery, a real Gemma reply completed in 21.32 s. | Local sandbox with real OAuth inference; NVIDIA branch tested by fault injection, alongside the earlier live provider preflight. |
| Model comparison | Three task types through live local Hermes, OAuth and Ollama; one initial local schema failure corrected and successfully retested. | [Measured report](PERFORMANCE_REPORT.md). |
| Local serving | Gemma 4 E2B; 65,536 context; full tool turn completed. | Model allocation after retest: 7,428,940,802 bytes; not whole-system peak RAM. |
| Load / stress | 100/100 mocked requests at concurrency 4; p95 22.084 ms. Concurrency 32: four successes, 252 bounded HTTP 429s, then 10/10 recovery successes. | Fake 20-ms upstream; not model or cloud throughput. |
| Native scheduled scripts | Both reviewed scripts executed through Hermes’s scheduler against a synthetic local service; out-of-directory paths remained blocked. | Regression added after live acceptance exposed the original path error. |
| Source integrity | Five PDF hashes unchanged; 19 extracted files match ZIP members; 94 stable requirement IDs. | Original documents retained locally. |

## Integration and delivery evidence

- Real Google refresh, class-only account reads and dedicated-calendar reads were exercised.
- Separate native cloud OAuth rotation and fresh-profile recovery passed.
- Runtime-identity GCS save/restore, quota recovery and stale-writer rejection passed.
- Direct Tavily search and NVIDIA fallback preflights passed under bounded quotas.
- Permitted and denied private-network clients were checked against the owned tailnet.
- Native gateway tests and owner-confirmed Telegram replies exercised the local assistant.
- The original skill was published at a pinned GitHub tap revision, then installed and executed in a fresh native environment.

These probes have distinct scopes. The [release checklist](FINAL_REVIEW.md) repeats the relevant checks against the actual Instance before observation.

## Artifact-specific image evidence

The `9297bd4` weather/failover candidate passed [isolated validation](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44208764242), the [native image gate](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44208764207), and [approved publication](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44209039487). Artifact Registry confirms digest `sha256:5c99eb0e5f2931a25c08c90e9133c780be8e722b5697ff125f4112d8263b0640`; its Linux/amd64 image label matches the full source revision. Publication is separate from production deployment and observation.

Every publish runs the image/profile gate again and retains raw findings. Exact-version dispositions expire November 24; unknown Critical/High findings, profile drift or expired decisions block release. [Security register](SECURITY_REGISTER.md)

## Deployment configuration

- **Instance target:** `assignment3-515003`, `us-west1`, 1 vCPU / 2 GiB.
- **Existing registry and bucket region:** `us-central1`; these are separate resources from the Instance.
- **Release control:** exact image digest, reviewed region, pinned secrets, required GitHub production review and main-branch restriction.
- **Budget:** verified regional rates give $2.140992 compute over 144 hours at 1 vCPU / 2 GiB. With $0.40 search and $1.00 other-services reserves, the projection is $3.540992. Actual usage and availability extensions are reviewed against the $4 target; this is not a hard billing cap.
- **Evidence:** actual live acceptance, timestamps, logs, video and grader access fields are collected outside the frozen source and supplied through the prescribed submission channels.
