# My Class-Only Account Setup

## My November 17 integration checkpoint

My selected primary is Hermes OpenAI browser OAuth with `gpt-6.1-sol`; a real synthetic inference passed. NVIDIA remains fallback and Gemma 4 E2B handles local work. Google OAuth refresh, Gmail identity and dedicated-calendar access passed; the Telegram owner is configured. My project is `assignment3-515003` with a $4 total ceiling. My Mac is connected to my own Tailscale network, and isolated Google Cloud CLI sign-in verified the active project and enabled billing. Private inference access is not yet configured. Both published implementation checkpoints passed GitHub CI. Paid API calls remain disabled. Deployment and final evidence are unfinished; [my implementation status](IMPLEMENTATION_STATUS.md) distinguishes verified results from remaining work.

I use only throwaway accounts and fictional messages/events. Real tokens stay in Assignment 3's ignored `.env` and `secrets/` paths; I do not paste them into chat, GitHub, screenshots or the recording.

## 1. My private configuration

My setup helper has created an ignored `.env` within Assignment 3 with two different random access keys of at least 32 characters. I preserve that file rather than overwrite existing values. For a fresh checkout, the helper initializes it from `.env.example` without displaying secrets. I fill the remaining fields only when the corresponding class-only service is ready. Docker runtime files are authorized; project files remain inside Assignment 3.

## 2. My Telegram bot

1. From my assignment-only Telegram setup, I open the official **@BotFather**, send `/newbot`, and choose a bot name and username.
2. I save the returned token as `TELEGRAM_BOT_TOKEN` in `.env`.
3. I open my new bot and send `/start`. My setup check can read this pending update and display its numeric sender ID without displaying the token. I save the intended owner ID as `TELEGRAM_ALLOWED_USERS`; this implementation expects one owner.
4. After the gateway is connected, I test a normal request/reply. For email, I request a draft, send `/review DRAFT_ID`, inspect the complete recipient/subject/body, then choose the approval button. A model instruction or a browser message cannot approve a send.

BotFather is Telegram's documented bot-creation route. I keep the token out of browser URLs and shell history. [Official Telegram tutorial](https://core.telegram.org/bots/tutorial)

## 3. My throwaway Gmail and dedicated calendar

1. I create or choose a throwaway Google account containing no personal mail. Q01 permits a second temporary mailbox playing the fictional correspondent; only these synthetic recipients belong in my allowlist. I create a separate calendar named **Assignment 3 — Synthetic**, add fictional events, and copy its **Calendar ID** from calendar settings into `GOOGLE_CALENDAR_ID`. I do not use `primary`.
2. After selecting my GCP project, I enable **Gmail API** and **Google Calendar API** there. I configure the Google Auth Platform consent screen and add my throwaway account as a test user if the app is in Testing.
3. I create an OAuth client with application type **Desktop app**. I save its downloaded JSON as `secrets/google-client.json` inside Assignment 3.
4. I run `scripts/google_oauth.py` inside the approved container setup profile, publishing only `127.0.0.1:8765`. The helper prints a consent URL. I open it, deliberately choose the throwaway account, and review the requested scopes. It validates that Gmail reports the exact class-only email address I supplied, then saves the client settings and refresh token to `.env` without printing tokens.
5. I populate `EMAIL_ALLOWLIST` with only the intended synthetic test recipients, separated by commas. I prepare a few fictional unread/flagged messages and upcoming meetings.

My selected scopes are `gmail.readonly`, `gmail.send`, and `calendar.events.readonly`, using their full Google scope URLs. Drafts are held in my application database, so this version does not request Gmail draft-management permissions. Calendar access is currently read-only. The code gate, rather than the send scope, controls every actual send. Google documents the desktop loopback consent flow and PKCE. [Desktop OAuth guide](https://developers.google.com/identity/protocols/oauth2/native-app)

I check consent/refresh-token expiry before freezing the deployment. External applications in Testing can receive seven-day refresh tokens for these scopes; merely obtaining a token does not establish access through regrades. Production/verification requirements and an authorized renewal plan must be settled before claiming continuous grading access. [Google token-expiration guidance](https://developers.google.com/identity/protocols/oauth2#expiration)

## 4. My pending cloud and inference setup

I supplied project `assignment3-515003` and a $4 total ceiling for hosting and paid checks. I reserve funds for storage, networking and grading availability before enabling paid API calls. A budget alert is not a hard spending cap; deployment remains gated.

My installed `gemma4:e2b` completed direct local checks and a real Hermes memory-tool turn at a served context of 65,536. Local Docker uses `host.docker.internal`; deployment must instead use the approved Tailscale laptop address and userspace proxy. The laptop endpoint must not be exposed publicly or broadly on my LAN.

Before deployment, I also need a dedicated state bucket, runtime service account, Secret Manager entries, GitHub deployment authentication, and verified Tailscale grants. Secret values go through private setup/Secret Manager, never workflow YAML or GitHub issue text. My isolated Google Cloud CLI sign-in and read-only project/billing checks passed. Gmail and Calendar APIs are enabled; Cloud Run, Artifact Registry, Secret Manager and deployment identity setup remain pending. No cloud resources have been provisioned.

## 5. My final provider and grading checklist

My selected primary is Hermes OpenAI browser OAuth, with NVIDIA fallback and local Gemma 4 E2B. I use `A3_PRIMARY_AUTH=oauth` and an account-supported `A3_OPENAI_MODEL`. `scripts/openai_oauth.py` uses the pinned Hermes browser PKCE flow and stores credentials in my project, never in my existing Codex home. Docker publishes host loopback 1455 to container 1456; its relay reaches Hermes's container-loopback listener. USC blocks device-code login, so a busy browser port fails instead of switching flows. Local and cloud receive separate sign-ins because refresh tokens rotate. The proxy forwards Hermes's own authenticated requests to the fixed Codex backend; it does not treat OAuth tokens as OpenAI API keys. Live OAuth inference passed; durable cloud refresh recovery remains a release blocker.

I configure my own Tavily key for direct search, not a wrapper around bundled search. My README identifies the work and use of each of the four skills. Every email send, including a synthetic test send, requires explicit human approval.

Before grading, I verify browser access according to G, Telegram functionality, laptop/Ollama/Tailscale availability, actual served context and complete local tool use. Q01's older provisional access post does not replace the detailed access instructions.

I keep planned three-hour restarts disabled. Measured 1 vCPU/4 GiB is permitted if necessary, subject to my budget and documented justification. I keep final-model logs/video; primary-model changes require new evidence, while minor non-model fixes do not require a new full 48-hour run. Graders test after End Date and again 48 hours later; I retain availability through regrades and record actual incidents. [Clarification register](CLARIFICATIONS.md)

## My Google consent troubleshooting record

I enabled Gmail and Google Calendar APIs in my chosen project. The initial 403 `access_denied` was a Testing-audience issue: I added the class-only sign-in address under **Google Auth Platform → Audience → Test users**. A fresh consent callback then saved credentials successfully. Token refresh, Gmail identity and read-only access to my dedicated calendar passed. The application recipient allowlist is separate from Google's test-user list. Exact account addresses and calendar identifiers stay in ignored configuration. [Google OAuth setup](https://developers.google.com/workspace/guides/configure-oauth-consent)

## My November 17 grader-access update

My Tailscale 1.104.7 installer is available in the visible, Git-ignored `setup_downloads/` folder inside Assignment 3, with the original download retained in the ignored cache. macOS verified the Tailscale Inc. developer signature and Apple notarization outside the restricted command sandbox; the initial sandboxed trust check could not establish validity. I completed the macOS administrator approval and sign-in. After initially joining the shared USC network, I connected this Mac to a separate tailnet I control. The targeted status check reports Running/online and administrator access. No public Funnel or inference exposure is authorized by installation alone. [Official macOS download](https://tailscale.com/download/mac)

I confirmed that both configured Gmail accounts are dedicated class-only accounts with made-up data. My Gmail API integration uses OAuth, so I follow Q13's preferred Path 1 for grader access. Changing account security settings remains my explicit action; Codex has not disabled 2-Step Verification, changed passwords, published the consent app or collected backup codes. I still need the grader-style sign-in and token-validity check. Q14 separates live cloud grading from the Zoom local-Gemma video without removing the detailed video steps. My [grader-access checklist](GRADER_ACCESS.md) records both paths and the private submission fields; passwords/codes never belong in this repository.

## My private network and cloud setup checkpoint

My proposed rule allows only `tag:assignment3-agent` to reach the laptop's TCP port 11434. The prepared private policy is in `secrets/tailscale-policy.json`; it includes positive access assertions and negative assertions for other ports, UDP and a denied test identity. I review the existing owned-tailnet policy before applying it, retain a private backup and use the policy ETag to avoid overwriting concurrent edits. No university-wide rules are changed. Policy validation and an actual allowed/denied connection test remain required before I claim private inference works. Ollama stays on loopback; private Tailscale Serve forwards only the selected port after the rules are verified. [Policy syntax](https://tailscale.com/docs/reference/syntax/policy-file), [Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve)

For the temporary setup credential, I open **Settings → Keys → API access tokens → Generate access token** in my own Tailscale console, choose one day, and save only the token in the ignored `secrets/tailscale-api-key.txt`. A device auth key is a different credential. This temporary administration token stays out of the agent runtime and is revoked after setup. I do not share it in chat or commit it. [API authentication](https://tailscale.com/docs/reference/tailscale-api)

My Google Cloud CLI runs in the isolated `a3-gcloud` container with its configuration under ignored `.gcloud/`. I used its native browser login and supplied the one-time code through `secrets/gcp-login-code.txt`; the helper cleared the code after consuming it. Project access and billing are verified. Login does not create resources or establish a hard spending cap. My release script rejects a different project, a non-finite budget, and a budget above the reviewed $4 ceiling; actual usage monitoring and a funded availability window are still deployment prerequisites. [Google Cloud CLI authentication](https://docs.cloud.google.com/sdk/docs/authenticate)
