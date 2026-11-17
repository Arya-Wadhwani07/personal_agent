# My Personal Agent

## My November 17 regression and implementation update

I asked to prioritize implementation and leave my personal reflection and final submission writing for tomorrow. The current source passes **132 offline tests in 67.51 seconds**, with **74% measured combined statement/branch coverage** in the test process. Separate native subprocess checks, browser tests and earlier live checks have their own scope. I fixed independent alert-source failures, malformed delivery acknowledgements, failed-chat draft loss, late draft responses after sign-out, and cloud-auth readiness. My content workflow now has an original claim-to-source review helper. Alert sources run concurrently with a 30-second limit each, followed by a 55-second delivery budget. Cancellation marks an in-flight send unknown and leaves unattempted alerts pending; these limits cover network waits, not arbitrary local storage stalls.

My bounded mock load/stress/recovery checks and latest-source Chromium checks pass. Ruff and Bandit pass; the installed-package advisory check reports no known vulnerabilities in its scanned scope, excluding editable project/Hermes packages. A separate runtime image scan found OS and bundled-component advisories. The Debian 13 baseline, removal of the unused installer, and pinned zlib update cleared the scanned Critical findings and affected bundled installer packages, but **untriaged High findings still block release**. No claim of zero vulnerabilities or complete rubric coverage is justified.

I explicitly authorized publication of my reviewed original Hermes skill after its native safety scan and isolated installation passed. My public tap was fetched at commit 5ba6fa6 and passed the native safety scan. A fresh isolated Hermes profile then used Gemma to execute the installed helper successfully; the first ambiguous invocation failed and the explicit helper-command retry passed. This standalone skill check served a 4,096-token context, so it does not replace my separate 65,536-token application check or required video. My existing running local assistant remains on its earlier image; the new source and image checks do not silently update it. Live Cloud Run/GCS acceptance, bounded fallback/search usage, autonomous delivery evidence, final-model performance comparison, the genuine 48-hour record and video remain open. Earlier test/build counts below are historical checkpoints; acceptance columns describe work still to prove.

I build on [Hermes Agent by Nous Research](https://github.com/NousResearch/hermes-agent), pinned to v0.22.7. Codex assisted with my project source, documentation and tests; source comments and [PROCESS_LOG.md](PROCESS_LOG.md) record that assistance. Original course materials remain unchanged and excluded from this repository.

My [grader-access checklist](agent_docs/GRADER_ACCESS.md) records the professor's two account paths and private Brightspace fields. My [Process Log](PROCESS_LOG.md) records the implementation and Codex assistance.

## My local run

I build and run application code through Docker. I prepare the ignored `.env` and browser sign-ins using [SETUP.md](agent_docs/SETUP.md), select the verified OAuth model, and keep paid API calls disabled until their usage is bounded.

```sh
docker build --target runtime -t assignment3-agent:local .
docker compose up -d --no-build
```

My local UI is at `http://127.0.0.1:18080`. I use `API_SERVER_KEY` from my private `.env` to connect; I never put the key in the URL. The local Compose profile mounts only this project's `state/` for persistence and derives Telegram's home destination from the configured owner. Its default UID/GID are 501/20 for this Mac; another machine can set `A3_LOCAL_UID` and `A3_LOCAL_GID` to its project owner. Cloud deployment remains separately gated and uses a distinct OAuth login.

For reproducible offline checks, I build the test target and run it without network access:

```sh
docker build --target test -t assignment3-tests:local .
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 256 --memory 4g --cpus 4 --tmpfs /tmp:rw,nosuid,nodev,size=512m assignment3-tests:local .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/pytest
```

## My November 17 integration checkpoint

My selected primary is Hermes OpenAI browser OAuth with `gpt-6.1-sol`; a real synthetic inference passed. NVIDIA remains fallback and Gemma 4 E2B handles local work. Google OAuth refresh, Gmail identity and dedicated-calendar access passed; the Telegram owner is configured. My project is `assignment3-515003` with a $4 total ceiling. My Mac is connected to my own Tailscale network, and isolated Google Cloud CLI sign-in verified the active project and enabled billing. Private Gemma inference passed through an isolated Tailscale client, while an excluded tag was blocked. The separate cloud OAuth login is saved; cloud storage recovery and the actual Cloud Run path remain unverified. Published implementation checkpoints passed GitHub CI. Paid API calls remain disabled. Deployment and final evidence are unfinished; [my implementation status](agent_docs/IMPLEMENTATION_STATUS.md) distinguishes verified results from remaining work.

I am building a synthetic personal assistant for CSCI 599 Assignment 3 in [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent). I use Codex as an engineering and testing collaborator and remain responsible for understanding and submitting the work.

My selected system uses Hermes v0.22.7, Telegram, Daylight browser chat and local Gemma 4 E2B through Ollama. The deployment target is one Cloud Run Instance with a private Tailscale path to local inference. Application code, tests, Docker configuration and CI/CD workflows exist locally; the published checkpoints passed CI, while deployment and final submission evidence are incomplete.

**Provider plan:** Hermes OpenAI browser OAuth is my primary, NVIDIA is fallback and local Gemma handles private/simple work. The optional paid API adapter remains separate. Offline routing tests and browser sign-in passed; NVIDIA fallback and deployed inference still need verification. No paid inference calls have been made.

## My four skills

| Skill | What I created or configured | How I use it and what remains |
| --- | --- | --- |
| Calendar | Custom bounded Google adapter, dedicated-calendar restriction and read-only scope, with my own verified OAuth client. | Dedicated-calendar read verified (three events); briefing and alert delivery evidence remain pending. |
| Email | Custom draft store, recipient allowlist, owner-only payload-bound approval, expiry/replay protection and uncertain-send handling. | Synthetic mailbox reads and explicitly approved sends; Google credentials verified; explicit test-send evidence pending. |
| Web search | Direct Tavily adapter with my own key planned, bounded results, source attribution and LinkedIn exclusion. | Sourced briefings/content research; live authenticated search pending. This is not a wrapper around bundled search. |
| LinkedIn Content Brief | Original research-to-draft workflow, topic deduplication and stored draft history, with no publishing capability. | Daily source-backed outreach drafts for review; review controls, live demonstration and separate skill-publication evidence remain unfinished. |

Simply enabling a bundled capability does not count under the instructor clarification. I must demonstrate substantive integration and useful behavior for all four. My four advanced features are morning briefing, end-of-day recap, email integration and proactive alerts; skill names do not replace that feature requirement.

## My documentation

| Document | Purpose |
| --- | --- |
| [Working agreement](agent_docs/AGENTS.md) | Scope, sandbox boundaries, review and version control. |
| [Requirements](agent_docs/REQUIREMENTS.md) | All 94 stable requirement/option/workflow IDs and rubric coverage. |
| [Instructor clarifications](agent_docs/CLARIFICATIONS.md) | Q01–Q14, authority, final-model evidence rules and unanswered questions. |
| [Design](agent_docs/DESIGN.md) | Interfaces, skills, testing and delivery plan. |
| [Architecture](agent_docs/ARCHITECTURE.md) | Component rationale, five diagrams, requirement map and technology appendix. |
| [Implementation status](agent_docs/IMPLEMENTATION_STATUS.md) | Actual test results, artifact differences and release blockers. |
| [Setup](agent_docs/SETUP.md) | Private Telegram/Gmail/Calendar preparation and pending cloud setup. |
| [Security register](agent_docs/SECURITY_REGISTER.md) | Risks, findings, review evidence and release gates. |
| [Starter review](agent_docs/SCRIPT_REVIEW.md) | Original 19-file review and adaptation constraints. |

## My verification and operating policy

The latest completed source suite passed 37 isolated tests; later network additions still need testing. A real Hermes/Gemma memory-tool turn, isolated Chromium checks and bounded mock load/recovery checks passed. These results do not prove live Google/Telegram/cloud access or final-image readiness. The running local image predates some current source changes; full details and limits are in the status document.

My local browser entry point is `http://127.0.0.1:18080`; it is not the grader URL. Access keys stay in ignored private configuration. Class-only accounts and fictional data are required; two temporary fictional-role mailboxes are allowed, and every send still needs explicit approval.

I retain final-model logs/video. A primary-model change requires new logs and a new video; a minor non-model harness fix does not require a new full 48-hour run, but needs an honest change/test/outage timeline. Graders test after End Date (deadline + 2) and again 48 hours later; the exact first-test time is not supplied. My 48-hour observation has not started. Planned three-hour restarts stay disabled during grading; unexpected restarts remain reportable incidents with potential penalty. I keep access available through regrades.

My GCP project is `assignment3-515003`, with a $4 total spending ceiling. Google OAuth and read-only dedicated-calendar access are verified. Cloud sizing, private networking and deployment remain pending; resource increases must fit the remaining budget.

## My source and version-control boundaries

I review coherent changes, synchronize Markdown, check explicitly staged paths, commit and push to this repository. Routine pushes are authorized; deployment, skill publication, submission, destructive history changes and visibility changes retain separate approval requirements.

Original PDFs, ZIP and extracted scripts remain unchanged under local `docs/`, excluded from Git. Links into that directory require a workspace containing those materials. Credentials, caches, environments and private state are excluded. I deliberately review any sanitized evidence before publication.

Final reports, Process Log, video, published skill evidence and operational artifacts remain unfinished. I do not substitute mock results or historical model logs for final deployed evidence.

## My November 17 grader-access update

I confirmed that both configured Gmail accounts are dedicated class-only accounts with made-up data. My Gmail API integration uses OAuth, so I follow Q13's preferred Path 1 for grader access. Changing account security settings remains my explicit action; Codex has not disabled 2-Step Verification, changed passwords, published the consent app or collected backup codes. I still need the grader-style sign-in and token-validity check. Q14 separates live cloud grading from the Zoom local-Gemma video without removing the detailed video steps. My [grader-access checklist](agent_docs/GRADER_ACCESS.md) records both paths and the private submission fields; passwords/codes never belong in this repository.
