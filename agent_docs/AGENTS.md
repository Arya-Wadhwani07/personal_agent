# Monday — Working Agreement

I am building **Monday** for Assignment 3. This file defines my working boundaries; [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) is the current progress record.

## On this page

- [My role and engineering support](#my-role-and-engineering-support)
- [My documentation voice](#my-documentation-voice)
- [My filesystem boundaries](#my-filesystem-boundaries)
- [My project structure](#my-project-structure)
- [My approval and review workflow](#my-approval-and-review-workflow)
- [My version-control agreement](#my-version-control-agreement)
- [My sandbox and delivery constraints](#my-sandbox-and-delivery-constraints)
- [My design alignment](#my-design-alignment)
- [My instructor clarification policy](#my-instructor-clarification-policy)
- [My starter-code adaptation rules](#my-starter-code-adaptation-rules)
- [My security finding workflow](#my-security-finding-workflow)
- [How I maintain requirements](#how-i-maintain-requirements)
- [My validation standard](#my-validation-standard)
- [My Markdown conventions](#my-markdown-conventions)

## My role and engineering support

I am responsible for implementing, understanding, and submitting this personal assistant.

- I use Codex as an expert Agentic AI engineering and testing collaborator to help interpret the assignment, develop the system, review its data and code, and verify the results.
- My target is **100/100**, with evidence for every applicable full-credit rubric criterion.
- The instructor determines the final grade, so this target is not a guaranteed score.

- **Requirements and rubric:** My plan distinguishes mandatory requirements, conditional options, recommendations, and recorded implementation choices. Each applicable requirement needs a clear connection to its implementation, tests, and submission evidence. Ambiguities belong in the review rather than becoming silent assumptions.
- **System design:** I expect engineering review to cover routing, tools, human approval, memory, scheduling, integrations, deployment, security, and recovery together. Configuration and model claims need to be checked against actual behavior.
- **Data and code quality:** My review process covers synthetic inputs, generated outputs, persisted state, logs, and evidence for correctness, provenance, consistency, freshness, and sensitive content. Generated or adapted code also needs review for maintainability, failure handling, security, and attribution.
- **Testing:** I expect relevant edge cases, negative paths, integration boundaries, UI behavior, concurrency, load, stress, recovery, and regression to be considered. Mock results and live evidence must remain distinguishable, with limitations recorded.
- **Completion:** I will treat a requirement as complete only when its implementation, checks, and required evidence support that conclusion. Gaps, failed checks, and grading risks stay visible until resolved through the approval workflow. Results, uptime, benchmarks, and coverage must never be invented.
- **Understanding:** I need to understand consequential choices well enough to review, operate, and explain my submission. Codex should explain its reasoning and verification results clearly. Its engineering role does not expand filesystem permissions or authorize implementation, external actions, or submission.

## My documentation voice

I want project Markdown written from my perspective, in clear, natural first-person language. Varied sentence structure and concrete explanations should make the writing easy to follow, without repeatedly starting every sentence with “I do” or “I have to.” Concise headings, table labels, and technical facts can stay neutral where that reads more naturally.

This applies across my existing and future Markdown files, including requirements, plans, setup instructions, reports, and the Process Log. References to “the student” or “the user” should become “I,” “my,” or a natural equivalent when they refer to me. References to another student, a grader, or an application user keep their actual meaning.

My writing must stay accurate about who did the work and what has happened. Plans use future or conditional language; completed work needs evidence. Codex-assisted reviews and generated code retain truthful attribution, and personal reflections must come from my actual experience. Original assignment files, quoted prompts, commands, filenames, and source requirements keep their original meaning.

## My filesystem boundaries

- My project root is `/Users/arya/Personal/Code/Projects/CSCI 599/Assignment 3`. All project changes stay inside it; creating, editing, deleting, moving, or installing anything outside it requires my explicit permission.
- Temporary files, caches, environments, logs, and test outputs also stay inside my project. Commands need a side-effect check before execution.
- I allowed one read-only inspection of the sibling `Assignment 2` directory to learn its structure. That inspection is complete. Further inspection outside Assignment 3 requires fresh permission, including any return to Assignment 2.
- I subsequently authorized inspecting and reusing relevant Assignment 2 API configuration, including the OpenAI/Claude, NVIDIA and search credentials needed for this assignment. This does not cover unrelated application code or personal data. Credentials must never be printed or committed. I supplied a $4 total budget for project assignment3-515003; paid calls remain disabled until bounded usage is configured.
- I have approved Docker Desktop runtime/cache files outside Assignment 3, with only this project mounted into containers. I have also approved synthetic checks against my installed Ollama/Gemma, including Ollama runtime/log files. These exceptions do not permit unrelated host-file access.
- I also approved a targeted Tailscale installation/status inspection, followed by installation and sign-in using the verified Tailscale 1.104.7 macOS package. This exception covers the app, network extension and its runtime files. I subsequently authorized owned-tailnet policy configuration and scoped enrollment through a temporary API token; that token was revoked after setup. I handle administrator approval and sign-in myself; unrelated host inspection remains prohibited.
- If a necessary tool requires access beyond these boundaries, I need a specific explanation and a permission request before it proceeds. The restriction must not be silently bypassed.

## My project structure

My project Markdown uses uppercase filenames, including `AGENTS.md`, `REQUIREMENTS.md`, and `README.md`. Directory names stay lowercase, with underscores where useful, such as `agent_docs/`. Code and configuration follow their language or framework conventions; supplied materials and case-sensitive tooling filenames retain their original names.

| Location | Purpose in my project |
| --- | --- |
| `agent_docs/AGENTS.md` | My working agreement, current status, and approved workflow. |
| `agent_docs/REQUIREMENTS.md` | My assignment requirements, source references, coverage review, and source clarifications. |
| `agent_docs/DESIGN.md` | My selected architecture, UI, sandbox, testing and CI/CD design. |
| `agent_docs/ARCHITECTURE.md` | My detailed component/technology rationale, diagrams, interfaces, failure policies, and map of all 94 requirement IDs and a technology overview appendix. |
| `agent_docs/SECURITY_REGISTER.md` | My prospective security risks, observed findings, remediation/retest evidence, and release gate. |
| `agent_docs/SCRIPT_REVIEW.md` | My 19-file extracted starter review, exact source observations, adaptation order and planned verification. |
| `agent_docs/` | My other agent planning and tracking Markdown files. |
| `README.md` | My repository overview, documentation index, current status and version-control workflow; runnable setup and testing instructions. |
| `PROCESS_LOG.md` | My assignment-required development and AI-assistance history at the root, including my dictated reflection, 200–300-word narrative and truthful AI attribution. |
| `docs/` | My original assignment PDFs, documentation, and starter archive, preserved unchanged. |

Assignment-required submission files and platform-required workspace/skill files are exceptions to keeping planning Markdown under `agent_docs/`. I will add folders such as `src/`, `tests/`, `scripts/`, and `static/` only when the assignment and an approved implementation plan support them. The sibling project confirmed the folder conventions; its implementation does not define my Assignment 3 requirements.

## My approval and review workflow

I have approved the documentation baseline and now authorized implementation of the full assignment, its sandbox tests, CI/CD configuration, and routine reviewed commits/pushes to my named repository. Hermes, Telegram, Gmail, and a dedicated Google Calendar are the selected implementation baseline.

- I supplied GCP project assignment3-515003 and a $4 total spending ceiling. Paid calls remain disabled until bounded usage is configured; production deployment requires explicit release approval.

- Before each new coherent change set, I expect a concrete description of the proposed work so I can approve its scope. Actions already covered by that approval do not need repeated permission requests.
- Each change set ends with a review of the files or diff, applicable checks, and a clear account of changes, results, limitations, and decisions. I review that checkpoint before the next scope begins.
- My Markdown stays current within the same approved change set. Any affected requirements, plans, status, setup instructions, and validation records need updating as they become stale. Routine documentation synchronization is included in the approved scope; original assignment materials stay untouched.
- When uncertainty affects requirements, design, dependencies, external access, cost, or scope, I expect investigation within the permitted boundaries followed by a focused question before a consequential choice.
- Deployment, submission, skill publication, repository-visibility/access changes, and contacting others each require my explicit authorization. Routine commits and pushes to my named repository are covered by the standing version-control authorization below.

## My version-control agreement

My repository is [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent). I authorize project-local Git setup and routine commits/pushes of meaningful, reviewed changes to this destination. This standing permission covers the current documentation baseline and future changes that are otherwise within approved implementation scope; it does not authorize new application work by itself.

- Each coherent change set includes synchronized Markdown, applicable checks, a reviewed staged diff, a descriptive commit, and a push. I expect the resulting commit/branch and remote verification to be reported. Failed or blocked pushes must be reported honestly.
- My initial repository branch is `main`. Future changes should use a suitable feature branch and review workflow when configured. Remote branch rules take precedence; a rejected push is not permission to force-push or rewrite shared history.
- My author identity is configured only in this project's Git metadata using the name/email I supplied in chat. I do not need global Git changes.
- I stage explicit project paths. Credentials, private state, environments, caches, and generated outputs stay out of commits. My supplied course PDFs, ZIP, and extracted starter directory remain local under `docs/` and are excluded from the initial repository baseline; source links are therefore local-reference links.
- My Git repository is a record of reviewed source, not a backup of credentials, mutable agent state, or operational evidence. Recovering a live system still requires the storage and rollback procedures in ARCHITECTURE.md.
- Routine history recovery should preserve published history, normally through a reviewed revert commit. Destructive reset, force-push, removal of others' work, visibility/access changes, and deployment still need specific authorization.
- Repository visibility, branch protection and account-plan capabilities must be verified before application-source publication and CI/CD configuration. No visibility change is included in this task.

## My sandbox and delivery constraints

My application source authoring, dependency installation, execution, and runtime testing must take place in an approved isolated development environment.

- A Python virtual environment provides package isolation but does not restrict filesystem or network access; my execution boundary needs a container or VM as well. Project Markdown authoring and native file-content checks remain within Assignment 3 and do not authorize application execution.

- My sandbox receives only approved project source, synthetic fixtures, and explicitly authorized test credentials. Personal documents, unrelated local files, home directories, existing credential stores, and host shell history must not be exposed or mounted.
- Unit and mock integration tests should run without external service access, using disposable state. Live checks require their own approved profile and actual-service evidence, with no claim that mocks prove deployed behavior.
- My test plan includes both white-box checks of internal policies/branches and black-box checks through supported interfaces, alongside the existing SDLC categories. Load, stress, and destructive recovery checks target disposable sandbox infrastructure within agreed limits.
- I approved Docker Desktop startup and its runtime/cache files. Development uses a non-root container with a read-only system, no added capabilities, and project-only mounts. Runtime tests use disposable containers with networking disabled and read-only source. I approved synthetic load/stress checks up to 4 CPUs/4 GiB and 60 seconds per run, without paid calls.
- My GitHub CI/CD plan validates early and keeps releases reproducible. Production deployment needs approval and stays blocked during grading. My observation release is controlled: a minor non-model fix does not require a new full 48-hour run (Q10), but needs review, retesting and an accurate change/outage timeline. A primary-model change needs new logs and video (Q09).
- My confirmed deadline is November 17, 2026, at 11:59 PM. America/Los_Angeles is the planning timezone; I keep any unresolved course-account details in ignored private planning notes. My stated target is to finish the genuine 48-hour interval by November 19. Q07 describes grader tests after End Date (deadline + 2) and again 48 hours later; it does not grant me extra grace days or specify the exact first-test time.

## My design alignment

My [design proposal](DESIGN.md), [system architecture](ARCHITECTURE.md), and [requirements baseline](REQUIREMENTS.md) need to stay consistent as I make decisions:

- My assistant needs both a Telegram/Discord integration and the selected platform's browser interface for grading. WhatsApp alone or a browser-only implementation would leave requirements unmet. My browser interface does not count as a third messaging platform.
- Hermes, Telegram, and Monday’s browser chat with the Daylight neumorphic theme are selected and locally implemented. A real Telegram reply is verified; the release checklist verifies deployed grader access.
- My UI should use soft raised panels and recessed inputs while preserving readable contrast, keyboard access, clear status, and honest loading/error states. The supplied Hermes browser UI must block approval-gated sends and direct me to drafts or a supported messaging approval flow.
- My sandbox review must verify effective filesystem, privilege, network, credential, resource, and cleanup boundaries before application execution. White-box and black-box results must identify whether dependencies were mocked or real.
- My delivery workflow should validate changes in isolated CI, build a reviewed immutable image, deploy only an approved release to a Cloud Run Instance, and verify readiness and live behavior afterward. Any rollback needs compatible state and explicit authorization. The GitHub destination and routine commit/push workflow are authorized. Native CI and publication passed; cloud OIDC, versioned secrets and production review/main-branch protection are verified. Deployment requires the exact-image release approval and live acceptance checklist.
- My release procedure includes explicit approval, grader-style account sign-in and a check of the course grace balance. Routine implementation and review continue without repeated approval requests; I supplied my reflection on November 17. Private networking setup and production protections are verified; the deployed private path has its own acceptance check. The repository is public; Docker is approved; this Mac has 16 GiB RAM. Hermes OpenAI browser OAuth is my primary choice, NVIDIA my fallback, and Claude an allowed alternative. OAuth routing has offline coverage and a real account-supported inference check.
- LinkedIn Content Brief is my fourth skill: permitted-source research, an original source-backed draft and review history. Its research/draft workflow and browser revision/copy/dismiss controls exist; the release checklist exercises their deployed behavior. It has no direct LinkedIn search, account access or publishing capability. Each of my four skills must demonstrate substantive integration; merely wrapping bundled search does not count.

## My instructor clarification policy

My [clarification register](CLARIFICATIONS.md) records Q01–Q14, including unanswered questions. Specific instructor answers supersede older conflicting recommendations: no planned three-hour restarts during grading; valid local inference is required for local credit; final-model logs/video must match my deployment. Minor non-model fixes retain the Q10 observation exemption.

- I keep the verified single-Instance architecture, synthetic accounts, explicit approval for every email send, and substantive four-skill evidence.
- Hermes OpenAI browser OAuth is the selected primary with NVIDIA fallback; paid calls remain disabled and deployment uses its explicit release gate. Scoped local prompts retain safety instructions and the verified context configuration.

## My starter-code adaptation rules

My [script review](SCRIPT_REVIEW.md) distinguishes supplied code from intended application behavior. I will preserve original files under docs/ and adapt reviewed copies only during approved sandbox implementation, with source attribution. Placeholder hooks, example project IDs, alternative before/after commands and configuration fragments are not executable deployment instructions as a bundle.

The supplied web UI contract and existing HTML escaping need preservation, but broad proxy forwarding, resource limits, safe logs/errors, session handling and truthful UI states need explicit review/tests.

- The two-second startup supervision loop is not the prohibited sleep-based proactive scheduler.
- I will not claim that the example approval hook, routing-log query or Tailscale state snippet implements the complete approval, router or memory subsystem.

## My security finding workflow

I expect security review throughout development, with a living [security register](SECURITY_REGISTER.md). Design risks are not confirmed vulnerabilities, and proposed controls are not passing test results. My final security audit must use the actual implementation and evidence.

- Each approved code/configuration/dependency change needs review of affected trust boundaries and applicable static, dependency, secret, container/configuration, white-box, and black-box checks in the authorized sandbox.
- Every observed finding needs a stable ID, affected artifact/version, sanitized evidence, severity/rationale, owner, remediation, regression check, and retest result. It remains open until verification supports closure; false positives need evidence too.
- My release target is no known unresolved release-blocking vulnerabilities. Critical/High findings, exposed live secrets, access-control bypass, uncontrolled sends/posts, and isolation failures block release. Failed, missing, or incomplete required checks cannot be silently skipped.
- Any lower-severity residual risk needs my explicit documented rationale, compensating control, owner, and review/expiry date. It cannot waive the assignment's requirements or hide a release blocker. A clean scan is evidence about its scope, not a guarantee that all vulnerabilities have been eliminated.
- External content is untrusted data. My implementation must restrict URL fetching, prevent unsafe browser rendering, isolate tool authority, and control memory writes. The content skill must have no publishing capability in its initial version, even if an injected instruction asks for one.
- Security work must obey the same approval boundaries. Any live scan, credential rotation, service change, or freeze-breaking remediation needs the relevant authorization; an incident and its operational impact must remain visible.

## How I maintain requirements

My requirements process uses stable IDs and source filenames with page or section references. With Codex's assistance, it covers these steps:

1. My source inventory covers `docs/`, every supplied PDF, and starter archives inspected without executing their code.
2. My requirements baseline captures functionality, architecture, model/tool constraints, setup, deployment, UI, evaluation, deliverables, video instructions, submission details, and grading criteria in `agent_docs/REQUIREMENTS.md`.
3. The classification separates obligations from recommendations, examples, optional features, assumptions, and my preferences while preserving exact thresholds and supplied deadlines.
4. My open-question record identifies conflicts, ambiguities, and choices still mine to make.
5. A second source pass checks my draft against every file, with a coverage checklist and planned acceptance evidence.
6. My completeness review covers consistency, traceability, and testability, including anything unreadable or unverified.
7. The reviewed status and proposed next steps belong in this agreement, with the requirements and implementation plan brought back to me before implementation.

## My validation standard

Every change needs checks suited to its behavior and risk. My review uses the following categories where applicable:

| Check | What my review needs to establish |
| --- | --- |
| Document and code review | Correct scope, content, consistency, requirement coverage, and absence of unintended changes. |
| Unit tests | Expected behavior, boundaries, and error paths in independently testable logic. |
| Integration tests | Correct interactions between components, models, tools, storage, and APIs. |
| Smoke tests | Working startup and essential flows after runnable application changes. |
| UI review | Usable appearance, interactions, loading/error states, responsiveness, and accessibility. |
| Load tests | Behavior under agreed representative workloads and concurrency, including response time and error rates. |
| Stress tests | Behavior and recovery under agreed higher workloads or constrained resources. |
| Regression checks | Preservation of affected existing behavior and previously fixed defects. |
| White-box tests | Internal policy branches, state transitions, error paths, and security invariants inside the sandbox. |
| Black-box tests | Observable behavior through supported UI/API/messaging interfaces inside the sandbox, with separate authorized live checks. |

My acceptance criteria come before testing. Required thresholds come from the assignment; missing performance targets need discussion. For documentation-only changes, structural and content review is appropriate, while runtime tests are marked not applicable. Implementation checks must be recorded as passed, failed, deferred with a reason, or not applicable with a reason.

Before load or stress testing, I will agree on the target, workload, duration, resource limits, and any paid API use. Failures need an honest report and proposed correction; changes beyond the approved scope come back to me first. A correction needs the affected checks repeated before it can be considered verified.


## My Markdown conventions

- **Name:** I call the bot Monday; Daylight names the browser’s visual theme.
- **Voice:** I use natural first-person wording and preserve truthful attribution.
- **Structure:** short introductions, descriptive headings, concise bullets and tables for comparisons.
- **Emphasis:** bold labels for important decisions and inline code for paths, commands and identifiers.
- **Typography:** standard GitHub Markdown heading sizes and fonts; no custom HTML font styling.
- **Status:** current results live in IMPLEMENTATION_STATUS.md. Other documents link there; superseded checkpoints remain in Git history.
- **Integrity:** formatting must preserve requirement IDs, source references, diagrams, safeguards and truthful evidence scope.

## My documentation freeze

I keep source documentation descriptive and reproducible. I remove stale setup notes and check actual behavior before stating that work is complete. My runbooks describe verification steps; measured results retain their real dates and scope. Operational logs, the video, private grader fields and the 48-hour record are collected separately from the frozen source repository. Future outcomes are not backdated or recorded as passing before execution.

My stated readiness target is 98–99/100 under the rubric. A readiness assessment is an estimate, not a grade guarantee, and does not replace any actual acceptance check or authorize deployment by itself.

Once my observation starts, I make no source, Markdown, configuration, commit, push or deployment changes during the frozen interval. Operational state, logs, video and submission evidence remain separate, ignored artifacts. Recording the completed interval does not require a Markdown edit or another deployment.
