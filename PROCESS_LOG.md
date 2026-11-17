# My Development Process Log

## My implementation narrative

I am building a class-only personal assistant with Hermes, Telegram, Gmail, a dedicated Google Calendar and a small browser interface. My first step was to preserve the supplied course materials and organize the assignment into 94 traceable requirements. I selected a content-research and drafting workflow as my fourth skill, with no automatic social publishing.

Codex assisted with requirements interpretation, architecture, source generation and testing. All application authoring and execution took place in approved Docker containers, with project-scoped mounts and disposable test state. I kept credentials and runtime data out of Git.

The implementation separates the public browser edge, native Hermes gateway and internal policy service. Email drafts require exact-payload human approval in Telegram. Routing considers task complexity and privacy, while persistent privacy records prevent a compacted conversation from silently moving to a cloud model.

My provider selection changed from an API-key proposal to supported Hermes OpenAI browser OAuth after I asked for another assignment check. Hermes now owns authentication and refresh; the routing proxy forwards its authenticated requests. A real synthetic comparison completed on gpt-6.1-sol. Google consent, refresh and dedicated-calendar reads also passed, and I confirmed a Telegram reply.

The latest isolated suite passed 68 tests. Browser interactions, static analysis and package advisory checks provided additional evidence within their stated limits. Cloud deployment, Tailscale, durable cloud OAuth recovery, live fallback, final reports and the Zoom video remain unfinished. I will record actual operating evidence rather than treat local tests as a completed 48-hour run.

## My change and evidence record

| Stage | Work and attribution | Evidence or limit |
| --- | --- | --- |
| Documentation baseline | Codex-assisted source inventory, requirement/rubric mapping, design and architecture; I supplied decisions and reviewed guardrails. | Five PDFs and 19 extracted files reviewed; 25 original hashes unchanged. |
| Isolated implementation | Codex generated the policy, routing, integration, state, UI, runtime and CI source with my authorization. | Docker-only authoring; offline white-box, integration and gateway tests. |
| Model verification | Local Gemma direct/full-tool checks; Hermes browser OAuth with gpt-6.1-sol. | Genuine local and OAuth samples; no paid API inference. |
| Account setup | I enabled Google APIs, added the test user, completed browser consents, supplied the dedicated calendar and recipient, and sent Telegram /start. | Google refresh/calendar access verified; I confirmed a Telegram reply. |
| Regression/security review | Codex added failure/replay/privacy/recovery tests, UI checks and bounded-response controls. | 68 tests passed in 23.57 seconds; Ruff/Bandit passed; package scan found no known advisories in scanned packages. |
| Clarification review | I supplied professor Q&A and confirmed both accounts are dedicated class-only. | Q01–Q14 mapped; grader-access rehearsal and private submission remain pending. |

## My reflection and remaining evidence

My required personal reflection is still pending my own input; Codex has not invented what I learned or felt. I will add my two or three reflection sentences and the final deployment, operating-window, report and video evidence before submission. Private authentication records and raw transcripts are not attached to this public log.
