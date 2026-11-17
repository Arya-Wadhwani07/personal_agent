# I developed this file with Codex assistance; see PROCESS_LOG.md.
from personal_agent.routing import Router
from personal_agent.settings import Settings


def test_private_proxy_is_scoped_to_local_client():
    s = Settings(
        api_key="public-" + "a" * 32,
        internal_key="internal-" + "b" * 32,
        local_url="http://gemma-laptop.example.ts.net:11434/api/chat",
        local_proxy="socks5://127.0.0.1:1055",
    )
    router = Router(s)
    # Cloud and local have separate transports, so local proxy cannot silently capture cloud credentials.
    assert router.cloud is not router.local
    assert router.cloud._trust_env is False
    assert router.local._trust_env is False
