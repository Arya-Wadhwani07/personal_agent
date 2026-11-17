# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Browser interaction checks against local UI; model replies are explicitly mocked."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("/results")
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.route("**/health", lambda route: route.fulfill(json={"status": "ready"}))
    assets = Path(__file__).resolve().parents[1] / "src/personal_agent/static"
    for asset, route_path in (("index.html", "/"), ("app.js", "/app.js"), ("app.css", "/app.css")):
        page.route("http://a3.test" + route_path, lambda route, request, name=asset: route.fulfill(path=str(assets / name)))
    reply = {
        "content": "I have a fictional project meeting at 10:00 AM. My afternoon has space for focused work. Email drafts are ready for review in Telegram."
    }
    page.route(
        "**/v1/chat/completions",
        lambda route: route.fulfill(
            status=reply.get("status", 200),
            json={"error": "Synthetic service unavailable", "choices": [{"message": {"role": "assistant", "content": reply["content"]}}]}
        ),
    )
    draft = {
        "id": "a" * 24,
        "topic": "Synthetic AI topic",
        "body": "An original test draft.",
        "sources": ["https://example.test/article"],
        "status": "draft",
        "revision": "r1",
    }
    actions = []
    page.route("**/content", lambda route: route.fulfill(json={"items": [draft]}))

    def review(route):
        payload = route.request.post_data_json
        if payload["revision"] != draft["revision"]:
            route.fulfill(status=400, json={"error": "Draft changed; refresh it."})
            return
        actions.append(payload["action"])
        if payload["action"] == "revise":
            draft["body"] = payload["body"]
        else:
            draft["status"] = payload["action"]
        draft["revision"] += "x"
        route.fulfill(json={"status": "updated"})

    page.route("**/content/*/review", review)
    page.goto("http://a3.test/", wait_until="networkidle")
    if not (page.get_by_label("Message my assistant").is_disabled()):
        raise RuntimeError("Browser verification failed")
    page.get_by_label("Private access key").fill("synthetic-ui-key-" + "x" * 32)
    page.get_by_role("button", name="Connect", exact=True).click()
    page.get_by_label("Message my assistant").fill("Help me plan my fictional day.")
    page.get_by_role("button", name="Send", exact=False).click()
    page.get_by_text(reply["content"], exact=True).wait_for()
    page.get_by_text("My content drafts", exact=True).click()
    page.get_by_role("button", name="Refresh drafts", exact=True).click()
    editor = page.get_by_label("Revise draft: Synthetic AI topic")
    editor.fill("My revised synthetic draft.")
    page.get_by_role("button", name="Save revision", exact=True).click()
    page.wait_for_function(
        "document.querySelector('.content-draft textarea')?.value === 'My revised synthetic draft.'"
    )
    page.evaluate(
        "Object.defineProperty(navigator, 'clipboard', {value:{writeText:async text=>{window.copiedText=text}}})"
    )
    page.get_by_role("button", name="Copy draft", exact=True).click()
    page.get_by_text("Draft · copied", exact=True).wait_for()
    if page.evaluate("window.copiedText") != "My revised synthetic draft.":
        raise RuntimeError("Clipboard review failed")
    page.screenshot(path=str(OUT / "desktop.png"), full_page=True)
    page.get_by_role("button", name="Dismiss", exact=True).click()
    page.get_by_text("Draft · dismiss", exact=True).wait_for()
    if actions != ["revise", "copied", "dismiss"]:
        raise RuntimeError("Content review workflow failed")
    reply["content"] = (
        '<img src=x onerror="window.injected=true"><script>window.injected=true</script>'
    )
    page.get_by_label("Message my assistant").fill(
        "Show the synthetic unsafe markup fixture as text."
    )
    page.get_by_role("button", name="Send", exact=False).click()
    page.get_by_text(reply["content"], exact=True).wait_for()
    if not (page.evaluate("window.injected === undefined")):
        raise RuntimeError("Browser verification failed")
    if not (page.locator("#messages img, #messages script").count() == 0):
        raise RuntimeError("Browser verification failed")
    reply["status"] = 503
    page.get_by_label("Message my assistant").fill("Preserve my synthetic unsent request.")
    page.get_by_role("button", name="Send", exact=False).click()
    page.get_by_text("Synthetic service unavailable", exact=True).wait_for()
    if page.get_by_label("Message my assistant").input_value() != "Preserve my synthetic unsent request.":
        raise RuntimeError("Failed-request draft was lost")
    if page.get_by_label("Message my assistant").is_disabled():
        raise RuntimeError("Composer did not recover")
    page.get_by_role("button", name="New chat", exact=True).click()
    if page.get_by_label("Message my assistant").input_value():
        raise RuntimeError("New chat retained the previous draft")
    page.set_viewport_size({"width": 390, "height": 844})
    if not (page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")):
        raise RuntimeError("Browser verification failed")
    page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
    pending = []
    page.route("**/content", lambda route: pending.append(route))
    with page.expect_request("**/content"):
        page.get_by_role("button", name="Refresh drafts", exact=True).click()
    page.get_by_role("button", name="Sign out & clear chat", exact=True).click()
    if not pending:
        raise RuntimeError("Late-response fixture did not start")
    pending[0].fulfill(json={"items": [draft]})
    page.wait_for_timeout(100)
    if page.locator(".content-draft").count():
        raise RuntimeError("Late response restored drafts after signout")
    if not (page.get_by_label("Message my assistant").is_disabled()):
        raise RuntimeError("Browser verification failed")
    if not (page.get_by_label("Private access key").input_value() == ""):
        raise RuntimeError("Browser verification failed")
    if not (page.evaluate("localStorage.length + sessionStorage.length") == 0):
        raise RuntimeError("Browser verification failed")
    browser.close()
print(
    json.dumps(
        {
            "browser": "Chromium",
            "checks": [
                "login",
                "chat",
                "failed-request draft recovery and composer reset",
                "plain-text XSS rejection",
                "content revision, copy and dismiss",
                "new chat",
                "mobile no horizontal overflow",
                "signout and late-response isolation",
                "no browser storage",
            ],
            "model": "mocked",
            "result": "passed",
        }
    )
)
