# My Security Risk and Finding Register

## My November 17 regression and implementation update

I asked to prioritize implementation and leave my personal reflection and final submission writing for tomorrow. The current source passes **129 offline tests in 24.78 seconds**, with **73% measured combined statement/branch coverage** in the test process. Separate native subprocess checks, browser tests and earlier live checks have their own scope. I fixed independent alert-source failures, malformed delivery acknowledgements, failed-chat draft loss, late draft responses after sign-out, and cloud-auth readiness. My content workflow now has an original claim-to-source review helper.

My bounded mock load/stress/recovery checks and latest-source Chromium checks pass. Ruff and Bandit pass; the installed-package advisory check reports no known vulnerabilities in its scanned scope, excluding editable project/Hermes packages. A separate runtime image scan found OS and bundled-component advisories. The Debian 13 baseline, removal of the unused installer, and pinned zlib update cleared the scanned Critical findings and affected bundled installer packages, but **untriaged High findings still block release**. No claim of zero vulnerabilities or complete rubric coverage is justified.

I explicitly authorized publication of my reviewed original Hermes skill after its native safety scan and isolated installation passed. Public-tap installation and a real agent invocation still need verification. My existing running local assistant remains on its earlier image; the new source and image checks do not silently update it. Live Cloud Run/GCS acceptance, bounded fallback/search usage, autonomous delivery evidence, final-model performance comparison, the genuine 48-hour record and video remain open. Earlier test/build counts below are historical checkpoints; acceptance columns describe work still to prove.

## My November 17 integration checkpoint

My selected primary is Hermes OpenAI browser OAuth with `gpt-6.1-sol`; a real synthetic inference passed. NVIDIA remains fallback and Gemma 4 E2B handles local work. Google OAuth refresh, Gmail identity and dedicated-calendar access passed; the Telegram owner is configured. My project is `assignment3-515003` with a $4 total ceiling. My Mac is connected to my own Tailscale network, and isolated Google Cloud CLI sign-in verified the active project and enabled billing. Private Gemma inference passed through an isolated Tailscale client, while an excluded tag was blocked. The separate cloud OAuth login is saved; cloud storage recovery and the actual Cloud Run path remain unverified. Published implementation checkpoints passed GitHub CI. Paid API calls remain disabled. Deployment and final evidence are unfinished; [my implementation status](IMPLEMENTATION_STATUS.md) distinguishes verified results from remaining work.

Status: implementation review is underway. My application source and dependency lock now exist; isolated policy/API tests and initial static/dependency scans have run. The initial dependency scan found no known advisories in its resolved scope; subsequent dependency changes require a fresh scan. Three initial static alerts were reviewed: fixed HTTPS bootstrap URL, empty OAuth cache value, and intentional container ingress binding. These are scoped configurations, not evidence that all vulnerabilities are absent. Current verification is in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

**VULN-003 — SQLite WAL-reset risk (mitigated in code; closure review pending):** The container links SQLite 3.40.1. Hermes warned that WAL mode is affected by the [SQLite WAL-reset issue](https://sqlite.org/wal.html#walresetbug). I changed my custom database to rollback journaling, matching Hermes's own fallback. No corruption was observed. Concurrent-write, snapshot and restart-related tests passed in the recorded suite. Final image/version/mode verification and closure evidence remain required; the finding is not marked closed.

Last updated: November 17, 2026.

My register supports [REQUIREMENTS.md](REQUIREMENTS.md), especially SEC-01 through SEC-08 and USER-13, and the controls proposed in [DESIGN.md](DESIGN.md) and [ARCHITECTURE.md](ARCHITECTURE.md). It will supply evidence for my final security audit rather than replace that deliverable. My working boundaries remain in [AGENTS.md](AGENTS.md).

## My security standard

I want to prevent vulnerabilities throughout development and catch problems before anyone uses the agent. My release target is **no known unresolved release-blocking vulnerabilities**, supported by current review, scans, and behavioral tests. A clean scanner result cannot guarantee that every vulnerability has been found.

My release gate blocks unresolved Critical/High findings, exposed live credentials, authentication or authorization bypass, uncontrolled email/social publishing, unintended public inference access, and violations of my sandbox boundary. These behavior-based blockers apply even if a scanner rates them lower. An untriaged scanner result is not a pass; failed, unavailable, stale, or incomplete required checks also block the security gate until resolved.

Any lower-severity residual risk needs my explicit documented decision, rationale, compensating control, owner, and review/expiry date. It remains visible in the final audit. This process must never waive an assignment requirement or relabel an unfixed release blocker as safe. The deadline does not change this standard.

## What I track

I keep **design risks** separate from **observed findings**. A risk describes a failure I need to prevent; a finding requires evidence from my code, dependency/image inventory, configuration, or test. A proposed mitigation is not a verified control.

For every actual finding, my entry will contain:

| Field | My record |
| --- | --- |
| ID and discovery | Stable `VULN-###` ID, discovery time, reporter/tool, and affected requirement/risk. |
| Affected artifact | File/component and exact commit, dependency version, image digest, or configuration revision. |
| Evidence | Sanitized reproduction, expected/actual behavior, scanner rule/advisory/CVE when one exists, tool/version/database date, and report location. |
| Assessment | Severity and rationale, exposure, exploitability, affected users/data, and triage decision. A CVE label alone does not establish reachability in my build. |
| Ownership | My assigned remediation owner, target date, and current status. |
| Fix | Proposed control, actual fix commit/configuration, and regression test. |
| Verification | Retest environment, exact artifact, result, date, reviewer, and evidence link. A fix is not closed until retested. |
| Residual decision | Any permitted lower-severity acceptance, compensating control, my approval, expiry, and final-audit reference. |

My finding lifecycle is **New → Triaged → In progress → Fixed, awaiting retest → Verified closed**. A false positive needs a recorded reason and supporting evidence. Permitted residual risks use **Accepted temporarily**, with expiry; they are not silently closed. A changed dependency, configuration, or failing regression can reopen a finding.

Secrets, personal data, exploit payloads containing live credentials, and private service URLs stay out of this Markdown. Sanitized summaries point to appropriately protected evidence where needed.

## My initial risk backlog

These are prospective risks, not discovered vulnerabilities or completed mitigations. This is my original design backlog; current scoped verification appears in the update and finding records. I own the review and release decision, with Codex assisting implementation and testing within approved scope.

| Risk ID | Potential failure and impact | Planned control | Required verification |
| --- | --- | --- | --- |
| RISK-01 | Gateway/session authorization failure exposes chat, drafts, or tools to another identity. | Authentication before operations, session ownership, minimal authorized identities, and reviewed grader access. | Missing/wrong credentials, cross-session access, unapproved messaging identity, and privilege-boundary tests. |
| RISK-02 | Credentials leak through Git, builds, logs, browser output, reports, or backups. | Runtime secret injection, redaction, excluded build paths, minimal UI exposure, and scoped retention. | Secret scans of source/history where available and image/artifact review; synthetic sentinel checks in output/logs. |
| RISK-03 | An approval bypass or replay sends email or publishes content without consent. | Code-enforced email approval/recipient restrictions; no LinkedIn publishing capability in the proposed fourth skill; noninteractive jobs only draft/notify. | Denial, changed-recipient/content, expired/replayed approval, scheduled-job, and unsupported-browser-action tests. |
| RISK-04 | Untrusted URLs reach metadata services, loopback, private networks, or local files. | Restricted fetch destinations/protocols, redirect and resolved-address checks, request/size limits, and no file-loading capability from external input. | SSRF, DNS/redirect changes, private-address/metadata/file URL cases using sandbox mocks. Only the authorized model adapter may reach its configured private Ollama endpoint. |
| RISK-05 | External text or model output executes script in browser chat. | Safe rendering/escaping, reviewed Markdown/link handling, and appropriate browser security controls. | Stored/reflected XSS fixtures in chat, source cards, error messages, and copy/export flows. |
| RISK-06 | Email, web, or imported content overrides instructions, steals data, or poisons persistent memory. | Treat retrieved content as untrusted data; isolate tool authority; validate arguments; control memory writes and provenance. | At least three distinct attacks if claiming injection defense; proposed cases target tool misuse, secret exfiltration, and persistent memory poisoning. |
| RISK-07 | Vulnerable dependencies/images or a compromised workflow reach a release. | Pinned dependency/action versions, vulnerability checks, minimal CI permissions, trusted publishing, scoped OIDC, and immutable image promotion. | Dependency/image inventory scans, workflow review, untrusted-PR isolation, and exact released digest evidence. |
| RISK-08 | Sandbox or network configuration exposes host data or unauthenticated Ollama. | No unrelated host mounts, non-root restricted processes, controlled network access, private inference, and explicit authorized setup. | Effective mount/privilege/network inspection and authorized-versus-unauthorized access tests. |
| RISK-09 | Concurrent state updates or unsafe snapshots corrupt memory, lose drafts, or mix sessions. | Controlled writer, session scoping, consistent snapshots, and verified restore. | Concurrent operations, interruption/restart, session isolation, and durable recall tests. |
| RISK-10 | Unbounded input, retries, requests, or scheduled work exhaust resources or provider budget. | Input/time/resource limits, bounded retries, concurrency control, and idempotent jobs. | Bounded sandbox load/stress, oversized payloads, timeout/retry, duplicate-job, and recovery tests. |
| RISK-11 | Content research exposes personal profiles, copies others' posts, or produces unsupported claims. | Permitted sources, synthetic assignment profile, provenance, short supported synthesis, duplicate checks, and draft-only export. | Personal-data fixtures, source/claim checks, prompt injection, stale/duplicate topics, and no-publishing assertions. |

## Alignment with my architecture

My architecture's sections A4-A11 place controls at explicit trust boundaries: authenticated entry, per-turn routing/privacy, the shared send gate, restricted provider adapters, single-writer state commits, and trusted build/release identities. Figures 3 and 4 define approval consumption/uncertain-send handling and durable memory acknowledgement. These are planned contracts, not verified controls.

The architecture review highlights implementation gates within existing risks: RISK-03 needs proof that alternate shell/tool paths cannot use send authority and that ambiguous sends are not blindly retried; RISK-09 needs an inventory of every framework/background writer, consistent snapshot hooks, and prevention of overlapping active writers. Generation-matched storage commits detect conflicts but do not by themselves fence an external side effect. RISK-04 must preserve the fixed local-model and trusted cloud-identity exceptions without exposing them to general URL fetching. RISK-06 must preserve private-task policy across subsequent model calls and tool results. Failure to establish these boundaries blocks the relevant release claim.

## Repository boundary and history

My approved repository destination is [Arya-Wadhwani07/personal_agent](https://github.com/Arya-Wadhwani07/personal_agent). Routine commits/pushes do not relax secret handling or the release gate. For the initial baseline, only project-authored documentation and .gitignore are staged; course PDFs, archives, extracted starter files, credentials, private state and generated outputs stay out of Git. Repository visibility/protections must be verified before application-source publication.

My pre-commit review checks explicit paths, content/diff and applicable verification results. This manual documentation/staging review is not an automated secret scan or a passing application-security assessment. Future scanners need to cover the actual source/history and exact candidate artifacts. A leaked secret already committed would require authorized revocation/rotation and a coordinated remediation decision; ignoring or deleting the file alone would not erase history.

## My observed findings

I recorded two statically observed findings in the unmodified Hermes starter, not a deployed application. Both were identified in the starter; my replacement application now has scoped mitigation and regression evidence, while deployed acceptance remains pending. I own remediation decisions with Codex assisting; the target is resolution/review before adopting this proxy in an exposed application. No CVE is asserted, no automated scanner/database version applies, and neither finding has a fix commit, regression result or closure evidence yet.

The common source artifact is `docs/Assignment3_local_Gemma_scripts/Hermes/web_ui.py`, SHA-256 `5730d4e2e6152ce276b16c2b98f8a3fda48019a8b594fc016618645d8e068e2b`, byte-identical to the ZIP member on November 16, 2026. [SCRIPT_REVIEW.md](SCRIPT_REVIEW.md) records archive identity and the scope. Sources remain local and unchanged.

### VULN-001 — unbounded proxy resource handling

- **Discovered:** November 16, 2026, Codex-assisted manual source review; affected RISK-10, SEC-07 and USER-13.
- **Evidence:** Lines 288-290 read supplied Content-Length without an application size bound; lines 299-300 buffer the upstream response in full; lines 327-332 create a thread per request without a source-level concurrency cap. Body parsing is outside the proxy error-handling block. The upstream 120-second timeout does not establish client-body, total-request or concurrency limits.
- **Severity/exposure:** Provisional Medium for availability risk if adopted as an exposed gateway. Effective platform limits, reachable load and impact remain unmeasured; this is not a demonstrated outage.
- **Remediation plan:** Validate framing and nonnegative bounded lengths, restrict body/response sizes and concurrent work, add client-read and total-operation deadlines, and return safe errors/backpressure. Verify deployment limits too.
- **Retest required:** Invalid/negative/oversized lengths, slow/incomplete bodies, oversized responses and bounded concurrency/stress against an authorized disposable target, with resource/recovery evidence.
- **Current outcome:** Unfixed source finding; no execution, exploit, mitigation claim or residual-risk acceptance. Required checks must pass before adopting the proxy.

### VULN-002 — unsafe access-log construction and error disclosure

- **Discovered:** November 16, 2026, Codex-assisted manual source review; affected RISK-02, SEC-05/07, CORE-10 and USER-13.
- **Evidence:** Lines 322-324 interpolate access-log text into JSON after replacing double quotes only, without JSON-escaping backslashes or applying a field/query redaction policy. Lines 314-320 return raw exception text to the client. This differs from the required sanitized, structured evidence design.
- **Severity/exposure:** Provisional Medium for log integrity and potential information disclosure if sensitive request/error data reaches these paths. No real credential leakage, attacker-controlled log entry or deployed exploit was observed. Normal chat uses an Authorization header, so this observation does not establish that the normal chat request logs its API key.
- **Remediation plan:** Use a JSON serializer with allowlisted metadata, omit query strings/message text/secrets, and return sanitized error categories with correlation IDs. Keep detailed diagnostics restricted and redacted.
- **Retest required:** Synthetic query/exception sentinels, backslash/control-character cases, parseable log records and absence of sensitive sentinels from responses/logs, inside the approved sandbox.
- **Current outcome:** Unfixed source finding; no execution, fix commit, retest or residual-risk acceptance.

Broad proxy routing, incomplete approval hooks, default-green health and daemon state snippets are additional review gates in SCRIPT_REVIEW.md. I have not labeled these as proven authentication bypass, XSS, or deployed vulnerabilities. Existing escape-before-format logic is a control to preserve and test.

## My security check record

| Check | Scope and observed checkpoint | Remaining limit |
| --- | --- | --- |
| Threat model | Trust boundaries, grader access, tools, memory and content research reviewed. | Deployed controls and residual-risk decisions remain pending. |
| Static analysis | Original 19-file manual review and initial application Ruff/Bandit checks. Three scoped alerts were reviewed. | Latest source needs renewed checks; VULN-001/002 need adaptation closure records. |
| Dependencies | Initial installed-package advisory scan reported no known advisories. Lockfile exists. | Subsequent dependency additions require a new scan; no zero-vulnerability guarantee. |
| Secrets | Ignored private configuration and explicit staging boundaries. | Current full source/history/image and artifact scan still required. |
| Container/configuration | Non-root, project-scoped sandbox and an earlier runtime image exercised. | Latest image, OS advisories, cloud IAM and deployed configuration remain unverified. |
| White-box | Approval, replay, concurrent claims, routing, bounded work and state tests passed within the recorded 68-test suite. | New provider chain, latest network code and broader injection defenses remain unverified. |
| Black-box | Isolated API and Chromium auth/plain-text rendering/overload checks passed; model replies mocked. | Live cloud/messaging/account and complete injection evaluation remain pending. |
| Release gate | Not eligible for release. | Required live checks, open findings and exact final artifact evidence remain incomplete. |

My tool selection will match the platform and repository plan. GitHub can surface code-scanning results from CodeQL or compatible third-party tools, but feature availability and licensing must be checked for my repository. If a hosted feature is unavailable, I need an approved equivalent scanner/reporting path rather than silently skipping the check. [GitHub code scanning](https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning), [GitHub security availability](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)

## How I keep the record current

Each approved implementation change includes a security review of affected paths and updates this register when risks, findings, controls, or evidence change. Before merge/release, applicable checks must cover the candidate artifact. A periodic advisory recheck can produce new findings even without code changes; its schedule and network access need approval during implementation.

If a live credential is exposed, my first remediation decision is revocation/rotation through an authorized account operation, followed by removing the exposure and retesting; deleting a string alone does not invalidate it. An incident during the observation/grading freeze comes back to me for a documented containment/fix decision. The freeze must not be used to hide a vulnerability, and any interruption remains part of the uptime evidence.

## Review history

| Date | Change | Evidence/status |
| --- | --- | --- |
| 2026-11-16 | I requested ongoing vulnerability tracking. Codex created this register, defined the release gate, and connected security review to the proposed content skill and CI/CD. | Documentation review only; no scan, penetration test, or remediation claim. |
| 2026-11-16 | I requested the detailed architecture. Codex linked its trust boundaries and storage/send failure contracts to the existing risk backlog. | Design review only; no new confirmed vulnerability, implemented mitigation, scan or retest. |
| 2026-11-16 | I supplied the repository and authorized coherent commits/pushes. Codex documented staged-content controls and local-only source/secret/state exclusions. | Documentation/staging review only; repository visibility and automated scans remain unverified. |
| 2026-11-16 | I authorized extracted-script review. Codex recorded VULN-001/002 from the unchanged Hermes proxy, with source identity, provisional severity and adaptation/retest gates. | Manual static evidence only; no exploit, scan, runtime test, fix or closure claimed. |

## My clarification-driven controls

I keep the instructor rulings in [CLARIFICATIONS.md](CLARIFICATIONS.md) separate from vulnerability findings. No new exploit is established by those posts.

- **Provider boundaries:** Hermes OpenAI browser OAuth is my selected primary, NVIDIA my fallback, with Claude an accepted alternative. Separate credentials and fixed provider endpoints, bounded attempts and per-provider audit outcomes must accompany migration. Private context must remain local through fallback. NIM reliability remains a risk even as fallback; bounded usage and my $4 total ceiling gate paid calls.
- **Synthetic account safety:** Two temporary fictional-role mailboxes and a dedicated temporary Calendar are allowed. Every send still needs explicit payload-bound human approval. Own credentials/scopes and restrictions support meaningful skill integration.
- **Availability:** Planned three-hour grading restarts stay disabled. I address measured memory pressure before freezing; 1 vCPU/4 GiB is allowed if justified and affordable. Unexpected restarts remain reported incidents with potential penalty.
- **Evidence integrity:** Final primary-model changes require new logs/video. Minor non-model fixes retain Q10's observation exemption but still require affected security/regression checks and an honest change/outage record. Unanswered fallback-only questions do not create a waiver.
- **Topology:** One Instance with an internal broker preserves the documented deployment path. I do not copy separate-Service IAM recipes into Instance configuration without verifying the actual architecture.

## My November 17 grader-access update

I confirmed that both configured Gmail accounts are dedicated class-only accounts with made-up data. My Gmail API integration uses OAuth, so I follow Q13's preferred Path 1 for grader access. Changing account security settings remains my explicit action; Codex has not disabled 2-Step Verification, changed passwords, published the consent app or collected backup codes. I still need the grader-style sign-in and token-validity check. Q14 separates live cloud grading from the Zoom local-Gemma video without removing the detailed video steps. My [grader-access checklist](GRADER_ACCESS.md) records both paths and the private submission fields; passwords/codes never belong in this repository.

### VULN-004 — release authorization did not bind project and budget

- **Discovery/owner:** November 17, 2026, Codex-assisted review of `scripts/deploy.py`; I own the release decision. Related risks: RISK-07/10.
- **Affected artifact:** Published checkpoint `7006869`. The script accepted any syntactically valid project and any float greater than zero, without matching `config/release.json`'s approved project or $4 ceiling. NaN/infinite values could bypass the intended numeric check.
- **Severity/exposure:** Medium authorization/control defect in a manually invoked release workflow. The separate readiness gate was false; no deployment or unauthorized spending occurred.
- **Remediation:** Exact project match, finite decimal budget within the reviewed ceiling, and literal boolean readiness. These checks do not impose a provider-side billing cap.
- **Verification:** All 19 release tests passed, including a different valid project/image, excessive/invalid/non-finite budgets and invalid readiness. Ruff and Bandit passed for the modified code. Source remediation is verified; final commit and CI evidence follow the reviewed checkpoint.

### My owned-tailnet setup boundary

I confirmed the Mac is online in my own tailnet, with administrator capability. The university tailnet policy is untouched. The restrictive policy passed inspection, validation and isolated positive/negative connection checks. The temporary token stayed out of application configuration and has been revoked; a retry returned 401 and its local file was cleared. The actual Cloud Run path remains unverified. My Google Cloud login is isolated in project-local configuration; read-only project/billing checks passed without provisioning.

### My private-network verification and OAuth recovery review

The first negative network probe ran on the same host as the Tailscale endpoint and received an unexpected HTTP response. I did not count it as passing isolation evidence. Serve was paused while I corrected the test boundary. On an internal Docker network, both clients proved direct host access was blocked; only Tailscale's public HTTPS control/relay destinations were reachable through a temporary proxy. The permitted tag completed synthetic inference and the excluded tag was blocked. Test nodes/keys/proxy/network were cleaned up, while the restricted private forwarder remains enabled. No public Funnel or broad LAN Ollama listener was configured.

The cloud OAuth persistence gap is now addressed in source by a separate, bounded private credential object and generation-conditional refresh intent. A pending refresh cannot silently fall back to the old bootstrap. Tests cover stale/concurrent writers, native aliases, interruption, a failed post-rotation write, cross-profile refusal and an inference gate when recovery is unresolved. The adapter is tied to pinned Hermes entry points; framework upgrades require retesting. Its bootstrap and rotating object contain live credentials, so private bucket/secret IAM and live recovery remain release blockers. A clean offline suite does not establish those deployed controls.

## My November 17 findings and retests

- **VULN-001 (application mitigation verified; deployed bounds pending):** My replacement ASGI boundary caps request/response sizes, in-flight requests and body-read time. tests/test_api.py now checks oversized chunked requests, oversized upstream responses, a slow body releasing its slot, overload and recovery. My bounded load probe requires every recovery request to succeed. I preserve the original starter unchanged.
- **VULN-002 (application mitigation verified; live logging pending):** My replacement emits JSON-serialized allowlisted audit fields and sanitized service errors. tests/test_audit.py rejects prompt fields and verifies escaped control characters; tests/test_api.py proves a synthetic private upstream error is absent from the public response. Routing tests check prompt/credential exclusion. Native/cloud log review remains a separate acceptance check.
- **VULN-003 (mitigated, not fully closed):** The new runtime links SQLite 3.46.1, replacing 3.40.1; custom state still uses DELETE journaling. The native framework fallback and actual image recovery need final verification. A newer SQLite version alone is not proof that all SQLite advisories are fixed.
- **VULN-005 (High, release blocking, open):** Trivy 0.76.0 scanned my exported runtime, without a Docker socket mount, on November 17. The original Debian 12.15 image reported 2 Critical and 43 High OS entries, plus other component findings. I moved to pinned Debian 13.7, removed the unused system installer and installed zlib1g 1:1.3.dfsg+really1.3.1-1+deb13u1. The updated inventory has 0 Critical and 47 High OS entries, including util-linux, SQLite, ncurses and other packages with no fixed Debian version listed. The count can increase across distributions; it is not an exploit count or a clean security verdict. I own remaining applicability review/remediation before release; no exception is approved. Reports: .cache/audit/image-before.json and image-final.json.
- **VULN-006 (High, release blocking pending applicability review):** Both pinned Tailscale 1.104.7 binaries contain golang.org/x/net v0.60.0. CVE-2026-78661 concerns HTML parser resource exhaustion; the scanner lists v0.62.0 as fixed. Whether the affected parser is reachable in my userspace-only configuration remains unverified. I have not silently rebuilt/forked Tailscale or changed my Mac installation.
- **VULN-007 (Medium, UI fix verified):** An in-flight content refresh could render drafts after sign-out. I now verify the active key before rendering the response. The offline Chromium probe delays the response until after sign-out and confirms no draft is restored. Failed chat input is preserved for deliberate retry and cleared on new-chat/sign-out.
- **Scanner metadata review (not a waiver):** Hermes source is pinned and archive-verified at v0.22.7, while its upstream distribution metadata intentionally says 0.0.0. The scanner consequently reports older Hermes advisories, including duplicate CVE-2026-53869 entries with fixed version 0.16.0. These need source-version applicability records; I have not blanket-ignored future Hermes findings.
- **Secret check:** An exact-value comparison against configured credentials found zero matches across 69 source/Markdown/skill files and all Git history. My first scanner attempt misclassified Google's public token_uri endpoint as a secret; excluding public OAuth endpoint metadata removed that false positive. This is a scoped check, not proof about every possible secret format or final submission artifact.

My release remains blocked by VULN-005/006 and incomplete deployed checks. The runtime-vulnerability CI workflow uses a pinned scanner and exits unsuccessfully on High/Critical findings without suppressions. The dependency scan's clean result cannot override the image result. [Trivy image scanning](https://trivy.dev/docs/latest/guide/references/configuration/cli/trivy_image/), [Debian SQLite advisory](https://security-tracker.debian.org/tracker/CVE-2025-7458), [Debian MiniZip applicability notes](https://security-tracker.debian.org/tracker/CVE-2023-45853).
