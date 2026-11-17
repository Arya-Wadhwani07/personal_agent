# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Portable source-ledger review. No networking, publication or file writes."""
import argparse
import ipaddress
import json
import sys
from urllib.parse import urlsplit


def public_reference(url):
    if not isinstance(url, str) or not 1 <= len(url) <= 1000:
        raise ValueError("Source URL length is invalid")
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        raise ValueError("Source URL is malformed") from None
    if parsed.scheme != "https" or parsed.username is not None or port not in (None, 443):
        raise ValueError("Sources need credential-free HTTPS references")
    if not host or "." not in host or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Local source addresses are excluded")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and not address.is_global:
        raise ValueError("Private source addresses are excluded")
    if host == "linkedin.com" or host.endswith(".linkedin.com"):
        raise ValueError("LinkedIn scraping sources are excluded")
    return url


def review(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a draft object")
    topic, body = payload.get("topic"), payload.get("body")
    if not isinstance(topic, str) or not 1 <= len(topic.strip()) <= 200:
        raise ValueError("Topic needs 1–200 characters")
    if not isinstance(body, str) or not 1 <= len(body.strip()) <= 3000:
        raise ValueError("Draft needs 1–3000 characters")
    sources, claims = payload.get("sources"), payload.get("claims")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 5:
        raise ValueError("I need one to five sources")
    ledger = []
    for number, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            raise ValueError("Each source needs a URL, title and short evidence note")
        url = public_reference(source.get("url"))
        title, note = source.get("title"), source.get("note")
        if not isinstance(title, str) or not 1 <= len(title) <= 250:
            raise ValueError("Source title is missing or too long")
        if not isinstance(note, str) or not 1 <= len(note) <= 1000:
            raise ValueError("Source evidence note is missing or too long")
        ledger.append({"id": number, "url": url, "title": title, "note": note})
    if len({s["url"] for s in ledger}) != len(ledger):
        raise ValueError("Sources must be distinct")
    if not isinstance(claims, list) or not 1 <= len(claims) <= 20:
        raise ValueError("I need at least one explicit claim-to-source link")
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Claim must be an object")
        text, source = claim.get("text"), claim.get("source")
        if not isinstance(text, str) or not text.strip() or text not in body:
            raise ValueError("Each claim must identify exact text from my draft")
        if type(source) is not int or not 1 <= source <= len(ledger):
            raise ValueError("Each claim must reference a listed source number")
    history = payload.get("previous_topics", [])
    if not isinstance(history, list) or len(history) > 1000 or any(not isinstance(t, str) for t in history):
        raise ValueError("Topic history must be a bounded list")
    def normalize(text):
        return " ".join(text.casefold().split())
    if normalize(topic) in {normalize(t) for t in history}:
        raise ValueError("This topic is already in my history")
    return {
        "status": "ready_for_human_review", "topic": topic.strip(), "body": body.strip(),
        "sources": ledger, "claims": claims, "publishing": False,
        "limits": "I still check source accuracy, originality and tone before posting manually.",
    }


def example():
    return {
        "topic": "A fictional team tests approval gates",
        "body": "My fictional team tests an approval gate before every email send. That small check makes the review process easier to explain.",
        "sources": [{"url": "https://example.org/synthetic-study", "title": "Synthetic fixture",
                     "note": "Made-up test data: the fictional team verifies its approval gate."}],
        "claims": [{"text": "tests an approval gate before every email send", "source": 1}],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            payload = example()
        else:
            raw = sys.stdin.read(20001)
            if len(raw) > 20000:
                raise ValueError("Draft input exceeds 20,000 characters")
            payload = json.loads(raw)
        print(json.dumps(review(payload), ensure_ascii=True))
    except (ValueError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
