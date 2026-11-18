# Monday — Verification Record

I record results with their environment and artifact. This page is evidence about those checks, not a blanket claim about every deployment or future operating interval.

## Source and application checks

| Check | Recorded result | Scope |
| --- | --- | --- |
| Regression | **244 tests passed in 25.83 seconds** on November 17. | Offline Docker, disposable state, 4 CPUs/4 GiB. |
| Static review | Ruff and Bandit passed on the reviewed source; repeat on each release. | Source checks, not proof of no vulnerabilities. |
| Browser | Chromium chat, content review, unsafe-text handling, error recovery, mobile layout and sign-out tests passed. | Model replies mocked; interface behavior exercised. |
| Telegram rendering | Synthetic preview accepted with six bold entities in MarkdownV2. | Actual Telegram delivery and parser; no claim about every generated message. |
| Injection boundaries | Three distinct injected-action cases blocked without external calls or persistent writes. | Actual policy layer; model interpretation simulated. |
| Weather freshness and recovery | Local Open-Meteo checks passed; live Cloud Run acceptance exposed a TLS timeout. The deployed NWS fallback subsequently returned fresh named-period forecasts from that Instance. Offline tests also cover fallback freshness, period/unit and URL validation. | No long-duration provider-availability guarantee. |
| Local-outage failover | Real native/public gateway reached `gpt-6.1-sol` through OAuth with an unreachable test Ollama endpoint; public reply in 2.87 s. Private request held without cloud inference; after recovery, a real Gemma reply completed in 21.32 s. | Local sandbox with real OAuth inference; NVIDIA branch tested by fault injection, alongside the earlier live provider preflight. |
| Model comparison | Three task types through live local Hermes, OAuth and Ollama; one initial local schema failure corrected and successfully retested. | [Measured report](PERFORMANCE_REPORT.md). |
| Local serving | Gemma 4 E2B; 65,536 context; full tool turn completed. | Model allocation after retest: 7,428,940,802 bytes; not whole-system peak RAM. |
| Load / stress | 100/100 mocked requests at concurrency 4; p95 22.084 ms. Concurrency 32: four successes, 252 bounded HTTP 429s, then 10/10 recovery successes. | Fake 20-ms upstream; not model or cloud throughput. |
| Native scheduled scripts | Both reviewed scripts executed through Hermes’s scheduler against a synthetic local service; out-of-directory paths remained blocked. | Regression added after live acceptance exposed the original path error. |
| Native memory authorization | Real Hermes tool turns persist a literal synthetic fact in both API-key and OAuth modes; tool-result/cross-session context is rejected. | Added after live acceptance exposed an omitted native context argument. |
| Concurrent interfaces | Two distinct native gateway requests complete in the isolated smoke test; admission remains bounded at two. | Synthetic upstream; deployed behavior has its own acceptance check. |
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

The `f478e61` weather and daily-reading candidate passed [hosted validation](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44244942276), the [native image gate](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44244942080), and [approved publication with native tests and runtime security checks](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44245110126). Artifact Registry confirms digest `sha256:dec449692d77d0f78c4b8246f20b933224cec07eb6ec1053f8756f08ffaecf50`; its Linux/amd64 image label matches the full source revision. This image retains the scheduler, memory, concurrency and meeting-time corrections and adds bounded NWS fallback and the daily indexed LinkedIn recommendation. Publication is separate from exact-image production approval, live acceptance and observation.

Every publish runs the image/profile gate again and retains raw findings. Exact-version dispositions expire November 24; unknown Critical/High findings, profile drift or expired decisions block release. [Security register](SECURITY_REGISTER.md)

## Deployment configuration

- **Instance target:** `assignment3-515003`, `us-west1`, 1 vCPU / 2 GiB.
- **Existing registry and bucket region:** `us-central1`; these are separate resources from the Instance.
- **Release control:** exact image digest, reviewed region, pinned secrets, required GitHub production review and main-branch restriction.
- **Budget:** verified regional rates give $2.140992 compute over 144 hours at 1 vCPU / 2 GiB. With $0.40 search and $1.00 other-services reserves, the projection is $3.540992. Actual usage and availability extensions are reviewed against the $4 target; this is not a hard billing cap.
- **Evidence:** actual live acceptance, timestamps, logs, video and grader access fields are collected outside the frozen source and supplied through the prescribed submission channels.

### Latest presentation correction

My isolated regression suite verifies meeting-alert dates, local start/end times, timezone offsets, missing end-time handling, daylight-saving transitions and escaped Telegram delivery. Morning briefing instructions require sender, subject and a preview-grounded email summary; absent previews stay explicit. This correction is included with native memory-context and bounded-concurrency changes in the published `414dfef` image. Live checks on that deployment verified memory persistence/recall, both model paths, Telegram replies and timed meeting alerts; those results are recorded below.

### Weather and daily-reading candidate

The corrected source adds NWS fallback after the measured cloud-only Open-Meteo failure, plus an indexed LinkedIn daily reading recommendation. The 241-test offline run covers weather failure/recovery, fallback URL restrictions, preview-only evidence, daily caching and duplicate avoidance. Its native publication passed, and live checks on the deployed image verified both features. The separately observed startup timeout is addressed by the subsequent startup correction.

On the prior `414dfef` deployment, I verified real memory persistence/recall, both model paths, an owner-confirmed Telegram reply, an owner-confirmed timed meeting alert, and actual scheduled morning delivery. The alert record includes November 17, 9:45–10:45 PM PST. The owner confirmed the briefing’s other sections looked good; weather failure is preserved as the reason for this correction. The 48-hour interval has not started.

### Native initialization correction

Live startup of the weather/reading image exceeded the supervisor’s 20-second native schedule-initialization limit and retried before becoming healthy. I retained that trace and corrected the limit to a bounded 120 seconds. The initializer now belongs to the cleanup set until successful completion; timeout and shutdown terminate it. The 244-test regression suite includes slow initialization, deadline failure and shutdown cleanup. The startup correction passed hosted publication; exact-image deployment approval and cold-restart acceptance remain the release gates before observation.

On the deployed `f478e61` image, the weather tool returned HTTP 200 with NWS forecast periods after the primary timeout (16.41 seconds total). The daily-reading tool returned HTTP 200 with a real indexed LinkedIn AI-post preview (3.52 seconds). Both deployed adapter source hashes matched the reviewed source. These are live feature results; they do not waive the separately observed startup timeout or replace final restart acceptance.

The actual morning schedule completed and delivered at **2026-11-18 05:54:38 UTC (November 17, 9:54 PM PST)** on `f478e61`. Its output included the NWS forecast periods and a clearly labeled LinkedIn search preview with a short summary and reason to read it. This verifies the scheduled path, beyond direct tool calls.

The startup correction is published from source `405e284368fcd5f4d9f9a07bb7a044529a479be4`: [hosted validation](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44247838150) and [native publication, tests and runtime vulnerability gate](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44247908159) passed. Artifact Registry confirms Linux/amd64 and the matching source label at `sha256:968f8f63eeb20bdac1b67390b914dac8e93ae3e0ff9ace592bffd25473c1b883`. The earlier code-identical `9bb1098` runtime-image gate also passed; its validation run was superseded by the successful documentation-inclusive revision.
