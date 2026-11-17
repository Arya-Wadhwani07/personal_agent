# My Class-Only Account Setup

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

I still need to provide the chosen GCP project ID and total spending limit. Assignment 2's existing project is not automatically authorized for this assignment. Cloud provisioning and paid OpenAI/Claude/NIM/Tavily calls remain paused until these inputs are supplied.

My installed `gemma4:e2b` completed direct local checks and a real Hermes memory-tool turn at a served context of 65,536. Local Docker uses `host.docker.internal`; deployment must instead use the approved Tailscale laptop address and userspace proxy. The laptop endpoint must not be exposed publicly or broadly on my LAN.

Before deployment, I also need a dedicated state bucket, runtime service account, Secret Manager entries, GitHub deployment authentication, and verified Tailscale grants. Secret values go through private setup/Secret Manager, never workflow YAML or GitHub issue text. No cloud command in this guide has been executed yet.

## 5. My final provider and grading checklist

My working provider plan is OpenAI API primary, NVIDIA fallback and local Gemma 4 E2B. Claude API is an accepted primary alternative; Edu/Codex OAuth is a separate entitlement. I will select exact cloud model IDs and supply the spending limit before paid verification. The current settings and adapter are NVIDIA-only: adding an OpenAI key alone does not enable this plan. Provider-specific private setup instructions must follow the tested migration; I do not put keys in Markdown.

I configure my own Tavily key for direct search, not a wrapper around bundled search. My README identifies the work and use of each of the four skills. Every email send, including a synthetic test send, requires explicit human approval.

Before grading, I verify browser access according to G, Telegram functionality, laptop/Ollama/Tailscale availability, actual served context and complete local tool use. Q01's older provisional access post does not replace the detailed access instructions.

I keep planned three-hour restarts disabled. Measured 1 vCPU/4 GiB is permitted if necessary, subject to my budget and documented justification. I keep final-model logs/video; primary-model changes require new evidence, while minor non-model fixes do not require a new full 48-hour run. Graders test after End Date and again 48 hours later; I retain availability through regrades and record actual incidents. [Clarification register](CLARIFICATIONS.md)
