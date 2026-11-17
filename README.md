# My Personal Agent

I am building a synthetic personal assistant for CSCI 599 Assignment 3 in [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent). I use Codex as an engineering and testing collaborator and remain responsible for understanding and submitting the work.

My selected system uses Hermes v0.22.7, Telegram, Daylight browser chat and local Gemma 4 E2B through Ollama. The deployment target is one Cloud Run Instance with a private Tailscale path to local inference. Application code, tests, Docker configuration and CI/CD workflows exist locally; deployment, live accounts, CI execution and final submission evidence are incomplete.

**Provider plan:** OpenAI API is my working primary choice, NVIDIA is fallback and Claude API is an accepted primary alternative. The current cloud adapter is still NVIDIA-only. Exact cloud model IDs, migration/tests and spending approval remain pending; no paid calls have been made.

## My four skills

| Skill | What I created or configured | How I use it and what remains |
| --- | --- | --- |
| Calendar | Custom bounded Google adapter, dedicated-calendar restriction and read-only scope, with my own OAuth client planned. | Briefing and upcoming-event alerts; live account integration and demonstration pending. |
| Email | Custom draft store, recipient allowlist, owner-only payload-bound approval, expiry/replay protection and uncertain-send handling. | Synthetic mailbox reads and explicitly approved sends; live credentials and test-send evidence pending. |
| Web search | Direct Tavily adapter with my own key planned, bounded results, source attribution and LinkedIn exclusion. | Sourced briefings/content research; live authenticated search pending. This is not a wrapper around bundled search. |
| LinkedIn Content Brief | Original research-to-draft workflow, topic deduplication and stored draft history, with no publishing capability. | Daily source-backed outreach drafts for review; review controls, live demonstration and separate skill-publication evidence remain unfinished. |

Simply enabling a bundled capability does not count under the instructor clarification. I must demonstrate substantive integration and useful behavior for all four. My four advanced features are morning briefing, end-of-day recap, email integration and proactive alerts; skill names do not replace that feature requirement.

## My documentation

| Document | Purpose |
| --- | --- |
| [Working agreement](agent_docs/AGENTS.md) | Scope, sandbox boundaries, review and version control. |
| [Requirements](agent_docs/REQUIREMENTS.md) | All 94 stable requirement/option/workflow IDs and rubric coverage. |
| [Instructor clarifications](agent_docs/CLARIFICATIONS.md) | Q01–Q12, authority, final-model evidence rules and unanswered questions. |
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

My GCP project, spending limit, live credentials, deployed sizing and Tailscale configuration remain pending. 1 vCPU/4 GiB is allowed when measurements justify it; another person's cost report is not my budget.

## My source and version-control boundaries

I review coherent changes, synchronize Markdown, check explicitly staged paths, commit and push to this repository. Routine pushes are authorized; deployment, skill publication, submission, destructive history changes and visibility changes retain separate approval requirements.

Original PDFs, ZIP and extracted scripts remain unchanged under local `docs/`, excluded from Git. Links into that directory require a workspace containing those materials. Credentials, caches, environments and private state are excluded. I deliberately review any sanitized evidence before publication.

Final reports, Process Log, video, published skill evidence and operational artifacts remain unfinished. I do not substitute mock results or historical model logs for final deployed evidence.
