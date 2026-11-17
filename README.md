# Monday

I’m building **Monday**, my class-only personal assistant for CSCI 599 Assignment 3. Monday uses Hermes, replies through Telegram and browser chat, and routes work between OpenAI OAuth and local Gemma.

My test profile is **Alex Chen**, a fictional student in Los Angeles. My connected accounts must contain made-up assignment data only. After real promotional mail appeared in a briefing, I reported removing it on November 17; I also started a clean local history, with the earlier state privately quarantined outside submission evidence.

## Current status

- **Local bot:** running; I confirmed Telegram replies from both model paths.
- **Cloud image:** the earlier `ecb61d2` image passed publication; my latest presentation changes need a new native build and image gate.
- **Regression:** 177 isolated tests passed in 22.50 seconds; lint and static security checks passed.
- **Deployment:** pending my release approval and live acceptance checks.
- **48-hour record:** not started. Local test time does not count as cloud uptime.

[Current evidence and remaining work](agent_docs/IMPLEMENTATION_STATUS.md) · [Setup](agent_docs/SETUP.md) · [Requirements](agent_docs/REQUIREMENTS.md)

## What Monday does

I use Monday to read my synthetic schedule, summarize mail, prepare replies, research topics and draft sourced LinkedIn content for review.

| Scheduled task | Time in America/Los_Angeles | Intended result |
| --- | --- | --- |
| Morning briefing | 08:00 daily | Events, free gaps, weather and email summaries. |
| Content brief | 09:00 daily | An original, source-backed draft for my review. |
| End-of-day recap | 20:00 daily | Completed activity, pending decisions and tomorrow’s schedule. |
| Alert scan | Every 5 minutes | Useful notifications from my test inbox and calendar. |
| Durable checkpoint | Every minute | State backup and operational heartbeat. |

These native schedules are implemented. **Actual cloud delivery still needs acceptance evidence.**

My Telegram briefings use bold section headings and Unicode bullets without job IDs or cron management footers. Calendar gaps are calculated within the fictional profile's **09:00–17:00** window; incomplete calendar data is reported as unavailable. Email selection favors unread/flagged messages and excludes ordinary promotion/social categories. A clearly labeled synthetic preview passed Telegram's MarkdownV2 parsing check.

Every email send requires my review of the exact recipient, subject and body in Telegram. Browser chat and scheduled jobs cannot approve a send. Monday has no LinkedIn posting capability.

## My four skills

| Skill | My integration work | Evidence so far |
| --- | --- | --- |
| Calendar | Own Google OAuth client, read-only scope and a dedicated-calendar restriction. | Real calendar reads passed; deployed briefing/alert checks remain. |
| Email | Gmail API, local drafts, recipient allowlist, owner-only approval, expiry and replay protection. | Reads and offline send-gate tests passed; a real send needs my explicit approval. |
| Web search | Direct Tavily adapter with my own key, bounded calls and source attribution. | Real authenticated search passed; deployed workflow demonstration remains. |
| LinkedIn Content Brief | Original claim/source review helper, topic history, draft revision and manual review. | Published skill and fresh native install/helper execution passed; full deployed demonstration remains. |

My four advanced features are **morning briefing, end-of-day recap, email integration and proactive alerts**. For the separate advanced-integration requirement, I selected publication of my original skill.

## Architecture at a glance

```text
Telegram / Monday browser chat
              │
              ▼
Cloud Run Instance — Hermes + policy service + browser edge
              │
              ├── OpenAI browser OAuth → gpt-6.1-sol
              ├── NVIDIA developer endpoint → fallback
              ├── Tailscale → my Mac → Ollama / gemma4:e2b
              ├── Google APIs + Tavily + weather
              ├── Cloud Storage → durable state and OAuth recovery
              └── Secret Manager → private runtime credentials
```

| Component | My choice |
| --- | --- |
| Agent platform | Hermes v0.22.7, pinned and source-verified. |
| Cloud target | One Cloud Run **Instance**, initially 1 vCPU / 2 GiB. |
| Primary / local models | OpenAI OAuth `gpt-6.1-sol` / Ollama `gemma4:e2b`. |
| Fallback | NVIDIA `nvidia/nemotron-3-ultra-550b-a55b`. |
| Interfaces | Telegram and Monday’s browser chat with the Daylight visual theme. |
| Data | Local SQLite and native Hermes files, backed up to a private GCS bucket. |
| Delivery | GitHub Actions, restricted OIDC, required production review and immutable images. |

Private conversations stay on local Gemma. If it is unavailable, I hold those requests; I do not silently send them to a cloud model. Cloud-eligible work can continue through the cloud path.

[Component rationale and diagrams](agent_docs/ARCHITECTURE.md) · [UI and interaction design](agent_docs/DESIGN.md)

## Run and test locally

I prepare the ignored `.env` using [SETUP.md](agent_docs/SETUP.md), then use Docker from this project:

```sh
docker build --target runtime -t assignment3-agent:local .
docker compose up -d --no-build
```

- **Browser:** `http://127.0.0.1:18080`.
- **Access:** I enter my private `API_SERVER_KEY` in the UI, never in its URL.
- **Telegram checks:** “Compare two fictional study plans in two sentences” and “What is 17 plus 25?”
- **State:** only this project’s `state/` is mounted. The local profile defaults to UID/GID 501/20; another host can set `A3_LOCAL_UID` and `A3_LOCAL_GID`.

For the offline regression suite:

```sh
docker build --target test -t a3-tests .
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 256 --memory 4g --cpus 4 \
  --tmpfs /tmp:rw,nosuid,nodev,size=512m \
  a3-tests .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/pytest
```

## Security and operating limits

- **Accounts:** dedicated class-only accounts and synthetic data.
- **Secrets:** ignored local files or Secret Manager; none in Git, images, videos or shared reports.
- **Isolation:** non-root processes, no effective capabilities, no-new-privileges and bounded tests.
- **Inference access:** Ollama stays on loopback behind the restricted private Tailscale path.
- **Cost:** $4 total planning ceiling for `assignment3-515003`; budget tracking is not a hard cap.
- **Provider quotas:** 50 Tavily attempts, 20 NVIDIA attempts and zero paid OpenAI API-key calls; OAuth remains the primary path.
- **Grading:** no planned restarts or redeploys during the frozen window. Failures and gaps stay visible.

The image gate passed after fixes and documented, expiring applicability decisions. Raw scanner findings remain available; I do not claim that every possible vulnerability has been eliminated. [Security register](agent_docs/SECURITY_REGISTER.md)

## License

I license my original project code under the [MIT License](LICENSE), copyright © 2026 Arya Wadhwani. Third-party dependencies and supplied course materials retain their own licenses and notices. Course materials and private account data are excluded from my public repository.

## Documentation map

| File | What I use it for |
| --- | --- |
| [AGENTS.md](agent_docs/AGENTS.md) | Scope, sandbox, approvals and coding/documentation conventions. |
| [REQUIREMENTS.md](agent_docs/REQUIREMENTS.md) | All 94 requirement IDs, source references and rubric mapping. |
| [DESIGN.md](agent_docs/DESIGN.md) | Monday’s interfaces, features and review flows. |
| [ARCHITECTURE.md](agent_docs/ARCHITECTURE.md) | Components, diagrams, tradeoffs and requirement coverage. |
| [IMPLEMENTATION_STATUS.md](agent_docs/IMPLEMENTATION_STATUS.md) | Current verified results, exact artifacts and remaining acceptance. |
| [SETUP.md](agent_docs/SETUP.md) | Account setup, local commands, release and recovery steps. |
| [SECURITY_REGISTER.md](agent_docs/SECURITY_REGISTER.md) | Risks, findings, mitigations and retest evidence. |
| [GRADER_ACCESS.md](agent_docs/GRADER_ACCESS.md) | Private submission fields and account sign-in rehearsal. |
| [CLARIFICATIONS.md](agent_docs/CLARIFICATIONS.md) | Instructor Q01–Q14 and precedence decisions. |
| [SCRIPT_REVIEW.md](agent_docs/SCRIPT_REVIEW.md) | Review of the 19 original supplied files. |
| [HISTORY.md](agent_docs/HISTORY.md) | Earlier checkpoints, retained as history. |
| [PROCESS_LOG.md](PROCESS_LOG.md) | Development record and truthful AI-assistance attribution. |

## Attribution and submission

I build on [Hermes Agent by Nous Research](https://github.com/NousResearch/hermes-agent). Codex assisted with requirements, implementation, tests and documentation; I remain responsible for understanding and submitting the work.

Original course files stay unchanged under local `docs/` and are excluded from Git. Final reports, my own reflection, the Zoom video, grader login rehearsal and the genuine 48-hour record remain unfinished. Credentials go only in the prescribed private Brightspace comments.
