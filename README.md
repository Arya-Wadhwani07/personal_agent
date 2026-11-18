# Monday

I built **Monday**, a class-only personal assistant for CSCI 599 Assignment 3. It uses Hermes, Telegram and browser chat, with OpenAI OAuth for cloud reasoning and Gemma 4 E2B for local inference.

My profile is **Alex Chen**, a fictional student in Los Angeles. Connected accounts and demonstration data are dedicated to this assignment.

## What Monday does

| Skill | My integration work |
| --- | --- |
| Calendar | Own Google OAuth client, read-only scope, dedicated calendar, local-day events and calculated free-time windows. |
| Email | Gmail API summaries, local drafts, urgency flags, recipient allowlist and exact Telegram human approval. |
| Web search | Direct Tavily adapter with my own key, bounded attempts and source attribution. |
| LinkedIn Content Brief | Original research/draft workflow, claim/source review, topic history and browser revision/copy/dismiss controls, plus one daily indexed LinkedIn AI-post recommendation. No LinkedIn login, scraping or publishing. |

My four advanced features are **morning briefing, end-of-day recap, email integration and proactive alerts**. For the separate advanced integration, I published my [original skill at a pinned tap revision](https://github.com/Arya-Wadhwani07/personal_agent/tree/5ba6fa66a26bb09b6293a76dd6b4078e710a99c2/skills/linkedin-content-brief) and exercised a fresh native installation.

## Daily schedule

All schedules use `America/Los_Angeles` and native Hermes cron.

| Task | Schedule | Result |
| --- | --- | --- |
| Morning briefing | 08:00 | Events, gaps within the fictional 09:00–17:00 workday, Open-Meteo weather with NWS fallback, prioritized unread/starred email summaries, and one LinkedIn AI reading recommendation. |
| Content brief | 09:00 | A sourced original draft for my review. |
| Evening recap | 20:00 | Recorded activity, review decisions and tomorrow's schedule. |
| Alerts | Every five minutes | Fresh urgent-mail and upcoming-meeting notifications. |
| Durable checkpoint | Every minute | State backup and operational heartbeat. |

Telegram messages use bold headings and Unicode bullets without technical cron wrappers. Every email send requires my review of the exact recipient, subject and body through `/review DRAFT_ID` and its Telegram approval button. Browser chat and unattended jobs cannot approve a send.

## Models, privacy and deployment

- **Platform:** Hermes v0.22.7 on Python 3.14.
- **Primary:** Hermes OpenAI browser OAuth with `gpt-6.1-sol`.
- **Local:** Ollama `gemma4:e2b`, 65,536-token context, thinking disabled for short local turns.
- **Fallback:** NVIDIA `nvidia/nemotron-3-ultra-550b-a55b`, with bounded attempts.
- **Privacy:** private conversations and private tool context stay on local Gemma. If it is unavailable, I hold those requests. Cloud-eligible work can use the cloud when my laptop is offline.
- **Deployment:** one Cloud Run **Instance** in `us-west1`, with 1 vCPU / 2 GiB. The existing registry and state bucket are in `us-central1`.
- **Storage:** transactional SQLite/native Hermes files with generation-fenced private GCS checkpoints.
- **Credentials:** ignored local files or pinned Secret Manager versions; separate local/cloud OAuth sign-ins.

[Component rationale and diagrams](agent_docs/ARCHITECTURE.md) · [Interface design](agent_docs/DESIGN.md)

## Run locally

I prepare the private configuration using [SETUP.md](agent_docs/SETUP.md), then run from this project:

```sh
docker build --target runtime -t assignment3-agent:local .
docker compose up -d --no-build
```

- Browser: `http://127.0.0.1:18080`; enter the private API key in the form, never in the URL.
- Telegram smoke checks: “Compare two fictional study plans in two sentences” and “What is 17 plus 25?”
- Only this project's `state/` is mounted; local UID/GID defaults are 501/20.
- `A3_EMAIL_ENABLED` defaults off until the class-only data profile is prepared. Filtering is not a substitute for synthetic-only account contents.

## Test and release

```sh
docker build --target test -t a3-tests .
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 256 --memory 4g --cpus 4 \
  --tmpfs /tmp:rw,nosuid,nodev,size=512m \
  a3-tests .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/pytest
```

[Verification results](agent_docs/IMPLEMENTATION_STATUS.md) identify the test environment and artifact. GitHub validates source, builds native images and applies security gates. Publication and deployment are separate reviewed operations; only the exact approved digest and region can deploy.

I follow the [release and submission checklist](agent_docs/FINAL_REVIEW.md), commit and push the frozen configuration **before** starting observation, then collect actual logs/video separately from tracked source. The live Cloud Run URL, access key and test-account passwords are supplied only through Brightspace Comments. [Grader access instructions](agent_docs/GRADER_ACCESS.md)

## Security and cost

Non-root execution, no effective capabilities, no-new-privileges, narrow tools, safe rendering, strict email approval and restricted Tailscale access protect the test profile. My [security audit](agent_docs/SECURITY_AUDIT.md) explains residual risks and the scope of the attack tests; it does not claim perfect security.

My $4 project target is tracked, not enforced as a billing hard cap. Lifetime limits are 50 Tavily attempts, 20 NVIDIA attempts and zero paid OpenAI-key calls. Resource, storage and availability costs are checked before release and monitored during operation.

## Documentation

| File | Purpose |
| --- | --- |
| [PROCESS_LOG.md](PROCESS_LOG.md) | My lessons, tools, chronological narrative, code attribution and verification. |
| [REQUIREMENTS.md](agent_docs/REQUIREMENTS.md) | All 94 requirements, sources and rubric weights. |
| [ARCHITECTURE.md](agent_docs/ARCHITECTURE.md) | Components, diagrams, rationale and requirement mapping. |
| [PERFORMANCE_REPORT.md](agent_docs/PERFORMANCE_REPORT.md) | Three task types, measured model outputs/timings, routing and cost limits. |
| [PERSONALIZATION_PROFILE.md](agent_docs/PERSONALIZATION_PROFILE.md) | Fictional profile and native workspace snapshots. |
| [SECURITY_AUDIT.md](agent_docs/SECURITY_AUDIT.md) | Threat model, controls and attack outcomes. |
| [SECURITY_REGISTER.md](agent_docs/SECURITY_REGISTER.md) | Finding IDs, remediations and artifact-specific dispositions. |
| [AGENTS.md](agent_docs/AGENTS.md) | My scope, approval, sandbox and documentation agreement. |

Original course materials remain unchanged under local `docs/` and are excluded from Git. The [Hermes v0.22.7 framework](https://github.com/NousResearch/hermes-agent/tree/v0.22.7) supplies the native platform; source/adaptation attribution is recorded in my Process Log.

Weather is fetched fresh and checked for the current local date, valid values and observation age. Temporary transport/server failures get one bounded retry. Ordinary Gemma outages use OpenAI OAuth first, with NVIDIA as the transient-failure fallback; private requests stay held locally. My frozen source is independent of the separately collected 48-hour logs and video.

## License

I license my original project code under the [MIT License](LICENSE), copyright © 2026 Arya Wadhwani. Third-party dependencies and course materials retain their own licenses and notices.

### My daily AI read and weather sources

- **Today’s AI read:** one public LinkedIn post link, a short summary based on its search preview, and why it is useful. I label the evidence **Search preview**; I do not claim full-post access or guarantee the destination stays accessible without login. No suitable result produces an honest empty state.
- My direct Tavily adapter searches indexed posts, keeps one cached selection per local day, avoids the previous 30 selections, and shares the existing 50-call budget. It never signs into or fetches LinkedIn pages. Original draft creation remains available.
- My weather adapter tries Open-Meteo within 18 seconds, then a bounded 12-second [NWS fallback](https://www.weather.gov/documentation/services-web-api). NWS output identifies forecast periods and highs/lows; forecasts are not labeled as current observations. Missing data is never invented.
