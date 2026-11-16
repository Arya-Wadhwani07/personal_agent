# My Personal Agent

I am developing a synthetic personal assistant for CSCI 599 Assignment 3. My repository is [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent).

The project is currently a documentation baseline. The proposed system uses Hermes, Telegram, browser chat, cloud inference and local Gemma 4 through Ollama/Tailscale, hosted on a Cloud Run Instance. Platform/provider choices still need approval and verification. No runnable application, sandbox, GitHub Actions workflow, deployment or 48-hour observation run exists yet.

## My project documents

| Document | What I keep there |
| --- | --- |
| [Working agreement](agent_docs/AGENTS.md) | Filesystem boundaries, review, security and standing commit/push authorization. |
| [Requirements](agent_docs/REQUIREMENTS.md) | 94 requirement/option/workflow IDs, source references, rubric coverage and open questions. |
| [Design](agent_docs/DESIGN.md) | Proposed experience, neumorphic UI, skills and delivery approach. |
| [Architecture](agent_docs/ARCHITECTURE.md) | Component rationale, five diagrams, all requirement mappings and a concise technology appendix. |
| [Security register](agent_docs/SECURITY_REGISTER.md) | Prospective risks, two open starter-code findings, remediation/retests and release gates; runtime controls remain unverified. |
| [Starter-script review](agent_docs/SCRIPT_REVIEW.md) | My read-only review of all 19 extracted files, source identity, adaptation plan and planned tests. |

## My version-control workflow

I review a meaningful change set, run applicable checks, synchronize affected Markdown, inspect explicitly staged files, commit with a descriptive message and push to this repository. My initial branch is `main`; future branch/protection rules will guide the workflow when configured. Remote commit verification is reported after a push. Ordinary commits/pushes are authorized; deployment, destructive history rewriting and visibility/access changes require separate authorization.

Git preserves source history. It does not replace persistent-agent backups or guarantee that an old image can restore a newer state schema.

## My local assignment materials

The original PDFs, ZIP and extracted starter files live under `docs/` in my local Assignment 3 workspace. They are excluded from this initial Git baseline; source links into that folder work only in a workspace containing those materials. I keep supplied files unchanged and retain their source references in REQUIREMENTS.md. The authorized extracted-script review is complete: all 19 files were read and found byte-identical to the ZIP. None was executed or modified.

Credentials, environments, caches, private state, recordings and generated artifacts are also excluded by default. Any sanitized evidence selected for submission or Git will need deliberate review.

## My current verification and next steps

My documentation checks cover all 94 requirement IDs, links, tables/fences, 19 archive-to-extracted comparisons, source hashes and planned-versus-completed wording. Manual review identified proxy resource-limit and log/error-handling findings for future adaptation. It did not run application tests, vulnerability scanners or rendered-diagram verification. SCRIPT_REVIEW.md gives the revised implementation order.

Before implementation I still need the decisions listed in ARCHITECTURE.md A14, the approved development sandbox and service access. CI/CD remains planned for this repository; its workflow and deployment credentials have not been configured. Runnable setup instructions will be added and verified when the application exists.

I use Codex as an engineering and testing collaborator and remain responsible for understanding and submitting my individual work. The final PROCESS_LOG.md, reports, video and live evidence remain pending.
