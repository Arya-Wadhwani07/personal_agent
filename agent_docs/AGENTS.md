# Assignment 3: My Working Agreement

## My role and engineering support

I am responsible for implementing, understanding, and submitting this personal assistant. I use Codex as an expert Agentic AI engineering and testing collaborator to help interpret the assignment, develop the system, review its data and code, and verify the results. My target is **100/100**, with evidence for every applicable full-credit rubric criterion. The instructor determines the final grade, so this target is not a guaranteed score.

- **Requirements and rubric:** My plan distinguishes mandatory requirements, conditional options, recommendations, and choices I still need to make. Each applicable requirement needs a clear connection to its implementation, tests, and submission evidence. Ambiguities belong in the review rather than becoming silent assumptions.
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
- My permission did not include reading or copying Assignment 2 implementation files, credentials, environments, or data.
- If a necessary tool requires access beyond these boundaries, I need a specific explanation and a permission request before it proceeds. The restriction must not be silently bypassed.

## My project structure

My project Markdown uses uppercase filenames, including `AGENTS.md`, `REQUIREMENTS.md`, and `README.md`. Directory names stay lowercase, with underscores where useful, such as `agent_docs/`. Code and configuration follow their language or framework conventions; supplied materials and case-sensitive tooling filenames retain their original names.

| Location | Purpose in my project |
| --- | --- |
| `agent_docs/AGENTS.md` | My working agreement, current status, and approved workflow. |
| `agent_docs/REQUIREMENTS.md` | My assignment requirements, source references, coverage review, and open questions. |
| `agent_docs/DESIGN.md` | My rough architecture, UI, sandbox, testing, and CI/CD proposal, pending review. |
| `agent_docs/ARCHITECTURE.md` | My detailed component/technology rationale, diagrams, interfaces, failure policies, and map of all 94 requirement IDs and a technology overview appendix. |
| `agent_docs/SECURITY_REGISTER.md` | My prospective security risks, observed findings, remediation/retest evidence, and release gate. |
| `agent_docs/` | My other agent planning and tracking Markdown files. |
| `README.md` | My repository overview, documentation index, current status and version-control workflow; runnable setup instructions will follow implementation. |
| `PROCESS_LOG.md` | My assignment-required development and AI-assistance history at the root, to be created in an approved change set. |
| `docs/` | My original assignment PDFs, documentation, and starter archive, preserved unchanged. |

Assignment-required submission files and platform-required workspace/skill files are exceptions to keeping planning Markdown under `agent_docs/`. I will add folders such as `src/`, `tests/`, `scripts/`, and `static/` only when the assignment and an approved implementation plan support them. The sibling project confirmed the folder conventions; its implementation does not define my Assignment 3 requirements.

## My approval and review workflow

I have approved the initial guardrails, assignment-document review, requirements baseline creation, engineering-role definition, documentation style updates, preparation of a rough design covering UI, sandbox testing, and CI/CD, and the detailed system architecture. Creating and synchronizing these documents does not approve the proposed technology choices. Application implementation, sandbox provisioning, CI/CD workflow configuration, and deployment still need approval. I have now authorized connecting this project to my named GitHub repository and committing/pushing reviewed coherent changes.

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

My application source authoring, dependency installation, execution, and runtime testing must take place in an approved isolated development environment. A Python virtual environment provides package isolation but does not restrict filesystem or network access; my execution boundary needs a container or VM as well. Project Markdown authoring and native file-content checks remain within Assignment 3 and do not authorize application execution.

- My sandbox receives only approved project source, synthetic fixtures, and explicitly authorized test credentials. Personal documents, unrelated local files, home directories, existing credential stores, and host shell history must not be exposed or mounted.
- Unit and mock integration tests should run without external service access, using disposable state. Live checks require their own approved profile and actual-service evidence, with no claim that mocks prove deployed behavior.
- My test plan includes both white-box checks of internal policies/branches and black-box checks through supported interfaces, alongside the existing SDLC categories. Load, stress, and destructive recovery checks target disposable sandbox infrastructure within agreed limits.
- Local Docker installation/startup can create host-side files outside Assignment 3. I have not approved that exception. A remote disposable development environment and isolated CI runners are proposed alternatives; provisioning or transfer to a new environment still needs my authorization. Routine source pushes to my named GitHub repository are authorized under the version-control agreement.
- My GitHub CI/CD plan must validate early and keep releases reproducible. Builds and tests can be automated, but production deployment needs my approval and must be blocked during the 48-hour evidence window and grading freeze unless I explicitly authorize an intervention. Every intervention must be recorded honestly.
- My confirmed deadline is November 17, 2026, at 11:59 PM. America/Los_Angeles is the planning timezone pending confirmation; my remaining grace-day balance is unknown. Grace days do not reduce the required 48 hours of real operation.

## My design alignment

My [design proposal](DESIGN.md), [system architecture](ARCHITECTURE.md), and [requirements baseline](REQUIREMENTS.md) need to stay consistent as I make decisions:

- My assistant needs both a Telegram/Discord integration and the selected platform's browser interface for grading. WhatsApp alone or a browser-only implementation would leave requirements unmet. My browser interface does not count as a third messaging platform.
- Hermes, Telegram, and a small neumorphic browser chat remain a proposed combination. If I choose OpenClaw, its dashboard and grader-access requirements take precedence over assumptions about custom styling.
- My UI should use soft raised panels and recessed inputs while preserving readable contrast, keyboard access, clear status, and honest loading/error states. The supplied Hermes browser UI must block approval-gated sends and direct me to drafts or a supported messaging approval flow.
- My sandbox review must verify effective filesystem, privilege, network, credential, resource, and cleanup boundaries before application execution. White-box and black-box results must identify whether dependencies were mocked or real.
- My delivery workflow should validate changes in isolated CI, build a reviewed immutable image, deploy only an approved release to a Cloud Run Instance, and verify readiness and live behavior afterward. Any rollback needs compatible state and explicit authorization. The GitHub destination and routine commit/push workflow are authorized; Actions, OIDC, secrets, protections, and deployment configuration remain pending.
- My remaining planning inputs include repository visibility/access controls, chosen sandbox host, laptop RAM, cloud authentication, test integrations, deadline timezone, and grace balance. Missing inputs stay visible; the deadline does not justify skipping verification or claiming an incomplete 48-hour run.
- My new fourth-skill recommendation is LinkedIn Content Brief: permitted-source research, topic selection, an original source-backed daily draft, and review history. It remains a proposal. The initial scope has no direct LinkedIn search, personal-account access, or social publishing capability; it uses a synthetic assignment profile and does not replace the four required advanced features.

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

## My current status and next steps

1. **Guardrails:** I have approved the boundaries, uppercase Markdown naming, engineering/testing role, continuous documentation maintenance, and natural first-person writing style.
2. **Assignment analysis:** My source review with Codex was completed on November 16, 2026: all five PDFs (103 pages) and all 19 archive files were read without executing the supplied code. The video-instruction pages and rubric table were also visually reviewed. My original documents remain unchanged.
3. **Requirements:** My baseline in `agent_docs/REQUIREMENTS.md` contains 94 traceable requirement/option/workflow IDs, including ongoing vulnerability tracking, the daily content-skill proposal, and standing version-control workflow. My review is still pending. No application tests, security scans, or 48-hour run have taken place.
4. **Design choices:** My rough `agent_docs/DESIGN.md` proposes Hermes, Telegram, a small neumorphic browser chat, LinkedIn Content Brief as the fourth skill, isolated development/testing, and controlled GitHub delivery. These are proposals, not approved selections. Platform, hardware/models, cloud auth, sandbox host, repository protections, integrations, privacy policy, content preferences, features, and advanced integration remain open. My deadline is confirmed, but timezone, grace balance, MP4/ZIP packaging, and automatic restarts during grading still need clarification. My detailed ARCHITECTURE.md now covers all 94 requirement IDs, five diagrams, component/stack rationale, routing and approval policies, durable-state recovery, delivery, and submission evidence. It recommends original-skill publication as the advanced-integration option, pending selection and separate publication authorization. My architecture review and unresolved decisions precede implementation.
5. **Implementation:** I have authorized the design documents, and project-local Git setup/commits/pushes to my named repository, not runtime code, workflows, installations, accounts, sandbox provisioning, or deployment. My design review comes next; related Markdown will stay current throughout later approved implementation.
6. **Final verification:** My later milestones include real integration/security/performance checks, the 48-hour evidence, reports, Process Log, video, and grader access. Publishing, deployment, and submission need the relevant approval; grading access must remain available through regrades.

For the completed PDF review, Codex used installed macOS PDFKit through Swift without installing dependencies. Its extraction/rendering files and compiler caches stayed in project-local temporary storage and were removed afterward. Any future dependency installation or inspection of external tool locations remains subject to my boundaries.

## My documentation review record

- **2026-11-16:** My initial Codex-assisted documentation review established the source baseline, naming, root-document exceptions, and synchronization rule. It checked source links, requirement IDs, thresholds, rubric totals, original-file hashes, and consistency between the Markdown files. Runtime tests were not applicable.
- **2026-11-16:** I requested the engineering/testing role and 100/100 target. Codex added USER-06 and checked the corresponding documentation without changing the approval boundaries.
- **2026-11-16:** I requested a natural first-person voice across project Markdown. Codex revised both files, added USER-07, and checked requirement preservation, links, table structure, attribution, and pending-work status. Runtime tests were not applicable to this wording change.
- **2026-11-16:** I requested sandbox-only development/testing, white-box and black-box coverage, GitHub CI/CD, and a rough neumorphic UI/system design. Codex created DESIGN.md, added USER-08 through USER-12, and synchronized the deadline and pending decisions. The document review checked traceability, links, counts, and unchanged execution/approval boundaries; no runtime tests or external setup occurred.
- **2026-11-16:** I requested explicit synchronization of AGENTS.md and REQUIREMENTS.md with DESIGN.md. Codex clarified the difference between document preparation and design approval, added interface/delivery guardrails, and mapped the new workflow requirements to design sections and acceptance evidence. This remains a documentation-only change.
- **2026-11-16:** I requested ongoing security-vulnerability tracking and a LinkedIn-oriented fourth skill. Codex created SECURITY_REGISTER.md, added USER-13/14, revised the content workflow/UI and CI/CD security gate, and synchronized all project Markdown. The review retained first-person wording, source restrictions, and pending implementation status. No security scans or social actions occurred.

- **2026-11-16:** I requested a complete system architecture with requirement coverage, diagrams, references, and technology reasoning. Codex created ARCHITECTURE.md and synchronized the other four Markdown files. The architecture includes all 93 existing IDs and explicit conditional alternatives; stack selection and implementation remain pending. Document checks do not constitute rendered-diagram or runtime/security test results.

- **2026-11-16:** I supplied [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent) and authorized commits/pushes after meaningful reviewed changes. Codex added the technology appendix and USER-15, synchronized the six project Markdown files, and prepared the initial repository baseline with explicit source/secret/generated-file exclusions. Extracted Gemma scripts await my next instruction before a new inspection; CI/CD execution and runtime checks remain pending.
