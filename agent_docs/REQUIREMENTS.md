# My Assignment 3 Requirements

Status: my Codex-assisted requirements baseline, [rough design](DESIGN.md), [system architecture](ARCHITECTURE.md), and [security register](SECURITY_REGISTER.md) are ready for my review. The architecture maps all 94 requirement IDs to components, policies, alternatives, and evidence gates; it includes the content-drafting skill and continuous security checks. Application implementation, automated security scanning, pipeline configuration, and deployment have not started. My [extracted-script review](SCRIPT_REVIEW.md) is complete and has identified two source-level security findings to address before adopting the Hermes proxy. My named GitHub destination and routine commit/push workflow are now authorized under USER-15.

Last updated: November 16, 2026.

## 1. Purpose and scope

My project is a proactive personal AI assistant using **Hermes or OpenClaw**, hosted on **Google Cloud Run Instances**, with a cloud LLM and **local Gemma 4 through Ollama on my hardware**, connected through **Tailscale**. The assistant integrates messaging, tools, persistent memory, and autonomous scheduled/event-driven behavior. The assignment provides the project concept, while the synthetic persona, integrations, and feature details are mine to choose. [D pp. 1-4]

I use this document to track assignment obligations, conditional options, source conflicts, acceptance evidence, and my workflow constraints. Requirement capture is not evidence that a feature has been implemented or tested. All application acceptance checks below are **planned, not run**.

### Source register

Page references use physical PDF pages, counted from 1. Archive paths are relative to `Assignment3_local_Gemma_scripts/` inside the supplied ZIP.

| Key | Source | Scope and authority |
| --- | --- | --- |
| D | [Assignment_3_Description.pdf](../docs/Assignment_3_Description.pdf), 20 pages | Main requirements, rubric, deliverables, and academic-integrity rules. |
| G | [Assignment3_local_Gemma.pdf](../docs/Assignment3_local_Gemma.pdf), 31 pages | Specific grader-access and video instructions; explicitly replaces the original video duration. |
| V | [Assignment3_Video_Instructions.pdf](../docs/Assignment3_Video_Instructions.pdf), 6 pages | Zoom recording, device identification, MP4 naming, and upload instructions. |
| S | [Assignment_3_Setup_Recommendations.pdf](../docs/Assignment_3_Setup_Recommendations.pdf), 23 pages | Setup and troubleshooting guidance; p. 1 explicitly says it introduces no additional requirements. |
| R | [Deployment_Reference.pdf](../docs/Deployment_Reference.pdf), 23 pages | Optional infrastructure examples; pp. 1 and 23 say the description/rubric controls grading. Examples are not a complete tested solution. |
| Z | [Assignment3_local_Gemma_scripts.zip](../docs/Assignment3_local_Gemma_scripts.zip), 19 files | Copyable companions to G: Hermes web UI/startup, OpenClaw access setup, routing-log commands, recording prompts, and private submission template. Read without executing. |
| U | My instructions in this chat; [AGENTS.md](AGENTS.md) | Project boundaries, approvals, naming, documentation maintenance, and testing expectations. |

Classification: **Required** applies to everyone; **Conditional** applies to a selected platform, integration, claim, or accommodation; **Choose** identifies a required choice among alternatives; **Recommended** is source guidance rather than an added grading floor; **Optional** is elective; **User** is a project workflow constraint.

The assignment-specific platform versions, model examples, and prices remain source guidance rather than live guarantees. The rough design separately cites official documentation checked for container/virtual-environment boundaries, Telegram interactions, GitHub deployment controls, and Cloud Run Instances. Before implementation, I will verify the exact selected versions and accounts; the design review does not establish that my environment works.

## 2. Core architecture and hybrid routing

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| CORE-01 | Choose | My assistant will use one of OpenClaw or Hermes as the assistant platform. | Selected platform, effective runtime version, configuration, and working gateway. | D pp. 1-2 |
| CORE-02 | Required | My agent, orchestration, and scheduler will run on a long-running Google Cloud Run **Instance**, not a request-driven Cloud Run Service. My deployment commands will use the `gcloud beta run instances` resource family. | My deployed resource type, image, startup command, port, restart behavior, and health inspection. | D pp. 10-13 |
| CORE-03 | Choose | For cloud inference, I will configure a suitable model through NVIDIA NIM or the platform's supported OpenAI/ChatGPT OAuth path. My configuration record must identify the provider, exact model ID, and authentication method. Both are permitted; D recommends OAuth. | A completed real inference from the deployed agent with the configured account/model. | D pp. 2, 5-6 |
| CORE-04 | Required | My local route will use a Gemma 4 variant through Ollama on my own laptop/desktop. E2B is accepted with no size-only penalty; llama.cpp alone does not satisfy Ollama integration. | Exact installed tag, actual local inference through the deployed agent, `ollama list` and `ollama ps`. | D pp. 2, 6-7 |
| CORE-05 | Required | My design must connect the cloud agent to local Ollama privately through Tailscale userspace networking/proxy support. My inference client must actually use that path; gateway binding alone is insufficient. | Completed cloud-to-laptop inference and responding model identity, alongside network configuration. | D pp. 11-13 |
| CORE-06 | Required | My router must make task-aware decisions based on properties such as simplicity, reasoning depth, privacy, context length, or rate-limit state. Both cloud and local routes must execute for full hybrid credit. | Deterministic routing tests, live calls, logs, and comparison across at least three task types. | D pp. 7-8, 19 |
| CORE-07 | Required | My implementation needs a documented, reversible way to simulate cloud rate limiting without exhausting actual quota; demonstrate local fallback and its routing log. | Controlled flag/config/mock HTTP 429 test, local result, and successful removal of the injected condition. | D p. 8 |
| CORE-08 | Required | My assistant must keep answering cloud-eligible tasks when local Gemma is unavailable or the laptop is off. | Live non-private request succeeds through cloud with Ollama unavailable. | G p. 2 |
| CORE-09 | Choose | For private tasks when local inference is unavailable, I can either hold the request without sending it to any model or use cloud fallback. The policy belongs in my README and must match enforcement/logging. | Local-down test proves the selected policy; no unsupported privacy claims. | G pp. 2, 23-27 |
| CORE-10 | Required | My router must write Cloud Logging evidence for every request: time, local/cloud/held route, rule/reason, actual model, and success/failure. **My routing logs must not include message text.** A chosen route is not proof that inference completed. | My final-response/model-call review, request timestamp correlation, and log-content leakage check. | D pp. 7-8; G pp. 2, 21-23, 27 |
| CORE-11 | Required | My agent/tool prompts need a configured and verified Ollama context window. For Hermes, the assignment calls for at least 64K; my checks must cover the chosen release's requirement and `ollama ps`. My thinking/output budget needs a deliberate setting and an explanation in the report. | Full tool-using agent turn without context truncation or empty output; served context and thinking setting in performance report. | D pp. 7, 10; R pp. 13-14 |
| CORE-12 | Conditional | If my hardware cannot run even Gemma 4 E2B functionally, I will document the limitation in the Personalization Profile and discuss the cloud-only accommodation. It cannot demonstrate full hybrid operation and may reduce routing credit. | Hardware/context evidence and explicitly documented accommodation; never claim local execution that did not occur. | D pp. 10, 19 |

## 3. Skills, messaging, and proactive behavior

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| FUNC-01 | Required | My messaging interface must integrate at least one of **Telegram or Discord** with working incoming requests and delivered replies. | Live message/reply through the deployed agent and demo video. | D pp. 2, 8, 16; G p. 27 |
| FUNC-02 | Required | My assistant must provide and exercise at least **four skills**: calendar, email, web search, and at least one additional meaningful skill. The fourth can be installed or created; originality is required only for the publication option. | Skill inventory plus working tool invocations visible in the demo or verifiable through the deployed agent. | D pp. 2, 20 |
| FUNC-03 | Required | My implementation must cover at least **four of the six advanced features** below. Appropriate proactive features must execute by schedule or event without a user prompt. | Feature-to-test mapping, useful results from synthetic test accounts, trigger/execution/delivery evidence. | D pp. 3-4, 19 |
| FUNC-04 | Required | My proactive behavior will use cron, heartbeat, or an appropriate event trigger. Scheduled polling counts as event-driven for this assignment; a continuous `sleep()` polling loop does not. Push events such as IMAP IDLE are accepted. | Scheduler configuration and autonomous trigger/execution logs. | D pp. 3-4, 13 |
| FUNC-05 | Required | My demo must show a morning briefing, an end-of-day recap, and at least one proactive alert **regardless of the four-feature selection**. | All three are actually delivered in the video, following the run-now allowances below. | D p. 4; G pp. 28-29 |
| FUNC-06 | Required | My integrations must use a dedicated temporary email account and a dedicated temporary **Google Calendar**, with synthetic messages/events only. Gmail is not mandatory. | Sanitized account/integration configuration and synthetic fixtures; no personal or USC inbox/calendar connection. | D pp. 3, 8-9 |
| FUNC-07 | Required | My documentation must identify the email provider, authentication, capabilities, and send controls. Every email send needs explicit human approval enforced in code plus a recipient allowlist; unattended jobs draft and notify instead. | Unapproved send denied, approved permitted send scoped to allowed test recipients, disallowed recipient denied, and unattended job completes without sending/hanging. | D pp. 2-3, 8-9 |
| FUNC-08 | Required | My morning briefing must include weather, with the integration documented in my README. No particular weather vendor/plugin is mandated. | Delivered briefing with weather from the selected integration. | D pp. 3, 9-10 |
| FUNC-09 | Conditional | If I use Google APIs, I will enable needed APIs, configure consent and dedicated-account authorization, request narrow necessary scopes, verify draft permissions separately, test refresh during the 48-hour run, and assess applicable verification requirements. OAuth scopes alone do not enforce read/draft-only behavior. | Auth/refresh and read/draft tests, scope inventory, code-enforced approval gate. | D pp. 8-9 |

### Six-feature menu

My fourth-skill recommendation is **LinkedIn Content Brief**, specified in DESIGN.md section 3 and USER-14. It adds daily topic selection, source-backed drafting, and review history on top of the separate web-search skill. This proposed custom skill does not replace the requirement to implement four features from the menu below or automatically satisfy the advanced-integration criterion.

Each row applies if I select that feature, except the independent demo obligation in FUNC-05. My selection is still pending.

| ID | Feature | Required behavior when selected | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| FEAT-01 | Morning briefing | My briefing would arrive every morning on a schedule I choose, with today's events and gaps, local weather, and one-line summaries of top unread/flagged emails. The delivery format is my choice. News and assignment-deadline reminders are optional. | Schedule fires and delivers current integrated content; run-now video invokes the scheduled job. | D p. 3; G p. 28 |
| FEAT-02 | End-of-day recap | My evening recap would summarize actual tasks completed/messages handled, items needing review/decisions, and tomorrow's early meetings or approaching deadlines. | Scheduled recap grounded in activity logs; video can run the scheduled job early. | D p. 3; G p. 28 |
| FEAT-03 | Email integration | My email feature would summarize incoming messages on request or proactively, draft replies for review, and flag urgent messages. My assistant must never send without explicit human approval. | Synthetic inbox, summary, draft, urgency flag, and approval-control tests. | D pp. 3-4 |
| FEAT-04 | Proactive alerts | My alert feature would deliver context-aware notifications from schedules or observed events without waiting for me to ask. Meeting reminder, deadline/repository alert, and unanswered urgent email are examples, not three mandatory alert types. | A fresh synthetic trigger in my test setup, followed by an unsolicited alert and trigger/execution evidence. | D p. 4; G pp. 24, 28 |
| FEAT-05 | Calendar intelligence | My calendar feature would go beyond reading events by detecting conflicts, suggesting task-appropriate slots from gaps, and preparing meeting context from prior test emails/documents. | Synthetic conflicting events, slot suggestions, and context preparation examples. | D p. 4 |
| FEAT-06 | Personal knowledge base | My knowledge base would learn non-sensitive synthetic preferences, fictional people/projects, and workflow information over time, with persistence in workspace files. | A new synthetic fact in my test setup, its stored representation, and recall across sessions/restarts. | D p. 4 |

News, if chosen, needs a documented source/integration; news itself is optional. No independent cron job is required for every calendar-intelligence or knowledge-base feature. [D pp. 4, 10]

## 4. Memory, deployment, and continuous operation

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| OPS-01 | Required | My durable storage must use a dedicated Cloud Storage bucket for durable workspace/memory. Container-local state alone is insufficient. My platform must use the actual persistent paths. | Bucket/mount configuration, runtime permissions, and observed writes. | D pp. 11-13, 20 |
| OPS-02 | Required | My assistant must retain memory across sessions and agent restarts. My initial synthetic personalization belongs in these workspace files: OpenClaw `SOUL.md`, `USER.md`, `IDENTITY.md`; Hermes corresponding personality/context/memory files. | New fact stored durably, instance restart, new conversation recalls it from restored state. | D pp. 2-3, 11, 13, 16, 20 |
| OPS-03 | Required | My design must specify and document concurrent-write safety for scheduled tasks, messaging handlers, and any background memory writers. My design cannot assume Cloud Storage FUSE or local locks make shared updates transactional. | Concurrent update/restart tests for the selected single-writer, version-aware, journal, or equivalent strategy. | D p. 14 |
| OPS-04 | Required | My deployment needs a supported Instance region, compatible container/runtime, port, startup/restart behavior, stable authorized HTTPS access, and necessary APIs/permissions. | My deployed-setting inspection and verified gateway, tools, and both inference paths. | D pp. 11-13 |
| OPS-05 | Recommended | The recommended starting point for my deployment is 1 vCPU and 1 GiB, with more memory when needed, including 2 GiB for OpenClaw. My report must explain the memory allocation. These are starting allocations, not hard caps. | My selected allocation and measured workload/peak usage in the report. | D p. 11; R pp. 3-4 |
| OPS-06 | Required | My operational evidence must demonstrate **48 hours of continuous operation** with evidence throughout the window, not just start/end screenshots. A crash at hour 30 needing manual restart does not establish an uninterrupted 48-hour run. | Timestamped availability, messaging, scheduling, and lifecycle evidence spanning the complete interval. | D pp. 14, 16, 20 |
| OPS-07 | Required | My logs must record starts, crashes, restarts, scheduled executions, message handling, routing decisions, model failures, genuine outages, and missed jobs. Automatic managed-platform restarts can be acceptable when state and normal work recover; preserve proof. | Lifecycle record, recovery/state restoration, resumed jobs, and explicit gaps/missed-job analysis. | D p. 14 |
| OPS-08 | Required | Before my observation window starts, I will choose durable evidence storage and arrange a prompt export afterward. My evidence must retain the actual recorded time bounds. | Sanitized export covering the run, backed by Cloud Logging/bucket/job history; no reconstruction of a fictitious start time. | D p. 14; S pp. 21-22 |
| OPS-09 | Recommended | For reliability, I will consider combining bounded connectivity recovery with a separately configured clean restart schedule every three hours; verify state, messaging, jobs, and inference recover without lost/duplicate execution. A cooldown is not a restart schedule. | Pre-window controlled failure/restart tests, recovery logs, and documented decision whether to adopt this guidance. | D p. 14; S pp. 6, 12; R p. 8 |
| OPS-10 | Required | My submitted agent must stay running and unchanged until regrades close, with independent access even when I am absent or my laptop is off. I will avoid manually restarting or redeploying it during grading; see source ambiguity below about automatic planned restarts. | External access and laptop-off smoke tests before submission; preserve frozen configuration/evidence. | G pp. 20, 30-31 |

## 5. Security and data restrictions

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| SEC-01 | Required | My deployment must use Docker or equivalent container isolation. My audit must explain its boundaries and remaining agent access. If interactive shell access is unavailable, a timestamped startup runtime-user/capabilities report plus container configuration and audit is accepted. | Container configuration, startup isolation evidence, and audit. | D p. 2; R p. 19 |
| SEC-02 | Required | My security evidence must demonstrate at least **two security measures**, with container isolation counting as one. Additional menu choices: input validation/prompt-injection defense, permission scoping, credential management. | My mapping of implemented controls to the menu and verification results. | D pp. 2-3, 19 |
| SEC-03 | Required | My platform/application code must enforce explicit human approval for every email send, along with a recipient allowlist. LLM/guardian approval, prose instructions, or OAuth scopes alone are insufficient. | Positive/negative send tests, bypass attempts through available tools, and documented approval path. | D pp. 2-3, 9 |
| SEC-04 | Required | My connected services must use only throwaway class-only accounts and made-up data for email, calendar, messaging, and other connected services. No actual personal/sensitive personalization data; graders receive broad chat/tool access. | Test-data review and connected-account inventory. | D pp. 3, 9, 16; G pp. 2, 16, 20 |
| SEC-05 | Required | My real credentials must stay out of source, ordinary configuration, Git, images, README, video, logs, and shared archives. My `.env.example` must contain placeholders; grader secrets go privately through Brightspace. Secure runtime storage is required; Secret Manager is generally recommended and specified for G's access keys. | Secret-handling/configuration review and sanitized packaging/build-context checks. | D pp. 2-3, 12, 16, 19; G pp. 14, 17, 20, 29-30; S p. 7 |
| SEC-06 | Required | My local Ollama endpoint must remain restricted to authorized private access, without public or unintended LAN exposure. | Authorized deployed-agent success plus unauthorized/LAN rejection checks. | D p. 13; R pp. 5-6 |
| SEC-07 | Required | My submission needs a security audit with a threat model identifying **at least five risks**, implemented mitigations, and unmitigated residual risks with rationale. My audit must cover isolation, additional measures, the send gate, and recipient allowlist. | Audit-to-implementation traceability and reproducible security checks. | D pp. 2-3, 16, 19 |
| SEC-08 | Conditional | If I claim prompt-injection defense, my evaluation must test **at least three distinct attempted attacks** and document pass/fail. Graders may plant a test email. | Attack fixtures and observed outcomes; include incoming email/calendar/web content and memory risks as appropriate. | D pp. 16, 19; G p. 30 |

My [SECURITY_REGISTER.md](SECURITY_REGISTER.md) tracks implementation risks and observed findings under USER-13. Its initial risks and proposed mitigations are unverified; no security scan has run. It will inform the final SEC-07 audit, with actual results and residual risks preserved. My engineering target is no known unresolved release-blocking vulnerabilities, not an unsupported guarantee of zero vulnerabilities.

## 6. Advanced integration: choose one for the base 10%

This is separate from the four advanced features and the fourth skill. It is part of the base 100%, not extra credit. Completing more than one option earns no additional credit. [D p. 20]

| ID | Class | Option and obligations | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| ADV-01 | Choose | One option is to publish an original skill I develop: OpenClaw uses ClawHub; Hermes may use a public GitHub skill-tap repository, ClawHub, or skills.sh. My evidence would include the public location and pinned version/commit. For Hermes, my evidence would include a fresh-install installation/execution transcript; installation directly from a `SKILL.md` URL is not accepted. | Public pinned artifact plus clean-install/run evidence; attribute reused material. Publication requires my separate authorization. | D p. 20; S pp. 9-10 |
| ADV-02 | Choose | Another option is to connect my assistant to another student's independently developed personal assistant through A2A. We would exchange synthetic test messages while each implementing and submitting our own code and evidence. | Demonstrated cross-assistant request/result and independent implementation evidence. | D pp. 17, 20 |
| ADV-03 | Choose | My third option is to integrate **three or more messaging platforms simultaneously** with unified persistent memory and cross-platform context continuity. At least one Telegram/Discord integration is still required. A single Hermes home is sufficient only if channels truly share its persistent memory. | Three-service Bluebird exchange below; persistence tests and working additional services. | D pp. 8, 20; G pp. 27-28 |

## 7. Platform-specific grader access

Only the branch for my chosen platform will apply. I will adapt example ports and IDs to my deployment rather than copying placeholder cloud identifiers or secrets.

### Hermes branch

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| HERMES-01 | Conditional | If I choose Hermes, my deployment must expose browser chat at the Cloud Run URL through the supplied `web_ui.py` reverse-proxy pattern: external `$PORT` (8080 by default), internal Hermes API on `127.0.0.1:$HERMES_PORT` (8081 by default); forward `/v1/*` and `/health`. | Chrome opens chat, health works, authenticated chat produces a complete reply. | G pp. 3-13; Z `Hermes/web_ui.py`, `api_server.env` |
| HERMES-02 | Conditional | My Hermes image must include the UI, and its startup process must supervise both UI and gateway; shut down both on termination and fail/restart if either dies. My changes must preserve existing state, Tailscale, scheduler, and shutdown behavior. If I use Tailscale Serve, it must point to the UI. | Startup, subprocess failure, graceful termination, and recovery checks. | G pp. 11-13; Z `Hermes/start-agent.sh`, `Dockerfile_snippets.txt`, `tailscale_serve.sh` |
| HERMES-03 | Conditional | My Hermes deployment must supply `API_SERVER_KEY` securely through Secret Manager/runtime injection, never image `ENV`. Hermes requires at least **16 characters**; the supplied generator produces a longer random key. I will submit the key privately after verifying external authentication. | Missing/wrong-key rejection and valid-key chat; key not visible in assets or recording. | D p. 16; G pp. 14-16; Z `Hermes/api_server_key.sh` |
| HERMES-04 | Conditional | Because the supplied web UI has no approval buttons, my Hermes implementation must block approval-gated tools in API-server sessions and explain draft/messaging alternatives. Human approval must remain available on Telegram/Discord. | Web send request returns a block promptly without hanging; messaging request still shows approval controls. | G pp. 14-16; Z `Hermes/approval_hook_example.py` |

### OpenClaw branch

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| OPENCLAW-01 | Conditional | If I choose OpenClaw, my graders need an HTTPS Tailscale Serve dashboard link using MagicDNS/certificates and accepted Tailscale identity, without gateway-token entry or device-pairing intervention. | Chrome opens dashboard directly through the intended shared identity. | G pp. 16-20 |
| OPENCLAW-02 | Conditional | My access policy must restrict shared graders to agent TCP **443**. Agent-to-laptop Ollama TCP **11434** needs a separate grant. Only my agent machine may be shared, never my laptop; existing broad grants also need review. | Access policy and reachability tests for permitted/forbidden destinations. | G pp. 16-17, 20; Z `OpenClaw/tailscale_acl_example.hujson` |
| OPENCLAW-03 | Conditional | My OpenClaw deployment must use a reusable, tagged, **non-ephemeral** Tailscale auth key valid through grading (guide maximum: 90 days). My deployment must load the latest key version from Secret Manager as prescribed by this guide. My daemon identity must persist in the Cloud Storage-backed state path rather than `--state=mem:`. | Restart retains machine name/identity and existing grader URL; auth key not exposed. | G pp. 17-18; Z `OpenClaw/tailscale_authkey_secret.sh`, `tailscaled_state.sh` |
| OPENCLAW-04 | Conditional | My OpenClaw access setup needs HTTPS Serve to gateway, working default Tailscale socket access for identity lookup, writable socket directory for container user, `gateway.auth.allowTailscale=true`, and exact HTTPS allowed origin without trailing slash. My configuration must be validated and restarted before grading. | Config validation, startup/Serve logs, working identity recognition and post-restart dashboard. | G pp. 18-20; Z `OpenClaw/openclaw_config.sh`, `openclaw_json_result.txt`, `tailscale_serve_gateway.sh`, `Dockerfile_snippet.txt` |
| OPENCLAW-05 | Conditional | Near submission, I will create a reusable machine-share invitation; unused links expire after **30 days**. My invitation and agent URL go privately to the grader, with expired invitations replaced when needed. | Reusable share setup and pre-submission access check; keep access through regrades. | G p. 20 |

### Test-account access for either platform

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| ACCESS-01 | Required | My private Brightspace submission must provide dedicated test email/calendar account logins, including a separate calendar login if needed, so graders can plant a meeting and, if applicable, injection email. Hermes: Cloud Run URL and API server key. OpenClaw: Tailscale share link and agent URL. | My completed private Brightspace Comments template, with no secret values in project Markdown. | G pp. 29-30; Z `CloudRunSettings.txt` |
| ACCESS-02 | Conditional | For my disposable class-only accounts, I will follow the guide's access paths: preferred Path 1 uses password-only with 2-Step Verification off when no Google App Password is needed; Path 2 for Gmail App Passwords keeps 2-Step Verification on, removes Authenticator if added, and supplies at least **four unused backup codes**. These instructions are only for disposable assignment accounts. | My grader-style login test in an Incognito window of a different browser, excluding consumed codes and retaining four unused codes for Path 2. | G p. 30; Z `CloudRunSettings.txt` |
| ACCESS-03 | Conditional | My authorization plan needs to account for Google OAuth Testing-mode refresh-token expiry after **seven days**; refresh authorization near grading or follow an appropriate Production setup. I must not regenerate submitted backup codes or change passwords after submission. If I retain the accounts, I will rotate credentials after grading. | Token lifetime/reauthorization plan, external login test, and post-grading cleanup plan. | D pp. 9, 16; G pp. 30-31; Z `CloudRunSettings.txt` |

## 8. Video requirements and exact demonstration sequence

Graders do not independently test my local Gemma path; G identifies the video as the evidence of deployed-agent-to-laptop inference, local outage behavior, and the private-task policy. Direct laptop-only inference does not establish this path. [G p. 23]

| ID | Class | Requirement | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| VIDEO-01 | Required | My demo must be **one MP4**, recorded using a Zoom meeting and full desktop sharing. Audio is optional. My recording must begin with the Windows Product ID or macOS Hardware UUID, followed by the deployed platform's actual version from startup logs or Hermes health; Dockerfile intent alone is insufficient. | My final recording review for identity, runtime version, desktop visibility, and all steps below. | V pp. 1-6; G p. 25 |
| VIDEO-02 | Required | My complete video must stay within **12 minutes maximum**. G explicitly replaces D's original 5-7 minute requirement; this is not an additional second video. | Media duration and one final recording. | G pp. 23, 28-29 |
| VIDEO-03 | Required | For my routing demonstration, all four requests must go through the **deployed cloud agent's web chat/dashboard**, rather than directly to laptop Ollama. My recording must capture complete replies or the permitted held error. | Four requests, shutdown/recovery sequence, and matching successful final-call logs except held requests. | G pp. 23-27 |
| VIDEO-04 | Required | My video must show routing logs for the last **30 minutes**, **newest first**, with time, route, reason, model, and outcome, without message text. Query uses `--freshness=30m --order=desc`; actual field names may differ. | Readable log output correlated to all four requests; held request has no model call. | G pp. 21-23, 26-27; Z both `routing_log.sh` files |
| VIDEO-05 | Required | My local-model evidence must show installed Gemma via `ollama list`, and after the final local request show it loaded via `ollama ps`. OpenClaw also shows laptop `tailscale serve status` exposing TCP 11434 to loopback Ollama. | Visible terminal evidence in recording. | G pp. 25, 27 |
| VIDEO-06 | Required | My video must capture a real-time messaging reply, delivered morning briefing, unsolicited proactive alert, and delivered end-of-day recap. Briefing/recap may invoke the actual scheduled job's run-now option; asking for a briefing in chat is insufficient. Recap reflects actual activity. | Delivered messages and trigger/job evidence in recording. | D p. 16; G pp. 27-29 |
| VIDEO-07 | Required | My recording must keep API keys, tokens, share links, `.env` files, and other secrets off screen. With Hermes, I will save the key beforehand. No cloud-agent restarts or redeploys are allowed during my recording. | Full video review before submission. | G pp. 24, 28 |
| VIDEO-08 | Required | My video must be named `Assignment3-CSCI599-USCusername.mp4`, with my USC username substituted, and uploaded to Brightspace Assignment #3. My private access details belong in Comments. | Correct filename and upload checklist, subject to packaging clarification below. | V p. 6; G p. 29 |

### Recording sequence

The prompts below are supplied test data, not my private information. [G pp. 24-28; Z both `Video_Steps.txt` files]

| Step | Action | Expected evidence |
| --- | --- | --- |
| 1 | My opening shot will show the device Product ID/Hardware UUID. | Device identification at the beginning. |
| 2 | Next, I will show the deployed Hermes/OpenClaw version. | Runtime log or supported health response. |
| 3 | My local setup check will show `ollama list`; with OpenClaw, I will also show `tailscale serve status`. | Installed Gemma and applicable private exposure. |
| 4 | With Ollama on, my first prompt will be `What is 12 times 9?` | Local Gemma answers 108. |
| 5 | For the cloud route, I will send `Explain step by step why the sky is blue.` | Cloud model returns a complete explanation. |
| 6 | After quitting Ollama, I will run `curl -s -m 3 http://127.0.0.1:11434/api/tags \|\| echo "Ollama is off"` and wait for router detection. | Local service unavailable, with my health signal shown if available. |
| 7 | My local-outage prompt will be `This is confidential: remind me my locker code is on a sticky note.` | Hold with no model call, or cloud response, matching README policy. |
| 8 | I will restart Ollama, run `ollama list`, and wait for router recovery. | Local availability restored. |
| 9 | To check the restored local route, I will send `This is confidential: say "back online" in three words.` | Local Gemma gives a complete response, e.g. `Back online now.` |
| 10 | My prepared Cloud Logging query will identify the routes and outcomes of all four requests. | Local -> cloud -> held/cloud -> local; actual model/final outcomes and matching times. |
| 11 | I will run `ollama ps` to show the loaded local model. | Gemma still loaded on the laptop. |
| 12 | My desktop Telegram/Discord exchange will use `Hi, what can you do?`; if I choose ADV-03, I will use the cross-service exchange below instead. | Working messaging reply, or shared-memory proof on all claimed platforms. |
| 13 | My recording will capture the scheduled morning briefing arriving, using run-now if necessary. | Current test-calendar, weather, and email content at documented destination. |
| 14 | The next evidence will be my proactive alert arriving without a request. | For example, a timed test-calendar meeting reminder. |
| 15 | My recap demonstration will show scheduled delivery, using run-now if necessary. | Recap includes actual agent activity. |
| 16 | Finally, I will stop recording, end the Zoom meeting, let MP4 conversion finish, and apply the required filename. | Single complete video within 12 minutes. |

If I choose ADV-03, I will show the applications side by side on my recorded desktop and use a fact that is not already in my profile or memory:

1. Service 1: `Remember that my fictional project is called Bluebird and is due Friday.`
2. Service 2: `What is my fictional project called, and when is it due?` Expected: Bluebird, Friday.
3. Service 3: `Which app did I tell you about Bluebird on?` Expected: service 1.
4. On each additional service I claim, I will repeat the service-2 question.

Before recording, I will check that my cloud agent answers in Chrome, my laptop is awake/powered with Ollama and Tailscale available, authorization is fresh, the log query works, messaging is on the recorded desktop, and no secrets are visible. My alert needs to arrive during steps 13-15; the guide suggests creating a meeting about 35-40 minutes before recording for a 30-minute reminder. My rehearsal will cover job run-now and local-off/on detection. The guide's approximate 30-second health detection and 45-second model load are examples, not performance SLAs. [G pp. 24-29]

## 9. Submission, reports, and academic integrity

| ID | Class | Required deliverable or rule | Planned acceptance evidence | Source |
| --- | --- | --- | --- | --- |
| SUB-01 | Required | My Brightspace submission must contain a project ZIP named `firstname_lastname_a3.zip`, with standard layout and root `README.md`. The PDFs defer the deadline to the course schedule; I have now confirmed November 17, 2026, at 11:59 PM in chat, with timezone/grace details tracked in USER-12. | Archive inventory and README run/setup/deployment instructions sufficient for TA verification. | D pp. 15-16, 20; U |
| SUB-02 | Required | My source package must include complete source, platform configuration, created/installed skills, routing logic, scheduling, and container/deployment configuration; use `.env.example` placeholders. | Reproducible sanitized source package and setup review. | D p. 16 |
| SUB-03 | Required | My deployment evidence must include the Instance HTTPS URL, full 48-hour evidence, and Cloud Storage persistence configuration evidence; protect private access credentials separately. | Timestamp coverage, resource/persistence evidence, and private access checklist. | D p. 16 |
| SUB-04 | Required | My security audit must meet SEC-07/08. | At least five risks, implemented/residual mitigations, send approval/allowlist, isolation, and conditional attack results. | D pp. 16, 19 |
| SUB-05 | Required | My performance report must compare cloud and local inference for **at least three routed task types**: response time, output quality, cost analysis, routing decisions, and evidence those decisions were correct. My report must record actual latency, relevant context/thinking settings, hardware limits, and the deployment memory-allocation rationale. | Measured full-agent-turn results, justified quality assessment, and cost assumptions distinguished from actual charges/entitlements. | D pp. 7, 10-11, 16, 19 |
| SUB-06 | Required | My submission must include a Personalization Profile and the corresponding synthetic workspace/context files. | Platform-specific files with meaningful synthetic customization and any hardware accommodation. | D pp. 10, 16, 20 |
| SUB-07 | Required | My root **`PROCESS_LOG.md`** must include a list of every AI tool/model used, with versions where known; a chronological **200-300 word** development narrative with material prompts; substantial AI-code attribution by file/function/module; verification beyond merely running; and **2-3 sentences** on what I learned and had to solve. | Content and word-count review; an accurate process history and my understanding, written in my own voice. | D pp. 17-18 |
| SUB-08 | Required | My submission must include the complete demo and evidence for my selected advanced integration. Submission handling of the MP4 versus ZIP needs confirmation below. | Video checklist plus publication/A2A/multi-platform evidence. | D pp. 16, 20; V p. 6 |
| INTEGRITY-01 | Required | This is my individual assignment: I cannot share source, configuration, or custom skills with other students. AI assistance is allowed and expected, but I remain responsible for understanding the work. A2A permits independent assistants to exchange test messages, not share implementations. | Honest Process Log, independent source/deliverables, and explanations I have reviewed. | D p. 17 |
| INTEGRITY-02 | Required | My attribution must identify copied or substantially adapted external code in **code comments and Process Log**, using `Adapted from <source URL> - <one-line rationale>` (comment syntax adapted to language). My README must attribute framework forks, while routing, security, personalization, and custom skills remain my own implementation with disclosed assistance. | Attribution review of starter/framework/external code and process entries. | D p. 17 |
| POLICY-01 | Required | My submission follows the course-canonical late/regrade policy: two grace days across assignments, **30% penalty** after grace days are exhausted, regrade window closes **two days after the Brightspace form is posted**. My deadline is November 17 at 11:59 PM; its timezone and my remaining grace balance still need confirmation. | My confirmed course schedule, timezone, and remaining grace balance before final submission planning. | D p. 20; U |

My root `README.md` now provides the repository overview and documentation index; runnable setup instructions remain pending. My other proposed artifact names (not yet created) are root `PROCESS_LOG.md`; `agent_docs/SECURITY_AUDIT.md`, `PERFORMANCE_REPORT.md`, and `PERSONALIZATION_PROFILE.md`; sanitized evidence under an approved evidence directory. Platform-required workspace and skill files stay in their required runtime locations. These are layout proposals, not extra assignment deliverables.

## 10. Rubric coverage

| Criterion | Weight | Requirement coverage | Evidence needed for full credit |
| --- | --- | --- | --- |
| Hybrid routing correctness and intelligence | 20% | CORE-03 through CORE-12, SUB-05, VIDEO-03/04/05 | Task-aware decisions, completed local/cloud calls, inspectable logs, three-task comparison. |
| Proactive features and quality | 15% | FUNC-03/04/05, FEAT-01 through FEAT-06 | At least four features, autonomous triggers, useful integrated test-account content. |
| Security implementation and audit | 15% | SEC-01 through SEC-08, FUNC-07, SUB-04 | Isolation plus another measure, five-risk threat model, protected credentials, conditional three-attack evaluation. |
| Skill integration and utility | 15% | FUNC-01/02/06/08/09 | Four working exercised skills, with meaningful fourth skill. |
| Memory, personalization, scheduling | 15% | OPS-01/02/03/06/07/08, SUB-06 | Durable bucket memory, restart recall, real scheduling, complete 48-hour evidence. |
| Code quality, documentation, demo | 10% | SUB-01 through SUB-08, VIDEO-01 through VIDEO-08, INTEGRITY-01/02 | Readable working code, usable README, complete truthful Process Log and demo. |
| One advanced integration | 10% | ADV-01 or ADV-02 or ADV-03 | One fully evidenced option; no extra credit for multiple options. |
| **Total** | **100%** | All applicable requirements | All evidence remains pending implementation. |

Source: D pp. 18-20. Consequential grading failures include dead/trivial routing, no completed model evidence, fewer than four features, manual-only proactive behavior, absent isolation/security, exposed keys, unexercised skills, lost restart memory, and an incomplete/poorly evidenced 48-hour run. Hardware accommodation does not establish full hybrid credit.

## 11. Source precedence, ambiguities, and recommendations

### Resolved differences and unresolved questions

| Topic | Source difference | Handling |
| --- | --- | --- |
| Video duration | D p. 16 says 5-7 minutes; G p. 23 explicitly replaces this with one video up to 12 minutes. | My recording will follow the complete G procedure and 12-minute maximum. |
| ZIP versus separate MP4 | D pp. 15-16 requests a single ZIP including deliverables; V p. 6 explicitly instructs uploading the named MP4 to Brightspace. | I will retain both instructions until I confirm whether Brightspace expects the MP4 inside the ZIP, separately alongside it, or both. No second video is needed. |
| Private task/local outage | S p. 20 recommends keeping private tasks private; G pp. 2, 23 permits either holding or cloud fallback. | The explicit G choice governs my design; my documented policy and actual behavior must agree. |
| Tailscale identity | R pp. 7-8 illustrates in-memory/ephemeral cloud identity; G pp. 17-20 requires persistent non-ephemeral identity for OpenClaw grader URLs. | If I choose OpenClaw, my grader-access setup must use G's persistent identity. |
| Hermes Python versions | S p. 10 and R p. 12 refer to older Hermes requiring Python below 3.14; G pp. 1-2 says v0.22.7 requires Python 3.14. | These describe different pinned releases. My chosen release needs its own runtime/dependency check; older working versions are allowed. |
| OpenClaw runtime/configuration | G p. 2 gives Node >=24.22.1 shorthand; S pp. 12-13 gives tested ranges >=24.22.1 and <25, or >=26.12.1, and version-dependent config keys. | My runtime choice needs verification against the exact pinned release; not every Node 24/26 version is compatible. |
| Scheduled restarts versus grading freeze | D p. 14 recommends three-hour restarts during long operation; G p. 31 says no restarts/redeploys during grading. | I will avoid manual restarts/redeploys during grading. Whether preconfigured preventive restarts should be disabled before submission still needs clarification. |
| Four features versus video | D p. 4 allows four of six but separately requires briefing, recap, and alert demonstrations. | My plan needs all three demonstrated behaviors regardless of which four features I select. |
| Context and model size | Any Gemma 4 size is accepted; platform context requirements and actual available RAM still constrain operation. | E2B is valid, but my model choice still needs a real agent-turn/context measurement; a successful download does not prove it fits. |
| Gemma tags in video instructions | D pp. 6-7 accepts any Gemma 4, including a larger 26B variant; G pp. 24-27 names E2B/E4B in the video steps. | E2B/E4B are unambiguous choices. If I select another permitted Gemma 4 variant, I will confirm the video adaptation without narrowing D's model allowance. |
| Markdown locations | I want agent documentation under `agent_docs/`; D requires root `PROCESS_LOG.md` and README. | My planning documents belong under `agent_docs/`; submission/runtime files follow assignment or tooling locations. |
| Recording output path | V p. 6 describes Zoom's default `Documents/Zoom`; my permission limits changes to Assignment 3. | My recording output must stay inside Assignment 3 where supported. Any external write or hardware-UUID inspection needs my separate authorization before the recording step. |
| Deadline, platform, actual services | Files do not give a calendar due date or choose my integrations/model/platform. I confirmed November 17, 2026, at 11:59 PM in chat. | My timezone/grace balance and implementation choices still need confirmation. Credentials stay out of tracked Markdown. |

### Setup and infrastructure guidance retained for implementation

These are recommendations or implementation cautions, not new grading floors. They support the required outcomes above. No commands from the supplied archive have been executed.

| Topic | Guidance to apply when relevant | Sources |
| --- | --- | --- |
| Setup order | My setup sequence will pin the platform/runtime/dependencies, run synthetic checks, verify cloud/local calls, configure temporary integrations and private networking, create resources before dependent secrets, deploy, test persistence/outages, and complete a preliminary soak before the 48-hour window. | S p. 1 |
| Version evidence | My version record will include the platform, language runtime, dependency lock, image tag/digest, Ollama version, and model tag. G's tested releases are Hermes v0.22.7 and OpenClaw 2026.10.9; older releases may work. Hermes release tags and PyPI can differ; runtime version output may contain an older display date. | S pp. 2, 10-14; G pp. 1-2, 25 |
| Cloud models/auth | My cloud checks will use exact account-supported IDs, including separate general/reasoning roles if configured. Error handling needs bounded retries for 404/429/provider failures and errors inside successful HTTP streams. My laptop/cloud OAuth sign-ins must be independent, with refreshed credentials preserved; ChatGPT OAuth is not an ordinary API key. | D pp. 5-8; S pp. 2-3, 11-12, 17-18 |
| Local model behavior | My local-model evaluation will measure full tool turns, cold/warm latency, context, processor/offload, and memory. Ollama needs restarting after server environment changes. A restricted tool catalog, deliberate thinking mode, and optional keep-alive/preload are choices I will evaluate. OpenClaw reference uses 32,768 context; Hermes reference 65,536, not universal interchangeable defaults. | D pp. 7, 10; S pp. 3-4, 12-15; R pp. 10, 13-14 |
| Networking | For my private inference path, the recommended setup is loopback Ollama plus Tailscale Serve, never public Funnel. My checks need effective grants, real LAN rejection, and proxied tags/inference rather than online/ping status alone. Only the local model client should use the proxy, with SOCKS on loopback and consistent writable socket paths. | S pp. 4-6, 15; R pp. 5-11 |
| Recovery | My recovery design should confirm transport failure before bounded repair, preferring daemon repair before container restart. A known offline laptop or missing model is not a networking-repair trigger. Post-repair inference and records of network changes/offline periods belong in my checks. | S pp. 6, 12, 21; R pp. 6-8 |
| Integrations | My integration checks need actual provider auth/IMAP/SMTP/IDLE support and synthetic events with current timestamps/timezone. Private calendar ICS URLs are secrets. If I choose Telegram, setup includes starting the bot, numeric user allowlists, and one long-polling consumer per token. | S pp. 6-7, 18 |
| Cloud identities/build | My deployment plan must distinguish deployer, builder, and runtime identities. Scoped source-bucket/image-repository/log permissions belong to the actual build identity; a verified build/image comes before deployment. Region and CLI checks must be specific to Instances. | S pp. 2, 7-9; R pp. 3, 17-19 |
| Storage | My storage design should keep active SQLite and atomic-rename/lock-dependent state on local container disk with consistent durable snapshots/restore where required. My review will cover background writers, mount ownership/private modes, usability, and preservation of unrelated volumes during redeploy. | S pp. 8-9, 16-19; R pp. 14-16 |
| Scheduling | My scheduler needs an explicit timezone and separate checks for job completion/delivery and a fresh event path. Review will also cover quiet hours, deferrals, deduplication, startup baselining, idempotent registration, background heartbeat, memory review/flush/dreaming, and quota use. | S pp. 9, 16-19; R pp. 10, 13 |
| Approval safety | My approval checks must inspect the effective exec policy. Default execution or classifier `auto` approval is not human approval, and broad shell/interpreter/mail-CLI allowlists must not bypass my send gate. Scheduled jobs must not wait for approval. | S pp. 15-16; G pp. 14-16 |
| Secure gateway | If I choose OpenClaw, G's grader-specific Tailscale identity path governs access. Generic setup may require recognized device approval and secure WebSockets; broadly disabling authentication is not an acceptable fix for pairing issues in my deployment. | S pp. 19-20; G pp. 16-20 |
| Observation window | My controlled tests must finish before the observation window. When local inference is expected, my laptop needs power and wakefulness. I will avoid unplanned changes, record UTC bounds and scheduler timezone, retain lifecycle/job/delivery/backup outcomes, export promptly, sanitize evidence, and exclude private backups from submission. | S pp. 20-22; R pp. 19-20 |
| Cost and cleanup | D describes a $50 education credit and possible two additional $50 coupons, plus an illustrative $5.70/month base estimate. These are not a total-cost guarantee or spending authorization. My actual costs/entitlements need later validation; grading access must remain available until regrades close before I authorize cleanup. | D pp. 4-5; S p. 22; G pp. 30-31 |

## 12. Project workflow and verification plan

| ID | Class | My workflow requirement | Application |
| --- | --- | --- | --- |
| USER-01 | User | My project writes stay inside Assignment 3. The one read-only Assignment 2 structure inspection I allowed is complete. | Codex needs my permission for external filesystem access or global installation. My temporary/cache outputs stay inside the project. |
| USER-02 | User | I review and approve each coherent change set, with verification reported afterward and a checkpoint before the next scope. | I have approved documentation creation and updates; implementation/deployment is not authorized. |
| USER-03 | User | My project Markdown filenames use uppercase names, alongside standard tooling conventions. | My files use `AGENTS.md`, `REQUIREMENTS.md`, `README.md`, and future `PROCESS_LOG.md`, with lowercase directories such as `agent_docs/`. Original and tooling-required names are preserved. |
| USER-04 | User | My Markdown stays current as changes occur. | My affected requirements, plans, status, setup/run instructions, reports, and process history are synchronized within each approved change set, rather than deferred to final cleanup. |
| USER-05 | User | My review process requires appropriate SDLC testing for every change, including UI, unit, integration, smoke, load, and stress checks where applicable. | My verification record must distinguish results, failures, deferrals, and justified not-applicable checks. I will agree workload/resource/cost limits before load/stress runs. |
| USER-06 | User | I use Codex as an expert Agentic AI engineering and testing collaborator, targeting 100/100 through complete applicable rubric coverage and continuous data/code review. | My review needs requirement-to-code-to-test-to-evidence traceability, correctness/security checks across synthetic data, outputs, state, and logs, and explicit gaps and grading risks. The role in AGENTS.md supports my understanding; completion needs evidence. The instructor determines the final grade, and my target does not expand authorization. |
| USER-07 | User | My project Markdown uses a natural first-person voice, with varied phrasing and clear explanations rather than repetitive declarations. | The writing rule in AGENTS.md applies to existing and future Markdown. My plans stay distinct from completed work; actual AI assistance, source attribution, commands, prompts, and technical requirements remain accurate. |
| USER-08 | User | My application development and runtime tests must run in an approved isolated environment without accessing unrelated local/system data. | A container/VM boundary with project-scoped source, synthetic fixtures, disposable state, controlled network/credentials, and no personal host mounts. A Python virtual environment alone is insufficient. Local Docker host-side writes, remote provisioning, and source transfer need explicit approval. |
| USER-09 | User | My sandbox tests must include white-box and black-box approaches. | Internal policy/branch/error-path tests plus observable UI/API/messaging behavior checks. Unit, integration, smoke, UI, load, stress, and regression remain applicable categories; mock and live results are distinguished. |
| USER-10 | User | My project needs a GitHub CI/CD workflow and a traceable SDLC process so deployment is verified early. | Proposed automatic sandbox validation, trusted immutable builds, approved Instance releases, readiness/smoke checks, recovery records, and a deployment freeze during the real 48-hour run and grading. The repository destination and routine commits/pushes are authorized under USER-15; Actions configuration, deployment credentials, and workflow implementation remain pending. |
| USER-11 | User | My rough design must explain the required interfaces and propose an easy-to-use neumorphic UI. | DESIGN.md includes architecture, a chat wireframe, states, accessibility goals, and Telegram/Discord integration. The required messaging channel and platform-specific browser grader interface are both retained; a custom dashboard and WhatsApp are not assumed requirements. |
| USER-12 | User | My confirmed submission deadline is November 17, 2026, at 11:59 PM, and I intend to use available grace days if needed. | My planning timezone is America/Los_Angeles pending confirmation; the number of remaining grace days is unknown. The plan reserves a genuine 48-hour operational window plus final-delivery time after readiness, without promising that CI/CD removes this constraint. |
| USER-13 | User | My development process must continuously identify, track, remediate, and retest security vulnerabilities before release. | SECURITY_REGISTER.md separates risks from findings and records affected artifacts, severity, evidence, ownership, fixes, and retests. Applicable code/dependency/secret/image/configuration and sandbox behavioral checks gate releases; unresolved Critical/High or behavior-based blockers and incomplete required checks stop release. Permitted lower-severity residual risks need my explicit recorded decision. |
| USER-14 | User | My proposed fourth skill should support a daily original LinkedIn-oriented content draft that I can review, with the aim of supporting outreach. | LinkedIn Content Brief researches permitted sources, selects relevant nonduplicate topics, preserves provenance, drafts in a configured voice, and delivers to my review channel with persistent history. Assignment data remains synthetic; no direct LinkedIn search, personal-account access, or publishing in the initial scope. Approved API access would be a separate future decision. Outreach improvement is a goal, not a promised result. |
| USER-15 | User | My reviewed, coherent changes must be committed and pushed to [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent) so I can trace and recover earlier versions. | Project-local Git identity/configuration, explicit staging, appropriate checks, descriptive commits, and verified pushes; synchronize Markdown before each commit. No force-push/history rewrite or deployment is implied. Supplied course materials, secrets and generated/private state are excluded from the initial baseline; repository visibility/protections need verification before application publication. |

### Alignment with my design proposal

My [DESIGN.md](DESIGN.md) translates these requirements into a rough implementation plan. My [ARCHITECTURE.md](ARCHITECTURE.md) adds component and technology reasoning, five system/sequence/state diagrams, and a [complete requirement map](ARCHITECTURE.md#a15-requirement-by-requirement-architecture-coverage) covering every existing ID. Its sections A4-A11 define interface, routing, tool approval, scheduling, persistence, security, runtime, and delivery boundaries; A12-A14 cover evidence, alternatives and verification. I have authorized its preparation and documentation updates, not the proposed platform selection, sandbox provisioning, CI/CD configuration, or deployment. My later USER-15 authorization covers repository connection and reviewed commits/pushes. My existing requirement IDs remain stable.

| Requirement coverage | Design location | Evidence needed before I consider it implemented |
| --- | --- | --- |
| USER-08: isolated development/testing | Section 7: development and testing sandbox | Verified filesystem, privilege, network, credential, resource, and cleanup boundaries; only approved source and synthetic fixtures exposed. No unrelated host data or unapproved Docker host-side writes. |
| USER-09: white-box and black-box testing | Section 8: testing plan | Internal policy/branch/error-path results plus observable UI/API/messaging results from the approved sandbox, with mocks and live dependencies identified. |
| USER-10: CI/CD and SDLC | Sections 9-10: delivery workflow and milestones | Working GitHub checks, trusted immutable build, explicit release authorization, correct Instance deployment, readiness/live smoke results, recovery procedure, and a tested deployment freeze. All are currently planned. |
| USER-11; FUNC-01; HERMES-01/04 or OPENCLAW-01; VIDEO-03: interfaces | Sections 2, 5-6: required surfaces, UI concept, and messaging | Working Telegram/Discord plus the selected browser grader interface; readable neumorphic styling where approved; keyboard/loading/error checks; no unsupported browser approval controls. WhatsApp alone is insufficient, and the browser does not count as an extra messaging platform. |
| USER-12; OPS-06/08/10: deadline and evidence | Sections 1, 9, 11: timing, release freeze, and decisions | Confirmed timezone/grace balance, stable-release readiness, genuine 48-hour logs, export/submission buffer, and continued grader access. No shortened or simulated uptime claim. |
| USER-13; SEC-01 through SEC-08: security tracking | Section 8 security review, section 9 release workflow, and SECURITY_REGISTER.md | Current scoped scans/reviews/tests tied to the candidate artifact, triaged findings, fixes with retests, no unresolved blockers, and documented permitted residual risks. No runtime controls are verified yet; SCRIPT_REVIEW.md and SECURITY_REGISTER.md record the manual starter-code findings and their planned tests. |
| USER-14; FUNC-02; conditional ADV-01: fourth skill | Section 3 content-skill contract and section 5 draft-card UI | Research/draft/provenance/deduplication and scheduled-delivery checks, source-injection and no-publishing tests, synthetic data, and separate fresh-install/publication evidence only if I select ADV-01. |

Hermes + Telegram + a small neumorphic browser chat remains my proposed starting point, now with LinkedIn Content Brief as the fourth-skill recommendation. Platform selection, the content-skill scope/preferences, remote sandbox, private-task hold policy, and advanced integration remain design decisions. Approval and verification status must be updated together across my Markdown as those decisions become concrete.

### Planned test matrix

| Test category | Planned coverage | Current status |
| --- | --- | --- |
| Requirements/document review | Source coverage, mandatory/optional distinctions, exact thresholds, precedence, IDs, links, stale status, and original-file integrity. | Codex review completed for this documentation change; my review pending. |
| Unit | Routing properties/precedence, local-down/private behavior, reversible 429 simulation, send/recipient policy, scheduling calculations, summaries/validation boundaries, memory update rules. | Deferred until implementation; no runtime code exists. |
| Integration | Cloud auth, deployed Tailscale/Ollama calls, chosen tools, messaging, bucket persistence/restore, approval UI, concurrent writes, selected advanced integration. | Deferred until implementation and authorized service setup. |
| Smoke | Container/gateway readiness, authorized grader chat, message reply, cloud response with laptop off, basic local inference, scheduled job run-now. | Deferred until a runnable deployment exists. |
| UI review | Selected web/dashboard access, authentication, chat/error/loading states, approval behavior, responsive usability, and future UI changes I request. | Not applicable to this Markdown-only change; pending UI implementation. |
| Security/adversarial | Access/session isolation, approval bypasses, recipient restrictions, secrets, URL fetching, XSS, sandbox/network access, and at least three attacks if claiming injection defense. | Initial risks and two manually observed starter-code findings recorded in SECURITY_REGISTER.md; all runtime checks pending. |
| Load | Representative simultaneous messaging, scheduled work, model calls, memory writes; latency, errors, resource use, and duplicates/loss. | Deferred; workload, duration, budget, and target not yet agreed. |
| Stress | Bounded resource pressure, model/network loss, provider faults, process failure/restart, memory safety and recovery. | Deferred; no live disruption authorized. |
| Performance | Local/cloud measurements across at least three task types; quality and cost evidence with full-turn context. | Deferred until both inference paths work. |
| Soak/reliability | Preliminary soak followed by genuine 48-hour observation with durable interval-wide evidence. | Not started; cannot be replaced by short tests. |
| Regression/final acceptance | My affected checks repeated after approved fixes, followed by a submission audit against all applicable IDs and video/access requirements. | Pending implementation. |
| White-box | Internal routing/approval policies, branches, state transitions, retry/error handling, and memory consistency, using the approved sandbox. | Planned in DESIGN.md; sandbox and application do not yet exist. |
| Black-box | Supported UI/API/messaging contracts, success/error/denial cases, delivery, and restart behavior using synthetic sandbox data; authorized live verification separately. | Planned in DESIGN.md; no runtime checks performed. |
| CI/CD validation | Workflow/configuration review, isolated tests, required security scans, finding triage/retests, trusted build provenance, deployment approval/freeze, Instance readiness, and compatible rollback. | Repository destination selected and Git baseline authorized; scanners, Actions and cloud delivery remain unconfigured. |
| Content skill | Relevant dated sources, supported claims, original draft, duplicate-topic history, missing/stale/conflicting data, schedule idempotence, source injection, safe rendering/fetching, and no publishing or personal-account access. | Proposed contract only; no skill code or social integration exists. |

The PDFs specify no universal throughput, latency percentile, stress duration, test-count target, or code-coverage percentage. I will agree useful engineering targets before testing, without inventing grading requirements. Reference test counts (e.g. 45/46 passes), example tool counts, account-specific model IDs, and observed startup/model-load times are not requirements for this implementation.

## 13. Source coverage and second-pass review

My source review with Codex covered all **103 PDF pages**, which were text-extracted and read. The image-based Zoom/device instructions and rubric table were additionally rendered and visually inspected. All **19 archive files** were read without execution, including the `.env` template and `.hujson` access-policy example. PDF line wrapping was not treated as executable source syntax; Z provides intact script counterparts.

| Source sections | Coverage in this baseline | Review status |
| --- | --- | --- |
| D pp. 1-4: objective, platforms, floors, features, restrictions | CORE, FUNC, FEAT, SEC | Read and cross-checked. |
| D pp. 5-10: model/auth paths, routing, messaging, Google, weather, hardware | CORE, FUNC, ACCESS, recommendations | Read and cross-checked. |
| D pp. 11-15: deployment, storage, networking, scheduling, operation, concurrency | OPS, SEC, recommendations | Read and cross-checked. |
| D pp. 16-18: deliverables, integrity, Process Log, weights | SUB, INTEGRITY, rubric | Read and cross-checked; weight table visually checked. |
| D pp. 19-20: detailed rubric, advanced integration, late/regrade | CORE/FUNC/SEC/OPS, ADV, POLICY | Read and cross-checked. |
| G pp. 1-2: versions and universal deployment requirements | CORE-08/09/10, SEC-04, version guidance | Read and cross-checked. |
| G pp. 3-16: Hermes UI, startup, key, approval behavior | HERMES branch | Read and cross-checked against Z. |
| G pp. 16-20: OpenClaw identity/access and persistence | OPENCLAW branch | Read and cross-checked against Z. |
| G pp. 21-23: routing log fields/query | CORE-10, VIDEO-04 | Read and cross-checked against Z. |
| G pp. 23-29: replacement video, exact steps, common mistakes | VIDEO and sequence | Read and cross-checked against V and Z. |
| G pp. 29-31: private submission/accounts and grading availability | ACCESS, OPS-10, unresolved restart question | Read and cross-checked against Z. |
| V pp. 1-6: identity, Zoom, full desktop, MP4 naming/upload | VIDEO, packaging/output-path questions | Read and visually reviewed. |
| S pp. 1-9: shared setup, privacy, recovery, identities, tests | Recommendations and test plan | Read and cross-checked; explicitly advisory. |
| S pp. 10-19: Hermes/OpenClaw version-specific setup | Recommendations, platform branches, version conflicts | Read and cross-checked; examples not treated as project requirements. |
| S pp. 20-23: pre-run checklist, evidence, troubleshooting/references | OPS, test plan, guidance | Read and cross-checked. |
| R pp. 1-8: optional architecture, local model, Tailscale | CORE/OPS guidance, ephemeral-identity conflict | Read and cross-checked. |
| R pp. 9-16: platform paths, context, storage/concurrency | CORE/OPS guidance and storage caution | Read and cross-checked. |
| R pp. 17-23: deployment, verification, mistakes/references | OPS, test plan, guidance | Read and cross-checked; optional status preserved. |
| Z: `CloudRunSettings.txt`; Hermes 9 files; OpenClaw 9 files | ACCESS, HERMES, OPENCLAW, VIDEO, source attribution | All 19 read; no scripts executed or installed. |

Second-pass checks: minimum counts/durations and all seven rubric weights reconciled; all six feature options and three advanced-integration options represented; both grader-access branches retained; video override and unresolved packaging/restart issues recorded; recommendations separated from obligations; no unverified implementation/test claims. My six original source files remain unchanged, as verified by Codex using SHA-256 before/after the review.

## 14. Decisions and proposed next steps

I have not yet selected a platform, model, project persona, fourth skill, feature set, or advanced integration.

My [rough design](DESIGN.md) now proposes a small Hermes browser chat with neumorphic styling, Telegram delivery, LinkedIn Content Brief, a sandbox boundary, continuous security tracking, and controlled GitHub CI/CD. These choices remain open for review. I confirmed November 17, 2026, at 11:59 PM as the deadline; timezone and remaining grace days still need confirmation. My detailed [architecture](ARCHITECTURE.md) is now prepared for review. It proposes original content-skill publication for the advanced-integration criterion, without selecting or authorizing it, and identifies the framework-hook, storage-consistency, account and environment decisions that must be resolved before implementation.

1. **Requirements review.** My next step is to resolve the interpretation questions and confirm the grace balance/timezone, leaving enough time for the real 48-hour run and delivery buffer.
2. **Design choices.** I still need to confirm laptop RAM/model feasibility, Hermes versus OpenClaw, cloud provider/auth, Telegram versus Discord, dedicated test email/calendar path, private-task outage policy, fourth skill, at least four features, and one advanced integration.
3. **Implementation plan.** My rough design and detailed architecture need approval and concrete choices for the sandbox host, GitHub visibility/protection settings, synthetic persona, scheduler timezone/times/delivery destinations, threat model, test criteria, cost limits, and report locations. Morning briefing, end-of-day recap, email integration, and proactive alerts are a possible feature combination; I have not selected it yet.
4. **Incremental development.** Once approved, my implementation can progress through platform/configuration and synthetic tests, routing, tools/approval controls, memory/scheduling, and grader UI/access. Related Markdown will stay current with each change.
5. **External setup.** Account creation/authentication, model downloads, installations, cloud resources/deployment, messaging, publication, and filesystem access beyond Assignment 3 each need my explicit authorization before execution.
6. **Validation and observation.** My real integration, security, persistence, controlled recovery, applicable load/stress checks, and preliminary soak come before the genuine 48-hour run and durable evidence collection.
7. **Deliverables and submission.** My final review will cover truthful reports/Process Log, the prescribed video, grader access, and packaging. Submission needs my approval, and grading access must remain available until regrades close.

### Extracted-script implementation alignment

My [SCRIPT_REVIEW.md](SCRIPT_REVIEW.md) records per-file evidence and adaptations. All 94 existing IDs remain stable; these are implementation constraints, not new grading floors.

| Existing requirements | Source-specific refinement | Evidence required later |
| --- | --- | --- |
| HERMES-01/03; USER-11; CORE-10/11 | Preserve the actual Bearer/non-streaming chat contract; the gateway model label is not serving-model identity. Browser history is not persistent memory and health HTTP success is not authenticated/model readiness. | API/session isolation, complete nonempty reply, truthful status, bounded history and actual-model routing records. |
| HERMES-01; SEC-05/07; USER-13 | Proxy forwarding exceeds the documented minimum paths; source-level body/response/thread handling is unbounded and log construction unsafe. | Resolve VULN-001/002; route/auth coverage, resource bounds, loopback-only proxy routing and structured redacted errors/logs. |
| HERMES-04; FUNC-07; SEC-03 | The approval hook has undefined placeholders and no implemented registration/trusted platform mapping. | Verified framework hook, unknown-session denial, prompt browser block and real messaging approval with allowlist/replay protection. |
| HERMES-02; OPS-01/02/03/04 | Startup is a minimal supervisor, not the full state/Tailscale/readiness lifecycle; its process watch is distinct from proactive scheduling. | Restore-before-work, valid loopback/ports, child-failure and bounded shutdown tests; complete memory/daemon writer inventory. |
| OPENCLAW-02/03/04 | Config/socket/key/state files are fragments or mutually exclusive alternatives; daemon identity writes are separate from memory writes. | Complete grants, exact origin/user/socket/port, one persistent daemon, secret injection and stable post-restart identity. |
| CORE-10; VIDEO-01 through VIDEO-07; ACCESS-01/02/03 | Query scripts do not emit routing events; video companions omit PDF steps, including OpenClaw Serve status. | Resource-scoped sufficient log rows, canonical PDF-derived sequence, real replies/deliveries, private account access and no secret exposure. |

Source checks cover the five PDFs, ZIP and 19 extracted files without execution. Runtime, browser, adversarial and performance checks still need the approved sandbox and implementation.

### Repository and coverage review update

My repository destination is [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent); routine commits/pushes are authorized under USER-15. The architecture's [technology appendix](ARCHITECTURE.md#a17-appendix--technology-and-development-stack-overview) gives a shorter explanation of the development/runtime stack, while A2 retains the tradeoffs and references.

The current cross-check retains every previously captured assignment requirement, all seven rubric categories, the six-feature menu, three advanced-integration options, both access branches, video/report/account obligations, and the 48-hour window. No new missing source obligation was identified against the existing 103-page/19-file baseline. This is a baseline-to-design review, not a new extraction of the PDFs or a claim that implementation is complete.

The unresolved items remain concrete: platform/runtime/model fit, provider and account access, sandbox and repository protections, test/resource limits, timezone/grace balance, MP4 packaging and preventive-restart interpretation. Implementation, CI/CD execution, live integrations, runtime/security tests, reports, video and 48-hour evidence are still outstanding. My authorized follow-up review has now read all 19 extracted starter files and confirmed byte identity with the ZIP. SCRIPT_REVIEW.md records the incomplete hook/setup fragments, proxy/UI differences, two source-level findings and implementation/test steps. No starter code has been executed or modified.

## Change history

| Date | Change | Verification |
| --- | --- | --- |
| 2026-11-16 | My initial Codex-assisted baseline brought together five PDFs and the starter archive, with source references, conflicts, evidence, rubric coverage, decisions, and the documentation-maintenance rule. | Codex source review and structural checks; application tests not yet applicable. |
| 2026-11-16 | I requested the engineering/testing role and full-credit target. Codex added USER-06 and synchronized AGENTS.md. | Codex checked the then-current 85 unique IDs, consistency, links, and Markdown structure; runtime tests not applicable. |
| 2026-11-16 | I requested a natural first-person voice throughout my Markdown. Codex revised both documents and added USER-07 while preserving source obligations, attribution, and pending-work status. | Wording review, 86 unique IDs, preserved source references/technical details, valid links/tables, and unchanged source files; runtime tests not applicable. |
| 2026-11-16 | I requested a rough design, neumorphic UI, sandbox-only development/testing, white-box/black-box checks, and GitHub CI/CD. Codex created DESIGN.md and added USER-08 through USER-12, including my confirmed deadline. | Document review and cross-file consistency checks; 91 unique IDs. Runtime tests, pipeline execution, and external setup remain unperformed. |
| 2026-11-16 | I requested synchronization with DESIGN.md. Codex added the design-to-requirement evidence map and clarified that document preparation does not approve implementation choices or external setup. | Existing 91 IDs preserved; design references, tables, links, and pending-work wording reviewed. Runtime testing remains not applicable to this documentation change. |
| 2026-11-16 | I requested vulnerability tracking and a daily LinkedIn content skill. Codex added USER-13/14, created SECURITY_REGISTER.md, and synchronized the design, UI, testing, and release gates across my Markdown. | 93 unique requirement IDs; documented source/access limits and no-publishing scope; no scans, skill execution, social-account actions, or architecture-file creation. |
| 2026-11-16 | I requested the complete system architecture, diagrams, references and technology justification. Codex created ARCHITECTURE.md and synchronized all affected Markdown. | All 93 IDs retained and individually mapped; conditional options and evidence gates preserved. Documentation review only; no application code, provisioning, graphical rendering or runtime testing. |
| 2026-11-16 | I supplied the GitHub repository and requested regular commits/pushes plus a technology overview appendix. Codex added USER-15, updated the architecture map and synchronized the repository documentation. | 94 stable IDs including all previous 93; baseline coverage and staging checks; no new PDF extraction, extracted-script inspection or runtime tests. |
| 2026-11-16 | I requested the extracted-script review. Codex read all 19 files and recorded source-specific adaptation steps and VULN-001/002, synchronizing the plans and README. | 19 byte-identical ZIP members; 94 IDs retained; original/extracted sources unchanged; static review only, no script execution or automated scan. |
