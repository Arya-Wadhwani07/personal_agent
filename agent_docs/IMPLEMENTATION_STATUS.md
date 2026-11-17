# Monday — Implementation Status

**Updated:** November 17, 2026. I use this page as the current evidence record. Earlier results belong in [HISTORY.md](HISTORY.md); they do not override newer checks.

## Release summary

| Item | Current result |
| --- | --- |
| Local bot | Running; I confirmed both cloud and local Telegram replies. |
| Source regression | **165 passed in 21.07 seconds**, network disabled and disposable test state. |
| Lint / static security | Ruff and Bandit passed for the reviewed source. |
| Native cloud image | Published successfully from `ecb61d2`; build, tests, image profile and vulnerability gate passed. |
| Google federation | Corrected exact ID-qualified GitHub subject; successful publish proves end-to-end authentication. |
| Production protection | My GitHub review is required; only branch `main` is allowed. |
| Cloud Run Instance | **Not deployed.** Release approval and live acceptance remain. |
| 48-hour observation | **Not started.** No uptime or completion claim yet. |

[Successful publish run](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44166861878) · [Native image gate](https://github.com/Arya-Wadhwani07/personal_agent/actions/runs/44166803286)

**Published image:**

```text
us-central1-docker.pkg.dev/assignment3-515003/a3/agent@sha256:022db95cf04cb1c740ba536d3bc8974efe37dbcf3fb05a360312018660e3baa6
```

## What I have verified

| Area | Evidence | Limit |
| --- | --- | --- |
| Routing | Real OpenAI OAuth comparison, local Gemma arithmetic and full memory-tool turn; offline privacy/failure/429 cases. | Final deployed route/failure checks and three-task comparison remain. |
| Local serving | Gemma 4 E2B at a verified 65,536-token context. | A separate published-skill helper run used 4,096; it does not replace the required context/video evidence. |
| Telegram | I confirmed replies to the two cloud/local smoke prompts. | This was the local deployment; cloud delivery remains. |
| Google | OAuth refresh, expected class-only Gmail identity, mailbox reads and dedicated-calendar reads passed. | Grader password-only sign-in and deployed alert injection remain. |
| Search / fallback | One direct Tavily basic search and one real NVIDIA fallback-model call passed. | Direct preflight calls do not prove the whole deployed routing workflow. |
| Durable state | Real GCS save/restore, quota recovery and stale-writer rejection passed under the runtime identity. | Full Cloud Run restart, native transcript/cron and network identity recovery remain. |
| OAuth recovery | Separate native cloud login, real token rotation and fresh-profile recovery passed. | Actual deployed restart acceptance remains. |
| UI | Isolated Chromium chat, content revision/copy/dismiss, XSS rendering, mobile overflow and sign-out race checks passed. | Real grader URL and cloud chat remain. |
| Published skill | Pinned public tap fetch, native safety scan, fresh installation and real Gemma helper execution passed. | Research-to-draft deployment/video demonstration remains. |
| Restore startup | A snapshot without native profile files now gets missing defaults after restore; saved preferences survive. | Covered by regression and supervisor-order tests. |

My [published original skill](https://github.com/Arya-Wadhwani07/personal_agent/tree/5ba6fa66a26bb09b6293a76dd6b4078e710a99c2/skills/linkedin-content-brief) supplies the selected advanced-integration option. Private transcripts remain outside Git.

## Test scope

- **Regression:** 165 offline tests, including actual native Hermes subprocess integration with mocked inference.
- **White-box:** routing, privacy, approvals, quotas, state fencing, recovery and release checks.
- **Black-box:** API/browser behavior and native gateway/tool turns; separate real provider and messaging probes.
- **Load:** 100/100 mocked requests at concurrency 4; p95 22.084 ms in the latest recorded probe.
- **Stress/recovery:** concurrency 32 produced 4 successes and 252 deliberate HTTP 429 responses, then 10/10 recovery successes.
- **Limits:** mocked load uses a 20 ms fake upstream. These numbers are not model or cloud throughput.
- **Coverage:** the earlier measured suite reported 74% combined statement/branch coverage. I have not measured that figure again for all 165 tests.

## Security result

- My hardened image uses **SQLite 3.54.1**, **ACL 2.4.0**, the pinned zlib security update and patched container Tailscale dependencies.
- The native amd64 build and runtime-profile gate passed. The upstream ACL suite retained its assertions: 14 passes and two expected NFS exclusions.
- The arm64 raw report retained **45 High package entries across eight CVEs** under exact-version, profile-specific decisions expiring November 24. I do not reuse that count as an amd64 count.
- Unknown Critical/High findings, changed packages, expired decisions or profile drift block release.
- Temporary tailnet administration credentials were revoked. The expired runtime impersonation grant and temporary storage/budget setup tokens were removed.

[Finding details and source references](SECURITY_REGISTER.md) · [Machine-readable dispositions](../config/image-dispositions.json)

## Cloud resources and budget

| Resource | Current state |
| --- | --- |
| Project / region | `assignment3-515003` / `us-central1`. |
| Artifact Registry | Private `a3` repository with the published immutable image. |
| State bucket | Private `assignment3-515003-a3-state`; real state and OAuth recovery checked. |
| Identities | Separate runtime/deploy service accounts and restricted GitHub OIDC. |
| Secrets | Ten versioned Secret Manager entries with scoped access. |
| Billing tracking | Project-only $4 monthly gross-cost budget; notifications disabled; **not a hard cap**. |
| Planned compute | 1 vCPU / 2 GiB; estimated $1.070496 for 72 hours at the checked Instance rates. |
| Other allocation | $0.40 search reserve and $1 for other services; total usage still needs monitoring. |

My lifetime application quotas are **50 Tavily attempts**, **20 NVIDIA attempts**, and **zero paid OpenAI API-key calls**. Failed/uncertain attempts consume quota before the request. The production state already records the search and NVIDIA preflight attempts.

The requested custom non-resetting budget period was rejected by the API. The verified tracking budget remains monthly; I do not claim a total-spend enforcement mechanism. Longer grading/regrade availability needs a fresh cost review.

## Remaining acceptance checklist

- [ ] Approve and deploy the exact published digest; stop the local Telegram poller before starting the cloud poller.
- [ ] Verify cloud health, authenticated browser chat, Telegram and actual cloud-to-Mac Gemma inference.
- [ ] Exercise the four skills and useful scheduled briefing, recap and unsolicited alerts against synthetic data.
- [ ] Review and explicitly approve one exact synthetic email if I choose to demonstrate a real send.
- [ ] Verify a controlled pre-observation restart restores state, schedules, network identity and OAuth.
- [ ] Verify runtime isolation, routing/lifecycle log fields, cost use and export filters on the real Instance.
- [ ] Start the genuine 48-hour window only after acceptance; freeze deployment and collect complete evidence.
- [ ] Complete grader-style account sign-in, final-model comparison, reports, Zoom video, my own reflection and submission packaging.

## Requirement map

| Requirement groups | Implementation | Evidence still needed |
| --- | --- | --- |
| CORE-01–11 | Native Hermes, task router, OAuth proxy, local Gemma and private network adapter. | Deployed paths, failure cases and comparison. |
| FUNC-01–09 / FEAT-01–04 | Messaging, four skills, native schedules and approval-controlled email. | Useful cloud delivery and demonstration. |
| SEC-01–08 | Isolation, secret scopes, validation, send gate and image gate. | Deployed controls and final audit/attack evidence. |
| OPS-01–10 | Generation-fenced state, OAuth recovery, Instance release and observation helpers. | Restart acceptance and real 48-hour coverage. |
| ADV-01 | Original published skill, fresh install and execution. | Final video/submission evidence. |
| USER / VIDEO / DOC | Guardrails, CI/CD, readable docs and submission plan. | Remaining human inputs and final deliverables. |

The full [94-ID requirements baseline](REQUIREMENTS.md) and [architecture map](ARCHITECTURE.md#a15-requirement-by-requirement-architecture-coverage) remain authoritative. A source implementation or passing mock test alone does not complete a grading criterion.

## Exact-image release control

My predeployment gate now names the tested `ecb61d2` registry digest. Deployment and observation refuse a different digest, even if it is a valid image in my registry. `ready` records passed predeployment engineering checks; the GitHub production job still requires my explicit approval before it can deploy. Post-deployment checks remain required before observation; they are not falsely marked complete to permit the first deployment.

My exact-image release/observation checks passed **26 isolated tests**, with lint and static security checks passing. The private environment matches the reviewed project, state bucket and provider quotas. The prepared deployment command has not been executed; my production review is the final authorization step.
