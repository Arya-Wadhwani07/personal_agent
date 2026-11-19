# Monday — Security Register

I track findings, fixes and residual limits by artifact. A passing scoped check is **not** a guarantee that no vulnerabilities exist. I own release decisions, with Codex assisting investigation, implementation and retesting.

[Threat model and attacks](SECURITY_AUDIT.md) · [Verification record](IMPLEMENTATION_STATUS.md) · [Exact image dispositions](../config/image-dispositions.json)

## Findings and verified responses

| ID | Finding and discovery | Implemented response / evidence | Scope and residual limit |
| --- | --- | --- | --- |
| VULN-001 | Medium: supplied proxy lacks bounded body/response size and application concurrency limits; manual review November 16. | Replacement ASGI edge caps input/output, body wait and in-flight work. API tests cover slow/oversized traffic, overload and recovery. | Course original unchanged. Final-Instance acceptance checks effective deployed limits. |
| VULN-002 | Medium: supplied proxy interpolates log strings and returns raw exception text; manual review November 16. | JSON serialization, allowlisted audit fields and sanitized errors; `test_audit.py` and private-error sentinel tests. | Native/cloud logs are reviewed separately from custom logger tests. No actual credential disclosure was observed. |
| VULN-003 | SQLite baseline and durable-state compatibility require image-level review. | Hardened runtime uses SQLite 3.54.1; state, snapshots and recovery tests exercise application/native state. | Controlled actual Instance recovery belongs before observation. A version number alone does not establish security. |
| VULN-004 | Project/budget validation could accept an unreviewed deployment target or invalid limit. | Exact project, approved finite budget and reviewed-region validation; release negative tests. | Billing tracking is not a hard spending cap. |
| VULN-005 | High/Critical OS entries in earlier Trivy runtime inventories, November 17. | SQLite/ACL/zlib patched; unused mount, nsenter and infocmp removed. Remaining findings receive exact-version, profile-specific applicability dispositions. | Raw scan entries are retained. Unknown High/Critical findings, changed profile or expired review block the gate. |
| VULN-006 | High: container Tailscale x/net dependency flagged CVE-2026-78661. | Verified v1.104.7 source build with patched x/net/x/crypto; hardened image scan and profile gate. | Mac installation is outside this container patch. |
| VULN-007 | Medium: delayed content response could render after sign-out. | Active key/session check before rendering; delayed-response Chromium regression confirms no draft reappears. | Final browser rehearsal exercises the deployed artifact. |
| VULN-008 | High: klauspost/compress affected symbols in original Tailscale binaries, GO-2026-6865 / CVE-2026-116591. | Verified-source container build updates compress; hardened scan no longer reports the earlier Go findings. | Symbol presence was not claimed as an executed exploit; no crash payload was run. |

The original proxy is identified by SHA-256 `5730d4e2e6152ce276b16c2b98f8a3fda48019a8b594fc016618645d8e068e2b`. Its source locations and exact observations are in [SCRIPT_REVIEW.md](SCRIPT_REVIEW.md). Earlier discovery snapshots remain in Git history; superseded versions are not presented as the current runtime.

## Image applicability and release gate

The native `ba45c35` candidate passed its [published gate](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44195006786). This result applies to that digest. Every later publish reruns the gate against its own image.

- **Runtime profile:** non-root UID, zero effective capabilities, no-new-privileges and userspace-only Tailscale.
- **Component evidence:** systemd-homed and Perl Archive::Tar are absent; removed utility entrypoints constrain the recorded util-linux/ncurses findings.
- **Hermes metadata:** upstream reports package version `0.0.0`; pinned verified source is v0.22.7. The specific CVE-2026-53869 disposition uses source identity and Host/Origin behavior, not a blanket version suppression.
- **Expiry:** exact package dispositions expire **November 24, 2026**. `image_profile.py` and `image_gate.py` reject profile drift, unknown findings and expired reviews.
- **Evidence:** raw Trivy JSON, runtime profile proof and decisions are retained in CI artifacts. Package-entry counts are not exploit counts or a zero-vulnerability statement.

References: [SQLite releases](https://www.sqlite.org/changes.html), [Debian ACL advisory](https://security-tracker.debian.org/tracker/CVE-2026-54369), [Tailscale build source](https://github.com/tailscale/tailscale/blob/v1.104.7/build_docker.sh). Individual applicability references and exact versions are in the disposition file.

## Threat register

These are failure scenarios, not eleven discovered vulnerabilities. Each control is exercised through the security audit and relevant tests.

| Risk ID | Potential failure and impact | Control contract | Verification contract |
| --- | --- | --- | --- |
| RISK-01 | Gateway/session authorization failure exposes chat, drafts, or tools to another identity. | Authentication before operations, session ownership, minimal authorized identities, and reviewed grader access. | Missing/wrong credentials, cross-session access, unapproved messaging identity, and privilege-boundary tests. |
| RISK-02 | Credentials leak through Git, builds, logs, browser output, reports, or backups. | Runtime secret injection, redaction, excluded build paths, minimal UI exposure, and scoped retention. | Secret scans of source/history where available and image/artifact review; synthetic sentinel checks in output/logs. |
| RISK-03 | An approval bypass or replay sends email or publishes content without consent. | Code-enforced email approval/recipient restrictions; no LinkedIn publishing capability in the fourth skill; noninteractive jobs only draft/notify. | Denial, changed-recipient/content, expired/replayed approval, scheduled-job, and unsupported-browser-action tests. |
| RISK-04 | Untrusted URLs reach metadata services, loopback, private networks, or local files. | Restricted fetch destinations/protocols, redirect and resolved-address checks, request/size limits, and no file-loading capability from external input. | SSRF, DNS/redirect changes, private-address/metadata/file URL cases using sandbox mocks. Only the authorized model adapter may reach its configured private Ollama endpoint. |
| RISK-05 | External text or model output executes script in browser chat. | Safe rendering/escaping, reviewed Markdown/link handling, and appropriate browser security controls. | Stored/reflected XSS fixtures in chat, source cards, error messages, and copy/export flows. |
| RISK-06 | Email, web, or imported content overrides instructions, steals data, or poisons persistent memory. | Treat retrieved content as untrusted data; isolate tool authority; validate arguments; control memory writes and provenance. | At least three distinct attacks if claiming injection defense; cases target tool misuse, secret exfiltration, and persistent memory poisoning. |
| RISK-07 | Vulnerable dependencies/images or a compromised workflow reach a release. | Pinned dependency/action versions, vulnerability checks, minimal CI permissions, trusted publishing, scoped OIDC, and immutable image promotion. | Dependency/image inventory scans, workflow review, untrusted-PR isolation, and exact released digest evidence. |
| RISK-08 | Sandbox or network configuration exposes host data or unauthenticated Ollama. | No unrelated host mounts, non-root restricted processes, controlled network access, private inference, and explicit authorized setup. | Effective mount/privilege/network inspection and authorized-versus-unauthorized access tests. |
| RISK-09 | Concurrent state updates or unsafe snapshots corrupt memory, lose drafts, or mix sessions. | Controlled writer, session scoping, consistent snapshots, and verified restore. | Concurrent operations, interruption/restart, session isolation, and durable recall tests. |
| RISK-10 | Unbounded input, retries, requests, or scheduled work exhaust resources or provider budget. | Input/time/resource limits, bounded retries, concurrency control, and idempotent jobs. | Bounded sandbox load/stress, oversized payloads, timeout/retry, duplicate-job, and recovery tests. |
| RISK-11 | Content research exposes personal profiles, copies others' posts, or produces unsupported claims. | Permitted sources, synthetic assignment profile, provenance, short supported synthesis, duplicate checks, and draft-only export. | Personal-data fixtures, source/claim checks, prompt injection, stale/duplicate topics, and no-publishing assertions. |

## My release standard

Unresolved Critical/High findings, live-secret exposure, authentication bypass, uncontrolled sends, public inference exposure and sandbox failures block release. Unavailable or stale required checks cannot be silently counted as passing.

A finding records its ID, discovery, exact artifact, sanitized evidence, severity, owner, fix, retest and residual decision. Any temporary disposition is explicit, scoped and expiring. Changed dependencies or failing regressions reopen review.

Credentials stay out of tracked files, images, reports and ordinary backups. Exact-value scans cover configured secrets, while pattern scans and artifact review cover other exposure paths; neither guarantees every possible secret format was detected. Exposure requires authorized revocation/rotation, not merely deletion of a file.

Operational incidents retain actual timestamps. The source freeze does not hide failures; any containment or deployment change requires the relevant authorization and an honest outage record. Scheduled three-hour restarts remain disabled.

## Weather fallback and indexed reading review

- My NWS fallback validates the exact HTTPS API host/gridpoint path before following a returned reference. Freshness, timezone conversion, numeric bounds and forecast-versus-observation labeling have regression coverage.
- My daily LinkedIn recommendation fetches only Tavily’s fixed API origin. Returned links must be public post/activity paths; profiles, login links, spoofed hosts and embedded credentials are rejected. Search previews remain untrusted data and cannot authorize memory changes or sends.
- Daily caching, a 30-selection history bound, serialized selection and the existing paid-search quota limit repeated requests. These controls do not guarantee third-party availability or the accuracy of every indexed preview.

- **Initializer cleanup:** The native schedule initializer remains supervised until it exits. Deadline or shutdown paths terminate it; successful completion removes it from the running-child watch set. Regression tests exercise all three paths, preventing a timed-out initialization process from being left unmanaged.

## Connection-retry review — November 19

The local transport repair retries only connection-establishment errors, at most twice, within the existing deadline. Private context never crosses to cloud. Read/write failures, rejected responses and uncertain inference results are not replayed. Retry records contain only allowlisted metadata. Regression tests cover credential isolation, sticky privacy across compaction/restart, cancellation and the total deadline. The candidate passed 256 isolated tests, Ruff and a targeted Bandit check; each published image still requires its own runtime vulnerability gate. A persistent network failure remains an availability limitation.
