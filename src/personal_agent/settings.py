# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Explicit, validated configuration. No implicit home-directory or dotenv reads."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    api_key: str
    internal_key: str
    state_dir: Path = Path("/state")
    primary_auth: str = "api_key"
    primary_key: str = ""
    primary_model: str = ""
    primary_url: str = "https://api.openai.com/v1/responses"
    paid_calls: bool = False
    search_call_limit: int = 0
    nvidia_call_limit: int = 0
    openai_call_limit: int = 0
    simulate_primary_429: bool = False
    cloud_key: str = ""
    cloud_model: str = "nvidia/nemotron-3-ultra-550b-a55b"
    cloud_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"
    local_url: str = "http://host.docker.internal:11434/api/chat"
    local_model: str = "gemma4:e2b"
    local_proxy: str = ""
    simulate_429: bool = False
    max_body: int = 131072
    max_response: int = 1048576
    timeout: float = 90
    max_inflight: int = 4
    gmail_refresh_token: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    calendar_id: str = ""
    email_allowlist: tuple[str, ...] = ()
    email_enabled: bool = False
    telegram_user_id: str = ""
    telegram_token: str = ""
    tavily_key: str = ""
    bucket: str = ""
    latitude: float = 34.05
    longitude: float = -118.24
    timezone: str = "America/Los_Angeles"

    def __post_init__(self):
        if min(len(self.api_key), len(self.internal_key)) < 32:
            raise ValueError(
                "Independent public/internal keys must each have at least 32 characters"
            )
        if self.api_key == self.internal_key:
            raise ValueError("Public and internal credentials must differ")
        for limit in (self.search_call_limit, self.nvidia_call_limit, self.openai_call_limit):
            if type(limit) is not int or not 0 <= limit <= 1000:
                raise ValueError("Paid call limits must be integers between 0 and 1000")
        if self.primary_auth not in ("api_key", "oauth"):
            raise ValueError("Unsupported primary authentication mode")
        if self.primary_url != "https://api.openai.com/v1/responses":
            raise ValueError("OpenAI endpoint must be the fixed Responses API")
        if self.cloud_url != "https://integrate.api.nvidia.com/v1/chat/completions":
            raise ValueError("NVIDIA endpoint must be fixed")
        cloud = urlsplit(self.cloud_url)
        if (
            cloud.scheme != "https"
            or cloud.hostname != "integrate.api.nvidia.com"
            or cloud.username
        ):
            raise ValueError("Cloud inference must use the approved NVIDIA endpoint")
        local = urlsplit(self.local_url)
        if local.scheme not in ("http", "https") or not local.hostname or local.username:
            raise ValueError("Invalid private Ollama endpoint")
        if not 1 <= self.max_inflight <= 16 or not 1 <= self.timeout <= 180:
            raise ValueError("Resource bounds invalid")

    @classmethod
    def from_env(cls):
        e = os.environ
        return cls(
            api_key=e.get("API_SERVER_KEY", ""),
            internal_key=e.get("A3_INTERNAL_KEY", ""),
            state_dir=Path(e.get("A3_STATE_DIR", "/state")),
            primary_auth=e.get("A3_PRIMARY_AUTH", "oauth"),
            primary_key=e.get("A3_OPENAI_API_KEY", ""),
            primary_model=e.get("A3_OPENAI_MODEL", ""),
            paid_calls=e.get("A3_PAID_CALLS", "false").lower() == "true",
            search_call_limit=int(e.get("A3_SEARCH_CALL_LIMIT", "0")),
            nvidia_call_limit=int(e.get("A3_NVIDIA_CALL_LIMIT", "0")),
            openai_call_limit=int(e.get("A3_OPENAI_CALL_LIMIT", "0")),
            simulate_primary_429=e.get("A3_SIMULATE_PRIMARY_429", "false").lower() == "true",
            cloud_key=e.get("NVIDIA_API_KEY", ""),
            cloud_model=e.get("NVIDIA_MODEL", cls.cloud_model),
            local_url=e.get("OLLAMA_URL", cls.local_url),
            local_model=e.get("OLLAMA_MODEL", cls.local_model),
            local_proxy=e.get("OLLAMA_PROXY", ""),
            simulate_429=e.get("A3_SIMULATE_429", "false").lower() == "true",
            gmail_refresh_token=e.get("GOOGLE_REFRESH_TOKEN", ""),
            google_client_id=e.get("GOOGLE_CLIENT_ID", ""),
            google_client_secret=e.get("GOOGLE_CLIENT_SECRET", ""),
            calendar_id=e.get("GOOGLE_CALENDAR_ID", ""),
            email_enabled=e.get("A3_EMAIL_ENABLED", "false").lower() == "true",
            email_allowlist=tuple(
                x.strip().lower() for x in e.get("EMAIL_ALLOWLIST", "").split(",") if x.strip()
            ),
            telegram_user_id=e.get("TELEGRAM_ALLOWED_USERS", ""),
            telegram_token=e.get("TELEGRAM_BOT_TOKEN", ""),
            tavily_key=e.get("TAVILY_API_KEY", ""),
            bucket=e.get("A3_STATE_BUCKET", ""),
        )
