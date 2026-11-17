# Monday — Setup and Operation

I keep account secrets in ignored project files and execute application code only inside the approved Docker sandbox. **Existing working credentials do not need to be regenerated.**

[Current status](IMPLEMENTATION_STATUS.md) · [Grader access](GRADER_ACCESS.md) · [Working agreement](AGENTS.md)

## What is already set up

- **Telegram:** bot token, numeric owner and home destination; local replies confirmed.
- **Google:** own desktop OAuth client, Gmail/Calendar APIs, class-only identity and dedicated calendar; refresh and reads passed.
- **OpenAI:** separate local and cloud Hermes browser OAuth logins; the cloud grant’s real refresh/recovery passed.
- **Gemma:** installed `gemma4:e2b`; the application’s 65,536-token serving context was verified.
- **Tailscale:** my own tailnet, restricted agent tag and private laptop forwarding; permitted/denied client tests passed.
- **GCP:** project, billing, scoped identities, bucket, Artifact Registry and ten versioned secrets exist.
- **GitHub:** successful image publication, restricted OIDC, my required production review and a `main` branch rule.

Cloud deployment and its end-to-end acceptance remain separate. I do not run two Telegram pollers for the same bot.

## Private configuration

| File or value | Purpose |
| --- | --- |
| `.env.example` | Reviewed placeholders and expected variable names. |
| `.env` | Local runtime credentials and settings; ignored by Git. |
| `secrets/google-client.json` | Downloaded Google desktop OAuth client. |
| `state/hermes/auth.json` | Local native Hermes login. |
| `secrets/cloud-oauth/hermes/auth.json` | Separate cloud bootstrap login. |
| Secret Manager | Pinned cloud runtime credentials and private environment configuration. |

I never paste passwords, tokens, callback URLs or credential JSON into chat, Git or videos. The application’s recipient allowlist is separate from Google’s OAuth test-user list.

### Email readiness and fallback key

- **Email gate:** `A3_EMAIL_ENABLED` defaults to `false`. I enable it only after preparing dedicated class-only mailboxes with made-up data. A disabled gate prevents reads and sends without consuming an approval.
- **Current local profile:** after reporting promotional-mail cleanup on November 17, I enabled the gate and started fresh conversation/activity state. Earlier state is privately quarantined under ignored `private/`; it must not enter grader evidence or be restored into the clean profile.
- **NVIDIA:** the existing authorized key is now present in my ignored local `.env`; no new key is needed. Local paid calls remain disabled. A configured key alone does not enable paid inference.
- **Cloud release:** the new runtime requires the email gate in a reviewed, versioned runtime environment. The old image/configuration is not the updated release candidate.

## Run and test locally

From Assignment 3:

```sh
docker build --target runtime -t assignment3-agent:local .
docker compose up -d --no-build
```

1. I open `http://127.0.0.1:18080` and enter my private `API_SERVER_KEY` in the connection form.
2. In Telegram I send “Compare two fictional study plans in two sentences.”
3. I then send “What is 17 plus 25?” and check both replies arrive.
4. For a send demonstration, I first request a synthetic draft, use `/review DRAFT_ID`, inspect its exact payload and approve only that one send.

The two Telegram prompts already passed locally. Browser/API and Telegram checks do not begin the cloud observation window.

## Repeatable offline checks

```sh
docker build --target test -t a3-tests .
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 256 --memory 4g --cpus 4 \
  --tmpfs /tmp:rw,nosuid,nodev,size=512m \
  a3-tests .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/pytest
```

- My CI also checks lint, static security and installed-package advisories.
- The separate image gate checks the actual runtime and retains raw scanner results.
- Unknown High/Critical findings, profile drift or expired dispositions block release.
- I keep the native amd64 build in GitHub: the Mac emulator failed an upstream ACL syscall check, so I did not disable that test.
- The source downloader retries temporary errors at most four times and always verifies the pinned hash.

## Publish and deploy

1. I open **Actions → Approved Cloud Run Instance release → Run workflow**.
2. For a new image, I select `main`, choose **publish** and leave `image_digest` empty. I approve the production job when GitHub requests it.
3. I review the test/security results and the published immutable digest.
4. After a concrete release review, I approve deployment of that digest. **Publication alone does not deploy the bot.**
5. The local Telegram poller stops before the cloud poller starts. Local Ollama and Tailscale remain available.
6. I verify cloud health, authenticated chat, Telegram, local inference, services, schedules and recovery before starting observation.

My current published image and workflow links are in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). `config/release.json` and the manual production approval gate control deployment; I do not bypass a blocked gate.

## Start the 48-hour record

Only after all live acceptance checks pass, I run the observation helper inside the approved Cloud CLI container:

```sh
python scripts/observation.py --start path/to/live-acceptance.json
python scripts/observation.py --collect
```

- **Start:** records actual UTC time, freezes deployment and saves the manifest privately to GCS and Cloud Logging.
- **Collection:** exports structured events and reports elapsed time and heartbeat gaps separately.
- **Evidence:** 48 elapsed hours alone do not prove continuous coverage, delivery or absence of restarts.
- **Availability:** planned three-hour restarts stay disabled; access must remain available for grading and regrades within a reviewed budget.

## Remaining actions I handle

- [ ] Approve the exact deployment after the engineering release review.
- [ ] Follow [GRADER_ACCESS.md](GRADER_ACCESS.md) to test password-only sign-in to the dedicated accounts in another browser’s private window.
- [ ] Check Google consent-token age before grading; Testing-mode refresh tokens for these scopes expire after seven days.
- [ ] Keep the Mac awake and powered with Ollama and my own Tailscale connection during local demonstrations.
- [ ] Complete the Zoom video and provide my own reflection when the final system is ready.
- [ ] Put grader credentials only in Brightspace Comments using the supplied template.

## Account setup reference

<details>
<summary>Telegram setup if I need a fresh class-only bot</summary>

1. I use Telegram’s **BotFather** to create the bot and save its token as `TELEGRAM_BOT_TOKEN` in the ignored `.env`.
2. I send `/start` to the bot and verify the numeric owner ID before setting `TELEGRAM_ALLOWED_USERS`.
3. I test a normal reply and the exact-draft review flow. A model instruction or browser message is not approval.

[Official Telegram tutorial](https://core.telegram.org/bots/tutorial)

</details>

<details>
<summary>Google consent and dedicated calendar setup</summary>

1. I use only the disposable class-only account and create a dedicated synthetic calendar. I copy its Calendar ID into `GOOGLE_CALENDAR_ID`; I do not use `primary`.
2. I enable Gmail and Google Calendar APIs, configure the consent screen and add the account as a test user when the app is in Testing.
3. I create a **Desktop app** OAuth client and save the download to `secrets/google-client.json`.
4. In the approved setup container, `scripts/google_oauth.py` publishes only the local callback on `127.0.0.1:8765`. I review consent and select the intended test account.
5. The helper checks Gmail identity before privately saving credentials. I configure only the second synthetic mailbox in `EMAIL_ALLOWLIST`.

My scopes are `gmail.readonly`, `gmail.send` and `calendar.events.readonly`. Drafts live in my database, so Gmail draft-management scope is unnecessary. Calendar access remains read-only; the human grader can add events through the test account.

**403 access_denied:** I previously fixed this by adding the test account under **Google Auth Platform → Audience → Test users**, then completing fresh consent.

[Desktop OAuth](https://developers.google.com/identity/protocols/oauth2/native-app) · [Consent setup](https://developers.google.com/workspace/guides/configure-oauth-consent) · [Token expiry](https://developers.google.com/identity/protocols/oauth2#expiration)

</details>

<details>
<summary>OpenAI OAuth and cloud recovery</summary>

- I use `A3_PRIMARY_AUTH=oauth` and the verified model `gpt-6.1-sol`.
- `scripts/openai_oauth.py` uses Hermes’s native browser PKCE flow. Local and cloud receive distinct grants because refresh tokens rotate.
- The setup relay publishes host loopback 1455 to container 1456. It leaves my existing Codex login untouched; USC’s blocked device-code flow is not a fallback.
- Cloud startup restores the latest private authentication object. The pinned bootstrap secret is used only when no object exists.
- Refresh intent is recorded before rotation and the rotated grant is stored before returning it. An ambiguous/interrupted refresh blocks inference.
- If recovery reports a pending refresh, I complete a fresh separate cloud login and review a deliberate checkpoint reset. I do not delete markers or reuse stale tokens to bypass it.

Real bootstrap, rotation and fresh-profile recovery passed. Full deployed restart remains an acceptance check. OAuth files are excluded from ordinary workspace archives.

</details>

<details>
<summary>Private networking and resource limits</summary>

- Ollama stays on loopback. Private Tailscale Serve forwards only TCP 11434 for the authorized `tag:assignment3-agent`.
- My own tailnet is separate from USC’s network. The temporary administration token was revoked after scoped policy setup and positive/negative tests.
- The cloud enrollment key stays private. Tailscale uses non-root userspace networking and a SOCKS proxy; no public Funnel is configured.
- The reviewed cloud starting size is 1 vCPU / 2 GiB. Resource changes require measurements and a remaining-budget review.
- My $4 tracking budget is not a hard cap. The monthly budget remains in place after the custom-period API update was rejected.
- A restored paused cron job stays paused until deliberately resumed; startup preserves its history and pause state.

[Tailscale policy](https://tailscale.com/docs/reference/syntax/policy-file) · [Serve](https://tailscale.com/docs/reference/tailscale-cli/serve) · [Cloud CLI authentication](https://docs.cloud.google.com/sdk/docs/authenticate)

</details>
