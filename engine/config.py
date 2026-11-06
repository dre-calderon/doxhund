"""Doxhund engine configuration.

All settings load from environment variables (prefix ``DOXHUND_``) or a
``.env`` file in the repo root. No secrets are hardcoded anywhere.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="DOXHUND_",
        extra="ignore",
    )

    # "demo" (no network, synthetic preview) or "live" (Playwright scrapers)
    mode: str = "demo"

    # Comma-separated allowed CORS origins, or "*"
    cors_origins: str = "*"

    # --- Scraping ---
    proxy_url: str | None = None
    captcha_provider: str = "capsolver"  # capsolver | 2captcha (not yet wired)
    captcha_api_key: str | None = None
    request_timeout_s: int = 15
    max_brokers_per_scan: int = 4

    # --- Rate limiting (in-memory sliding window per client IP) ---
    rate_limit_requests: int = 10
    rate_limit_window_s: int = 60

    # Optional Cloudflare Turnstile site-verify secret (enables challenge gate)
    turnstile_secret: str | None = None

    # --- API authentication ---
    # Tier-1 shared secret. If set, POST /api/scan requires an
    # "Authorization: Bearer <key>" header. Unset = open (dev mode).
    api_key: str | None = None

    # --- Scraper launch ---
    # Browser channel passed to Playwright ("chrome" = installed Google Chrome).
    # Empty string or None = Playwright's bundled Chromium.
    browser_channel: str = "chrome"

    @property
    def cors_origin_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_brokers() -> List[dict]:
    """Load the broker catalog from catalog/brokers.json."""
    import json

    path = REPO_ROOT / "catalog" / "brokers.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("brokers", [])
