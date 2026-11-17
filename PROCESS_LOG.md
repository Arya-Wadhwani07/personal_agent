# My Development Process Log

## My implementation narrative

I am building a class-only personal assistant with Hermes, Telegram, Gmail, a dedicated Google Calendar and a small browser interface. My first step was to preserve the supplied course materials and organize the assignment into 94 traceable requirements. I selected a content-research and drafting workflow as my fourth skill, with no automatic social publishing.

Codex assisted with requirements interpretation, architecture, source generation and testing. All application authoring and execution took place in approved Docker containers, with project-scoped mounts and disposable test state. I kept credentials and runtime data out of Git.

The implementation separates the public browser edge, native Hermes gateway and internal policy service. Email drafts require exact-payload human approval in Telegram. Routing considers task complexity and privacy, while persistent privacy records prevent a compacted conversation from silently moving to a cloud model.

My provider selection changed from an API-key proposal to supported Hermes OpenAI browser OAuth after I asked for another assignment check. Hermes now owns authentication and refresh; the routing proxy forwards its authenticated requests. A real synthetic comparison completed on gpt-6.1-sol. Google consent, refresh and dedicated-calendar reads also passed, and I confirmed a Telegram reply.

The latest isolated suite passed 94 tests. Browser interactions, static analysis and package advisory checks provided additional evidence within their stated limits. Cloud deployment, live cloud OAuth recovery, live fallback, final reports and the Zoom video remain unfinished. I will record actual operating evidence rather than treat local tests as a completed 48-hour run.

I installed Tailscale and signed into my own tailnet. An isolated permitted client reached Gemma while an excluded client was blocked; I also completed a separate cloud OAuth sign-in. Containerized Google Cloud sign-in verified project access and billing. Codex tightened release checks to bind the project and $4 ceiling; these checks do not impose a billing hard cap.

## My change and evidence record

| Stage | Work and attribution | Evidence or limit |
| --- | --- | --- |
| Documentation baseline | Codex-assisted source inventory, requirement/rubric mapping, design and architecture; I supplied decisions and reviewed guardrails. | Five PDFs and 19 extracted files reviewed; 25 original hashes unchanged. |
| Isolated implementation | Codex generated the policy, routing, integration, state, UI, runtime and CI source with my authorization. | Docker-only authoring; offline white-box, integration and gateway tests. |
| Model verification | Local Gemma direct/full-tool checks; Hermes browser OAuth with gpt-6.1-sol. | Genuine local and OAuth samples; no paid API inference. |
| Account setup | I enabled Google APIs, added the test user, completed browser consents, supplied the dedicated calendar and recipient, and sent Telegram /start. | Google refresh/calendar access verified; I confirmed a Telegram reply. |
| Regression/security review | Codex added failure/replay/privacy/recovery tests, UI checks and bounded-response controls. | 68 tests passed in 23.57 seconds; Ruff/Bandit passed; package scan found no known advisories in scanned packages. |
| Private networking and cloud auth | I supplied the temporary tailnet token and completed cloud browser consent; Codex applied/reviewed the restricted policy and added native credential persistence. | Allowed/denied network probes passed, temporary admin token revoked; 94 offline tests passed, live cloud recovery pending. |
| Release preparation | I completed owned-tailnet and Cloud CLI sign-in; Codex verified access and tightened release authorization. | 82 tests passed in 21.98 seconds; no provisioning or paid inference. |
| Clarification review | I supplied professor Q&A and confirmed both accounts are dedicated class-only. | Q01–Q14 mapped; grader-access rehearsal and private submission remain pending. |

## My reflection and remaining evidence

My required personal reflection is still pending my own input; Codex has not invented what I learned or felt. I will add my two or three reflection sentences and the final deployment, operating-window, report and video evidence before submission. Private authentication records and raw transcripts are not attached to this public log.

### November 17 technical checkpoint

With Codex assistance, I added project-scoped cloud provisioning, keyless GitHub trust, pinned Secret Manager versions, persistent request quotas, patched runtime libraries and an evidence-based image gate. Live GCS state/OAuth recovery checks passed. The Tailscale build adapts upstream's version-stamping instructions; SQLite and ACL use checksum-verified upstream sources. ACL tests required Bash and a container-specific device-denial expectation, while retaining their permission assertions. My personal reflection and final-length submission edit remain deferred as requested.

## November 17: federation and first-start recovery

With Codex assistance, I used the non-secret GitHub identity diagnostic to identify the exact rejected subject condition, updated the project-scoped provider and checked the saved policy without broadening its restrictions. I also corrected default-profile initialization after restoring a preflight snapshot. My isolated regression suite passed 165 tests in 21.07 seconds. Cloud publication/deployment and the actual observation window still require their own successful evidence.
