# My Grader Access Checklist

I follow the professor's additional Q13/Q14 clarification and the supplied [CloudRunSettings.txt](../docs/Assignment3_local_Gemma_scripts/CloudRunSettings.txt). My existing ACCESS-01/02/03 and VIDEO requirements already cover these obligations; no new requirement IDs are needed.

## My selected account path

I confirmed that both configured email accounts are dedicated class-only accounts containing made-up data. My agent uses Gmail API OAuth and a dedicated Google Calendar. It does not use an IMAP/SMTP App Password, so **Path 1 is my selected grader-login path**.

Before submission, I personally verify that the dedicated test account permits password-only sign-in with 2-Step Verification off. This change is limited to the disposable assignment account. No personal or USC email/calendar login belongs in my submission. Using USC ChatGPT Edu for the separate OpenAI model login remains distinct from the prohibited use of a USC mailbox as the test mailbox.

I apply the same access rules to a separate calendar account if I use one. A Calendar ID alone is not a grader login: the grader needs the account that can add a fictional event to the calendar my agent monitors. Read-only Calendar API access for my assistant is compatible with the grader signing into that test account to create events.

## My OAuth validity check

My consent app is currently in Testing. The professor specifies seven-day refresh-token expiry for this configuration. Before grading I either reauthorize shortly beforehand or review and explicitly approve an appropriate Production transition. I record the actual authorization time and expected validity privately, including the repeat check and regrade period. A successful refresh today is not proof of access throughout grading.

Account security changes can invalidate access, so I repeat the agent's refresh/calendar/email checks after any authorized account change. I do not change the submitted password afterward.

## My conditional App Password alternative

Path 2 applies only if I change the integration to use a Google App Password. In that case, I retain 2-Step Verification, remove Google Authenticator if configured as the professor instructs, and submit at least four unused backup codes. Each code is single-use. A code consumed during my sign-in rehearsal is excluded, and I still need at least four unused codes for submission. Regenerating the set invalidates the previously submitted codes; I do not regenerate it or change the password after submission. Additional Google device checks can still interfere, which is why I selected OAuth/Path 1.

## My grader-style rehearsal

I open an Incognito window in a different browser and sign in to every required test account exactly as the grader will. I verify mailbox access and the ability to add a synthetic event to the monitored calendar. I then verify that the agent notices the intended test data and delivers the alert. Account sign-in, provider connectivity and actual proactive delivery are separate checks.

## My private submission fields

For Hermes, I fill the supplied template directly in **Brightspace Comments** with my Cloud Run URL, API Server Key, test email login/password, calendar login/password and selected 2-Step Verification path. Path 2 additionally needs at least four unused backup codes. These values never go into the ZIP, README, Git history, screenshots or video, and I do not send them in this chat.

The OpenClaw alternative uses its Tailscale share link and agent URL instead of the Hermes access fields; it does not change my selected Hermes architecture. I review every submitted field using the original template. Failed grader account access can lose the corresponding component's points.

## My two grading phases

- My cloud model and assistant behavior are assessed on the **live Cloud Run Instance**.
- My local Gemma behavior is assessed from the **Zoom video**.

I still follow Assignment3_Video_Instructions.pdf and Assignment3_local_Gemma.pdf, including the prescribed deployed-browser requests, local availability changes, routing logs, messaging and proactive evidence. The companion Video_Steps.txt files help order the demonstration but do not replace the PDFs. Genuine availability, final-model evidence and the grading freeze remain required.

## My current evidence

Google browser consent, token refresh, expected Gmail identity and a read of three dedicated-calendar events passed. I confirmed a live Telegram reply. These checks do not prove password-only grader login, alert injection, final cloud access, seven-day/regrade coverage or video completion. Those items remain open.
