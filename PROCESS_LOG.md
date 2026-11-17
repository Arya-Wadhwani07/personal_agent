# Monday — My Development Process Log

I built Monday as an individual assignment with AI assistance. I chose the requirements, accounts, constraints and review priorities; Codex helped draft, debug and test the implementation. This log reflects my own account of what I learned, with technical details checked against the repository.

## 1. AI tools and models I used

| Tool or model | How I used it | Version or limit |
| --- | --- | --- |
| OpenAI Codex | Requirements review, architecture, initial code drafts, debugging, tests, security review and documentation editing. | Exact coding-model version was not recorded consistently; I do not infer it from the assistant's product name. |
| OpenAI through Hermes browser OAuth | Monday's primary cloud inference and synthetic integration checks. | `gpt-6.1-sol`; this is the runtime model, not an assertion about the coding assistant. |
| Ollama with local Gemma | Local inference, tool-turn checks and the private-task route. | `gemma4:e2b`, with a verified 65,536-token context; thinking disabled for the short local path. |
| NVIDIA developer endpoint | A bounded fallback-model preflight. | `nvidia/nemotron-3-ultra-550b-a55b`; not my primary model or an additional coding assistant. |

My development account identifies Codex as the coding assistant. I have not claimed use of Claude, Copilot, Cursor or another coding tool simply because I own an API key.

## 2. Development narrative

- **First, I established the boundaries.** I asked, “You cannot be making any changes outside this Assignment 3 folder.” With Codex's help, I organized the PDFs into a requirements map, then created the design and architecture documents. Keeping those files current reduced repeated explanations and helped me manage the context and my concern about coding-assistant credits.
- **Next, I connected the services.** Tailscale and Hermes were new to me. I installed Tailscale, moved to a tailnet I controlled, completed Google and OpenAI browser consent, and connected Telegram with a dedicated calendar and test mailboxes. I asked, “I hope you know that we need to have open ai oauth as well check the assignment,” which prompted the authentication review.
- **Then, I balanced resources and cost.** I selected Gemma 4 E2B to fit my laptop's available resources. I set a $4 project spending target and used bounded provider quotas. I learned that a billing budget tracks spending rather than guaranteeing a hard cap. The cloud preparation covered storage, service identities, secrets and a reviewed release workflow; publishing an image did not mean deployment was complete.
- **Finally, I reviewed useful behavior and failure cases.** I requested sandboxed regression, integration, UI and security checks, and noticed that the Telegram briefing contained technical clutter and promotional mail. I removed those messages, while the implementation gained cleaner MarkdownV2 presentation, explicit calendar gaps and a clean local history. My LinkedIn Content Brief prepares source-backed drafts for review without posting. I use a separate release checklist for cloud acceptance, the video and genuine 48-hour evidence, so source history and later operating results stay distinguishable.

## 3. What I learned and had to resolve

Tailscale, private tailnet access rules and Hermes scheduling were new to me, and I learned how networking, authentication and orchestration fit together in a proactive assistant. I had to complete the account sign-ins, choose the resource and cost constraints, and judge whether the briefings were actually useful; the assistant could not make those personal decisions or complete my consents for me. Reviewing the promotional emails and poor formatting taught me that a working API call is only one part of a useful, safe workflow.

## 4. Problems, decisions and lessons

| Problem or concern | My decision and the resulting work | What I can claim now |
| --- | --- | --- |
| Unfamiliar private networking | I used an owned **tailnet** and restricted agent access to Ollama. | Permitted/denied private-network probes passed. This was Tailscale networking, not Telnet. |
| Laptop resource pressure | I chose **Gemma 4 E2B** rather than a larger variant and retained the required context setting. | Real local replies and a full tool turn passed. I do not claim a measured failure of a larger model that was not recorded. |
| Cloud and token spending | I requested the $4 target, finite provider quotas and OAuth as primary. | The application limits attempts; the billing budget is not a hard cap, and no measured token-cost reduction is claimed. |
| Cloud authentication and IAM | I completed browser consents and supplied account details; Codex assisted with scoped roles, separate OAuth logins and GitHub federation. | Storage/OAuth recovery and image publication passed; the live Instance is verified through the release checklist. |
| CI failed during a source download | The engineering fix added bounded retries while retaining checksum verification. | A temporary HTTP 429 no longer causes an immediate unverified workaround. |
| GitHub federation rejected the token | I supplied the diagnostic output; with Codex assistance, the exact ID-qualified subject condition was corrected. | Publication succeeded without broadening trust to unrelated repositories. |
| Telegram output was cluttered | I flagged the issue; the formatter uses native MarkdownV2, bold sections and Unicode bullets, with cron wrappers disabled. | A synthetic Telegram preview passed parsing with six bold headings. |
| Promotional mail entered a briefing | I removed promotional mail and requested cleaner summaries; the old local history was quarantined. | Current code filters unread/starred mail and routine promotion/social categories. The query uses these filters rather than a timestamp cutoff. |
| Repeating context consumed attention | I requested readable `agent_docs/` files and updates alongside implementation. | These documents preserve decisions and reduce repetition; I did not measure a token-saving percentage. |
| Outreach-oriented fourth skill | I selected LinkedIn Content Brief for permitted-source research and original drafts. | It does not scrape LinkedIn or publish posts; the deployment checklist exercises the full research-to-draft workflow. |
| Local tool call omitted a field | The live comparison exposed an incomplete nested tool schema; with Codex assistance, the schema now names required draft fields. | The original failure is retained alongside the successful real Gemma retest. |
| Deployment region and source freeze | The final guide review caught an unsupported Instance region and a helper that changed configuration after the clock started. | The target is us-west1; freezing and pushing source now precede the observation start. |
| Unused repository material | I requested a reference-based cleanup before the final release. | Two unconsumed configuration files and one unused version constant were removed; framework callbacks and operational scripts were retained. |

## 5. Substantial AI-assisted code attribution

Codex generated initial drafts and subsequent revisions of the following project modules under my direction. I do not present that implementation work as unaided hand-written code.

| Files or modules | Contribution and purpose |
| --- | --- |
| `src/personal_agent/routing.py`, `providers.py`, `oauth_proxy.py` | Task-aware routing, private-task hold, bounded provider calls and forwarding of native authenticated OAuth requests. |
| `src/personal_agent/api.py`, `broker.py`, `plugin.py`, `notifications.py` | Public/internal boundaries, narrow tools, exact human approval and Telegram integration. |
| `src/personal_agent/state.py`, `workspace.py`, `durability.py`, `auth_checkpoint.py` | Synthetic memory, approval state, generation-fenced backups and OAuth recovery. |
| `src/personal_agent/runtime.py`, `gateway_launcher.py`, `settings.py`, `network.py`, `isolation.py`, `audit.py` | Native Hermes supervision, configuration, private transport, runtime isolation and sanitized evidence. |
| `src/personal_agent/integrations.py`, `calendar_view.py`, `content_review.py` | Google/search/weather adapters, explicit free-time calculations and content provenance checks. |
| `src/personal_agent/static/` | Browser interface, safe text rendering and content-draft review controls. |
| `scripts/` and `.github/workflows/`, `Dockerfile`, `compose.yaml` | Setup, image hardening, scheduling, probes, provisioning, release and observation tooling. The specific upstream adaptation below is attributed separately. |
| `skills/linkedin-content-brief/` | My selected original skill's instructions and claim/source-review helper, developed with Codex assistance. |
| `tests/` | Generated and revised regression, boundary, integration, recovery and policy tests; mocked and live checks remain distinguished. |

### External sources and adaptations

- **Hermes framework:** [NousResearch/hermes-agent v0.22.7](https://github.com/NousResearch/hermes-agent/tree/v0.22.7), installed from pinned, checksum-verified source. I use its native gateway, scheduler, OAuth and Telegram components; I do not claim authorship of them.
- **Adapted code:** `scripts/build_tailnet.sh` — Adapted from [Tailscale's versioned build script](https://github.com/tailscale/tailscale/blob/v1.104.7/build_docker.sh) — retains version stamps while building the container dependency patch. The source comment carries the same attribution.
- **Course starter guidance:** `docs/Assignment3_local_Gemma_scripts/Hermes/` informs the browser-proxy contract, supervision and approval behavior. The original files stay unchanged; my FastAPI edge and policy code are separately implemented with Codex assistance. The supplied examples are not represented as my original code.
- **Documentation styling:** [AgenticAIThree](https://github.com/aadit11/AgenticAIThree) informed readable headings, bullets and tables only; its code and project decisions were not copied.

## 6. Verification beyond running the application

| Check | Evidence and limit |
| --- | --- |
| Requirement review | Five PDFs, 94 stable requirement IDs and an architecture map; the release checklist ties each claim to its evidence. |
| Unit and integration regression | The isolated regression results and environment are recorded in IMPLEMENTATION_STATUS.md. |
| White-box security | Negative cases cover unauthorized/changed/replayed approvals, privacy routing, response bounds, quotas, state conflicts and recovery. Three additional injected-action scenarios exercise the actual tool boundary with model interpretation simulated. |
| Black-box and UI | Native gateway/tool checks plus isolated Chromium interaction, unsafe-markup rendering, mobile layout and sign-out behavior. |
| Smoke/live checks | Local health, real Google reads, model replies, private-network access, Telegram delivery and separate storage/OAuth recovery probes. The release checklist repeats checks on the actual Instance. |
| Load and stress | Bounded mocked concurrency and recovery checks under the agreed 4-CPU/4-GiB limits. These are not measurements of live model throughput. |
| Vulnerability review | Static, package and image checks with recorded findings, fixes and expiring dispositions. Each updated native image has its own mandatory gate; I do not claim zero possible vulnerabilities. |
| Source and secret review | Tracked references, original-file hashes, Markdown links, diff review and comparison against configured secret values before publication. |

## 7. Release evidence and source freeze

My [performance report](agent_docs/PERFORMANCE_REPORT.md), [security audit](agent_docs/SECURITY_AUDIT.md) and [personalization profile](agent_docs/PERSONALIZATION_PROFILE.md) retain measured outcomes and their limits. I freeze source documentation before observation and collect the final live checks, Zoom video and 48-hour evidence separately; future results are not recorded as earlier accomplishments.

My release procedure is in [FINAL_REVIEW.md](agent_docs/FINAL_REVIEW.md). Earlier technical checkpoints remain available in [Git history](https://github.com/Arya-Wadhwani07/personal_agent/commits/main/).
