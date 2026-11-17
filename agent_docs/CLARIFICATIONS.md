# My Instructor Clarifications and Decisions

## My November 17 regression and implementation update

I asked to prioritize implementation and leave my personal reflection and final submission writing for tomorrow. The current source passes **139 offline tests in 23.09 seconds**. The preceding coverage run measured **74% combined statement/branch coverage** in the test process; the new scheduler integration runs in a separate native subprocess. Separate native subprocess checks, browser tests and earlier live checks have their own scope. I fixed independent alert-source failures, malformed delivery acknowledgements, failed-chat draft loss, late draft responses after sign-out, and cloud-auth readiness. My content workflow now has an original claim-to-source review helper. Startup now reconciles my five managed native schedules while retaining execution history and pauses; duplicate managed names stop startup, and a missing owner pauses restored notification jobs. Alert sources run concurrently with a 30-second limit each, followed by a 55-second delivery budget. Cancellation marks an in-flight send unknown and leaves unattempted alerts pending; these limits cover network waits, not arbitrary local storage stalls.

My bounded mock load/stress/recovery checks and latest-source Chromium checks pass. Ruff and Bandit pass; the installed-package advisory check reports no known vulnerabilities in its scanned scope, excluding editable project/Hermes packages. A separate runtime image scan found OS and bundled-component advisories. The Debian 13 baseline, removal of the unused installer, and pinned zlib update cleared the scanned Critical findings and affected bundled installer packages, but **untriaged High findings still block release**. No claim of zero vulnerabilities or complete rubric coverage is justified.

I explicitly authorized publication of my reviewed original Hermes skill after its native safety scan and isolated installation passed. My public tap was fetched at commit 5ba6fa6 and passed the native safety scan. A fresh isolated Hermes profile then used Gemma to execute the installed helper successfully; the first ambiguous invocation failed and the explicit helper-command retry passed. This standalone skill check served a 4,096-token context, so it does not replace my separate 65,536-token application check or required video. My existing running local assistant remains on its earlier image; the new source and image checks do not silently update it. Live Cloud Run/GCS acceptance, bounded fallback/search usage, autonomous delivery evidence, final-model performance comparison, the genuine 48-hour record and video remain open. Earlier test/build counts below are historical checkpoints; acceptance columns describe work still to prove.

## My November 17 integration checkpoint

My selected primary is Hermes OpenAI browser OAuth with `gpt-6.1-sol`; a real synthetic inference passed. NVIDIA remains fallback and Gemma 4 E2B handles local work. Google OAuth refresh, Gmail identity and dedicated-calendar access passed; the Telegram owner is configured. My project is `assignment3-515003` with a $4 total ceiling. My Mac is connected to my own Tailscale network, and isolated Google Cloud CLI sign-in verified the active project and enabled billing. Private Gemma inference passed through an isolated Tailscale client, while an excluded tag was blocked. The separate cloud OAuth login is saved; cloud storage recovery and the actual Cloud Run path remain unverified. Published implementation checkpoints passed GitHub CI. Paid API calls remain disabled. Deployment and final evidence are unfinished; [my implementation status](IMPLEMENTATION_STATUS.md) distinguishes verified results from remaining work.

Recorded November 16, 2026, from the forum excerpts I pasted into this chat. No forum URLs or absolute posting dates were supplied. Labels such as “two weeks ago” describe the pasted snapshot, not independently verified dates. I distinguish instructor/endorsed answers from student reports and unanswered questions. Original PDFs remain unchanged; the existing 94 requirement IDs are retained.

## My clarification register

| Key | Discussion and authority | My interpretation |
| --- | --- | --- |
| Q01 | Test mailboxes, local Gemma prompts and Discord access; instructor answer, two weeks ago | Two temporary mailboxes playing fictional roles are acceptable. All mail/events remain synthetic, the Google Calendar is dedicated/temporary, and every assistant send needs explicit human approval. Gemma may receive task-relevant context/tools only, while retaining necessary instructions/information. E2B is accepted; served context, memory use and a full tool turn need verification. Discord is allowed; GUI/Tailscale access was still being finalized in that older answer. |
| Q02 | OpenAI API key versus USC Edu OAuth; Marco Papa, two weeks ago | Paid OpenAI API keys and Anthropic Claude keys are acceptable alongside supported Edu/Codex OAuth. The instructor warns against NIM reliability. API-key billing is distinct from the Edu OAuth entitlement. |
| Q03 | Local hardware accommodation on an 8 GB Mac; Marco Papa, one week ago | A valid reproducible local reply is required for local points. Failure to provide it forfeits those points; cloud-only operation is not an alternative earning them. A friend's machine may be used for the video, with truthful attribution. |
| Q04 | Separate Hermes/email-broker Instances and a 403; Marco Papa, one week ago | The supplied verified architecture is recommended; deviations are my debugging responsibility. The pasted Service/IAM troubleshooting examples do not replace the assignment's Instance deployment requirement. |
| Q05 | Four skills; instructor answer, endorsed TA follow-up and later web-search reply | Simply enabling bundled capabilities is insufficient. Substantive account/credential/scope integration, safety restrictions, original workflows/code and demonstration count as integration work. The later specific answer rejects merely wrapping bundled web search. My README must explain my work and use of each skill. |
| Q06 | 4 GiB resource allocation; Marco Papa, six days ago | 1 vCPU with 4 GiB is explicitly permitted when needed to avoid OOM. I measure/justify resources and monitor spending; this is not a mandatory allocation. |
| Q07 | Adding Hermes UI after the observation window; Marco Papa, four days ago | Graders test the application and again 48 hours later after End Date (deadline + 2). I must retain final-deployment availability and not assume a completed private pre-submission soak is the sole assessment of the interval. |
| Q08 | Switching NIM to OpenAI OAuth; Marco Papa, two days ago | A model change requires a new video of the new deployment. These answers alone leave log reuse ambiguous; Q09 supplies the explicit log rule. |
| Q09 | Follow-up on a primary-model change; Marco Papa, two days ago | A changed primary model requires new logs. All logs/artifacts must relate to the final cloud/local selections. NIM and OpenAI are both cloud models. A README note cannot make old NIM-primary evidence prove OpenAI-primary behavior. |
| Q10 | Minor bug/harness fix and 48-hour evidence; Marco Papa, 14 hours ago | A minor fix without a model change does not require a new full 48-hour run. I still preserve the build/change timeline, affected test results and actual outages. The later three-part question about known defects and point deductions is unanswered. |
| Q11 | Three-hour restarts during grading; Marco Papa, updated one minute ago, plus endorsed resource discussion | Restarts during grading incur a penalty. I will disable planned three-hour restarts and address memory/capacity before grading. The student's $3/40-hour figure is an anecdote, not my cost estimate or approved budget. |
| Q12 | Adding Edu OAuth fallback after a NIM-primary run; question one hour ago, no answer supplied | This is unresolved. I do not infer blanket permission to reuse old evidence after a fallback-only change. |
| Q13 | Grader test-account access; additional professor excerpt supplied November 17 | I use dedicated class-only accounts with fictional data. OAuth uses preferred Path 1: password-only grader login, with 2-Step Verification off on the dedicated test account. Testing refresh tokens need renewal before grading or an approved Production transition. App Password integrations instead retain 2-Step Verification and at least four unused backup codes. I test a grader-style sign-in in another browser’s Incognito window and submit credentials only in Brightspace Comments. |
| Q14 | Two grading phases and added source files; additional professor excerpt supplied November 17 | Cloud behavior is tested on my live Cloud Run Instance; local Gemma is graded through the Zoom video. The video PDFs and platform-specific scripts remain the detailed checklist. CloudRunSettings.txt supplies the private Brightspace Comments format. |

## My provider decision

I asked to keep NVIDIA as fallback and use OpenAI or Claude as primary. My current selection is **Hermes OpenAI browser OAuth with gpt-6.1-sol as primary**, **NVIDIA NIM as cloud fallback**, and **Gemma 4 E2B through local Ollama as the local route**. Claude remains an acceptable alternative if I select it before final evidence collection.

The OpenAI account, gpt-6.1-sol inference and $4 total budget are verified/recorded; NVIDIA fallback still needs live verification. The existing NVIDIA model setting is a candidate, not a validated fallback. NIM's reliability warning still matters in fallback use. Q09 mentions a NIM fallback example for OpenClaw; Q12 does not establish a universal exemption for fallback changes.

My later instruction selects supported Hermes OpenAI browser OAuth as primary, retaining NVIDIA fallback. D pp. 6–7 require browser sign-in for USC and platform-owned OAuth inference. The new proxy forwards Hermes-authenticated requests; the optional paid API path remains separate. Offline tests passed, while final-model observation/video evidence remains pending. I supplied a $4 total budget.

## My evidence and restart policy

- A primary-model change requires fresh relevant logs and a new video. I record exact provider/model/auth, local tag/context, image/config revision and real timestamps. Historical logs keep their original identity.
- Q10 allows existing observation evidence for a minor non-model harness fix without restarting the full 48-hour clock. I record the change and verify it. This does not waive the grading freeze or excuse a broken required feature.
- Q12 supplies no answer about fallback-only changes. I settle and test the complete provider chain before final evidence rather than claim an unsupported exemption.
- I prepare for the grader's initial test and repeat test 48 hours later after End Date, retaining access through regrades. These excerpts do not specify the first test's exact hour/timezone or authorize fabricated uptime.
- Planned three-hour restarts stay disabled for grading. Unplanned restarts remain reported incidents with potential penalty even if state recovers. Controlled recovery tests happen before grading.

## My four-skill evidence plan

| Skill | My substantive work | Remaining evidence |
| --- | --- | --- |
| Calendar | My own OAuth client, dedicated synthetic Google Calendar, read-only scope, custom bounded adapter, briefing/reminder use. | Live account/scope review, calendar reads, scheduled use and demonstration. |
| Email | Temporary Gmail accounts, custom drafts, recipient allowlist, payload-bound human approval, replay/expiry protection and uncertain-send handling. | Synthetic read/draft flow and an explicitly approved test send. |
| Web search | My own Tavily key, direct custom adapter, bounded results, attribution and LinkedIn exclusion. | Live authenticated search used in a content brief. I do not count a bundled-search wrapper. |
| LinkedIn Content Brief | Original research-to-draft workflow, references, topic deduplication and stored review history; no publishing capability. | Useful exercised draft/review workflow; standalone publication/fresh-install evidence remains a separate advanced-integration requirement if selected. |

## My implementation boundaries

Q01's older provisional access answer does not replace G's more specific Hermes/OpenClaw access/video instructions. Telegram remains my selected messaging integration, and the browser grader interface remains necessary.

I keep **one Cloud Run Instance**, with supervised internal components and a loopback broker. Q04's Service-oriented IAM commands are diagnostic examples, not my deployment commands.

My machine has 16 GiB and has completed a real local Gemma tool turn. Scoped prompts may reduce irrelevant context, but must preserve safety policy, relevant history and tool results. I retain the verified 65,536-token Hermes serving configuration; Q01 does not explicitly lower that requirement.

No forum answer authorizes closing unrelated host applications, increasing my budget, changing repository visibility, contacting real recipients or exposing credentials. My working agreement remains in force.

## My documentation review

This update preserves all 94 requirement IDs and their architecture mappings. Review covered all 14 clarification entries, precedence, pending-versus-completed wording, Markdown tables/fences and local links. SHA-256 comparison confirmed that all 25 original PDF/archive/extracted files remain unchanged. Runtime unit/integration/load/stress tests are not applicable to this Markdown-only change; prior runtime evidence remains separately scoped in IMPLEMENTATION_STATUS.md. The primary OAuth path is verified; live fallback and deployed acceptance remain unfinished.

## My November 17 grader-access update

I confirmed that both configured Gmail accounts are dedicated class-only accounts with made-up data. My Gmail API integration uses OAuth, so I follow Q13's preferred Path 1 for grader access. Changing account security settings remains my explicit action; Codex has not disabled 2-Step Verification, changed passwords, published the consent app or collected backup codes. I still need the grader-style sign-in and token-validity check. Q14 separates live cloud grading from the Zoom local-Gemma video without removing the detailed video steps. My [grader-access checklist](GRADER_ACCESS.md) records both paths and the private submission fields; passwords/codes never belong in this repository.
