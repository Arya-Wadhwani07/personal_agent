# My Implementation and Evidence Status

Last updated: November 16, 2026. My assignment is **not ready for submission or deployment**. I authorized full implementation, Docker runtime files, local Ollama checks, and synthetic tests limited to 4 CPUs/4 GiB and 60 seconds per load/stress run.

## My verified checkpoint

| Scope | Observed result | Practical limit |
| --- | --- | --- |
| Isolated tests | 37 tests passed in 11.49 seconds, with networking disabled and read-only project source. | External services were mocked; later network-startup additions are not included in this completed suite. |
| Real Hermes integration | A real Hermes v0.22.7 gateway loaded my plugin, invoked my memory tool, and returned a reply through the browser edge. | The isolated integration used mocked inference. A separate real local Gemma tool turn also passed; neither proves live cloud or Telegram. |
| Email gate | Owner, recipient, exact-payload digest, expiry, replay, concurrent claims, unknown outcome and restart checks passed. | A real approved Gmail send remains pending credentials and authorization for the test message. |
| Routing | Simplicity, reasoning, long context, sticky privacy, local-down cloud fallback, and reversible simulated 429 checks passed. | Cloud inference and the deployed Tailscale path remain untested. |
| State | Concurrent writes, snapshots, restart recall, generation-conflict rejection and failed durable-commit tests passed. | GCS was mocked. Native workspace snapshot/restore tests passed, but live complete recovery and daemon identity persistence remain unverified. |
| Browser boundary | Auth, route allowlist, chunked-body limit, output validation, plain-text rendering and overload recovery passed. | Isolated Chromium login/chat/plain-text rendering/new-chat/sign-out and mobile overflow checks passed; screenshots were visually reviewed. Model responses were mocked. |
| Direct Gemma | `gemma4:e2b` completed arithmetic, reasoning and private synthetic calls; Ollama reported 65,536 context and 7,392,593,922 bytes in VRAM. | The direct three-word instruction returned two words and failed that constraint. A separate full Hermes/Gemma memory-tool turn succeeded. |
| Dependency review | Initial installed-package advisory scan reported no known vulnerabilities. | Changes after that scan require rerunning it; OS/image scan is separate. |

The direct Gemma elapsed times were 17.690 seconds (first arithmetic call, including load), 0.767 seconds (short reasoning), and 0.076 seconds (private phrase). These are single synthetic samples, not a benchmark or cloud/local comparison. No paid API calls or real account actions were made.

The real local tool turn used `gemma4:e2b` through Hermes: initial inference took 16.903 seconds, `a3_memory` completed successfully, and the following local inference took 0.568 seconds. The audit records local model/reason/outcome without message text. This is a single synthetic integration check, not a latency guarantee.

Bounded mock load checks completed 100/100 representative requests at concurrency 4 (p95 22.618 ms); stress at concurrency 32 yielded 4 successes and 252 intentional HTTP 429 rejections, followed by 10/10 recovery successes. These ASGI checks used a 20 ms fake upstream and do not measure model or cloud throughput.

**Artifact distinction:** The running local container predates the newest workspace/memory-envelope/private-network source changes. The 37-test result predates the latest network addition. Neither is evidence that the current full working tree or final release has passed every check.

## My implementation map

| Requirement areas | Current source | Remaining acceptance work |
| --- | --- | --- |
| CORE-01, CORE-04, CORE-06–11 | `runtime.py`, `routing.py`, `plugin.py`, `probe_gemma.py` | OpenAI-primary/NVIDIA-fallback migration, exact models, live cloud calls, deployed private path, live failure scenarios and comparative measurements. |
| FUNC-01–09, FEAT-01–04 | `integrations.py`, `broker.py`, `plugin.py`, `seed_jobs.py` | Connect class-only services; verify schedules, delivered briefing/weather/recap, unsolicited alert and OAuth refresh. |
| SEC-01–08 | Container profile, bounded API, allowlisted tools, approval ledger, security tests | Image scan, live access tests, complete injection evaluation and final audit. |
| OPS-01–03 | `state.py`, `durability.py` | Live dedicated GCS bucket; complete native transcript/cron/background-writer recovery and crash evidence. |
| USER-08–11, USER-15 | Docker sandbox, UI, locked dependencies, Git workflow | Latest-source container rebuild, CI execution and reviewed source push. Earlier container and browser checks passed. |
| CORE-02/05, OPS-04–10, platform access, video, reports, ADV choices | Architecture and requirements baseline | Cloud project/budget, Tailscale, release approval, genuine 48-hour evidence, published skill integration, video and submission artifacts. |

## My provider clarification checkpoint

I selected OpenAI or Claude as primary and NVIDIA as fallback. My working design uses OpenAI API primary; Claude remains an allowed alternative. The current source still has a NVIDIA-only cloud adapter. Model IDs, budget, adapter/configuration migration, fallback/simulation tests and live evidence remain pending. My key availability does not authorize paid calls. [CLARIFICATIONS.md](CLARIFICATIONS.md) records the professor's NIM reliability warning and final-model evidence rules.

My four skills require real integration evidence: own scoped Google accounts, direct Tavily access and an original content workflow. A bundled search wrapper would not qualify. No class-only credentials or live sends have been exercised.

## My open release blockers

I still need the GCP project ID and spending limit, class-only integration credentials, and private Tailscale configuration. My [setup guide](SETUP.md) explains the account preparation. I have not reused Assignment 2's cloud project or personal data. NVIDIA/Tavily setting names were identified there, but their credentials have not been copied or exercised.

My custom SQLite state has generation-fenced checkpoints; native workspace capture/restore has mocked test coverage. Live complete recovery, persistent Tailscale identity and current-image integration remain unfinished. The alert deduplication currently records an alert before confirmed Telegram delivery; delivery-failure recovery needs strengthening. Scheduled jobs are defined but not installed into a live authenticated gateway. Content drafts are stored and deduplicated; visual draft-review controls and the public skill-tap installation evidence remain unfinished.

The 48-hour observation window has not started. Q07 describes grader checks after End Date (deadline + 2) and again 48 hours later. Q09 requires new final-model logs/video after a primary change; Q10 allows minor non-model fixes without a new full run. Q11 prohibits planned grading restarts and warns of restart penalties. My November 17, 11:59 PM deadline and unknown grace balance remain distinct. Local checks cannot replace real availability or deliverables.

## My dependency and source record

I use Python 3.14.10 in `python:3.14-slim-bookworm`, pinned by digest, and a SHA-256-verified Hermes v0.22.7 archive. Hermes requires an editable source installation; its wheel build intentionally fails. Its declared uv compatibility overrides resolve the Pillow/browser-harness conflict without downgrading the security-patched Pillow version. My root `uv.lock` records resolved versions. Linux is the execution target; Android dependencies are excluded through an explicit psutil override.

The original PDFs and all 19 supplied files remain unchanged. My proxy/UI are newly authored implementations informed by the starter protocol and its recorded findings. Codex assisted with source generation, integration review and tests; I remain responsible for reviewing and understanding the submission.
