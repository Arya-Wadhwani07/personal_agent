# Monday — My Personalization Profile

My assistant operates as **Monday** for a fictional class-only profile. The files below are sanitized snapshots of the native Hermes workspace, not my personal biography or account credentials.

| Setting | My synthetic configuration |
| --- | --- |
| Profile identity | Alex Chen, a fictional student interested in Agentic AI. |
| Location and timezone | Los Angeles; `America/Los_Angeles`. |
| Workday for free-gap summaries | 09:00–17:00, explicitly stated in the calendar result. |
| Writing style | Concise, natural first-person drafts with source links. |
| Morning / evening delivery | 08:00 briefing and 20:00 recap through Telegram. |
| Content workflow | 09:00 research/draft for human review; no automatic LinkedIn posting. |
| Alerts | Native cron checks every five minutes for useful test-account triggers. |
| Privacy | Private conversations and private tool context use local Gemma; unavailable local inference is held. |
| Email policy | Dedicated accounts, allowlisted recipient and exact Telegram human approval for every send. |
| Memory policy | Explicitly requested synthetic preferences only; no credentials or embedded instructions. |

## Workspace files

- [SOUL.md](../profiles/classroom/SOUL.md): the actual initial personality, tool boundaries and behavior instructions.
- [USER.md](../profiles/classroom/USER.md): the actual initial fictional user context.
- At runtime, `runtime.initialize()` creates missing defaults under `/state/hermes/`; an existing profile survives initialization.
- My controlled memory adapter writes synthetic preferences through the policy store/workspace. Generation-fenced GCS checkpoints preserve state; the release checklist verifies recall after an actual Instance restart.

## Hardware choice

My local model is **Gemma 4 E2B**, served by Ollama on the 16-GiB Mac used in setup checks. I chose the smaller variant to manage resource pressure while preserving the required 65,536-token context and full tool-turn behavior. I am not claiming the cloud-only accommodation or a larger-model failure that was not measured.

[Measured model comparison](PERFORMANCE_REPORT.md) · [Memory and recovery architecture](ARCHITECTURE.md#a8-persistence-concurrency-and-restoration)

## Data handling

After I reported removing promotional mail, earlier local state was quarantined privately and excluded from this profile. Only the native OAuth login moved into the clean local runtime; it is not included in these snapshots. Real passwords, account logins, transcripts and private backups do not belong in the submitted profile.
