# Monday — My Cloud and Local Model Comparison

I measured **three task types** through the full local Hermes gateway with live OpenAI OAuth and Ollama inference. The six initial turns ran on November 17, 2026, from 21:40:21 to 21:41:11 UTC; a targeted tool-schema retest ran at 22:09:02 UTC. These are local-container measurements, not Cloud Run network-latency measurements.

[Sanitized prompts, replies, timestamps and model-route records](../evaluation/model-comparison.json)

## Method

- **Cloud:** `gpt-6.1-sol`, using Hermes-owned browser OAuth and the routing proxy.
- **Local:** `gemma4:e2b`, native Ollama API, `num_ctx=65536`, `think=false`, `num_predict=2048`, temperature 0.2.
- **Hardware:** the setup-verified 16-GiB Mac; the agent container is bounded to 4 CPUs/4 GiB locally. Ollama runs separately on the authorized host.
- **Task pairing:** both routes receive the same substantive task. A confidential-synthetic-data prefix selects local; an analysis prefix selects cloud. This is a routing-controlled comparison, not an identical-prompt randomized trial.
- **Timing:** wall time from API request to final agent answer, including tool turns. One initial sample per route/type; no percentile or statistical superiority claim.
- **Quality:** exact arithmetic, correct extracted fields and actual tool-confirmed status/flag. An HTTP 200 alone is insufficient.
- **Identity:** route logs identify the actual serving model and outcome. The gateway response's model field is not used as proof of the provider.

## Results

| Task type and quality criterion | Local full-turn time | Cloud full-turn time | Quality assessment |
| --- | --- | --- | --- |
| Arithmetic: 17 × 6 = 102 with a short explanation | 28.009 s | 8.036 s | Both correct. |
| Structured extraction: Bluebird and Friday as JSON | 2.801 s | 2.104 s | Both returned the correct project and due day. |
| Tool provenance: validate the supplied fictional ledger with `a3_review_content` | 2.257 s initially; **failed task** | 7.324 s | Local omitted the required topic, was safely rejected and reported failure. Cloud executed the tool and returned `ready_for_human_review`, publishing false. |
| Targeted local tool retest after schema correction | **27.223 s; passed** | Not repeated | The same substantive task succeeded; tool and routing logs confirm the real local call and successful validation. |

## What changed after the failed tool turn

The original tool schema described `draft` only as an object. Gemma omitted `topic`; the policy validator correctly rejected it. I expanded the schema to describe the required topic, body, source ledger and claims, including nested fields, then rebuilt and repeated the failed turn. The report retains the original failure rather than presenting the retest as the only sample.

## Routing assessment

- All confidential variants stayed on **local Gemma** with the logged `private_session` reason.
- All analysis variants used **OpenAI OAuth** with `reasoning_depth`.
- The content-validation turns exercised the actual tool path, not only a direct model chat.
- The local failure was a tool-argument quality failure, while model inference itself succeeded. Distinguishing those outcomes makes the comparison useful.
- The small sample supports the privacy/routing behavior and identifies a schema improvement. It does not establish broad quality rankings, tail latency, or cold/warm-load distributions.

## Resource and cost interpretation

The evidence records Ollama's loaded context and memory metadata after the retest. Those fields describe the loaded model allocation, not a measured peak for the entire laptop. The first arithmetic and later retest were slower, but I did not isolate model-loading time and will not label them calibrated cold-start benchmarks.

Paid API-key calls were disabled during these measurements. OAuth used the authenticated account entitlement; no per-token dollar price or unlimited entitlement is inferred. Local inference has hardware/energy cost that this experiment did not measure. The bounded NVIDIA fallback was not used in this comparison; its direct preflight is separate evidence.

My cloud plan uses a **$4 tracking target**, 50 Tavily attempts, 20 NVIDIA attempts and zero paid OpenAI-key attempts. Budget tracking is not a billing hard cap. The Instance target is `us-west1`; the existing registry and bucket remain in `us-central1`. The release cost review includes regional compute, storage/operations, cross-region transfer and the full grading/regrade availability period.

## Reproduction and release use

The JSON artifact records the exact synthetic inputs, baseline commit, corrected broker hash, local image and observed outputs. I run the same three task categories through the final authenticated grader interface for deployment acceptance, preserving the actual environment label. I use the release checklist to distinguish this measured comparison from deployed connectivity and the separate 48-hour operational record.

The separate cloud resource projection uses verified Oregon Instance catalog rates: $0.00000027 per vCPU-second and $0.00000193 per GiB-second. At 1 vCPU / 2 GiB, compute is $0.713664 for 48 hours or $2.140992 for 144 hours. My six-day plan reserves another $1.40 for search and other services; this is an estimate, not measured billed spending. [Cloud Run pricing](https://cloud.google.com/run/pricing) · [Storage and cross-region transfer](https://cloud.google.com/storage/pricing)

## Final deployment accuracy and recovery checks

My final-image acceptance retained two incorrect private arithmetic responses alongside successful retests. `17 + 25` initially returned `31`, then an explicit calculation prompt returned `42`; a private multiplication variant returned `72`, while the prescribed `What is 12 times 9?` prompt returned `108` in 0.66 seconds. Local memory-tool completion and recall also succeeded. These results show that local routing and tool integration work but do not establish uniformly reliable arithmetic or wording independence.

After a controlled stop/start, the first cloud reply took 62.12 seconds and memory recall took 24.63 seconds. Cloud Logging records actual OAuth inference, a cloud-eligible local failure followed by OAuth fallback, and later private local success. I retain cold-start and model-quality variability instead of reporting only the fastest or correct turns. [Final verification record](IMPLEMENTATION_STATUS.md)
