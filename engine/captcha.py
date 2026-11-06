"""CapSolver client for solving Cloudflare challenge pages (best-effort).

Uses CapSolver's AntiCloudflareTask, which returns a ``cf_clearance`` cookie
and a matching user-agent. Applying those in a fresh browser context lets the
scraper pass the "checking your browser" interstitial on Cloudflare-fronted
brokers. Returns None cleanly on any failure so scrapers fall back to an
honest "blocked" status.
"""
import asyncio
from urllib.parse import urlparse

import httpx

CREATE = "https://api.capsolver.com/createTask"
RESULT = "https://api.capsolver.com/getTaskResult"


async def _post(url: str, payload: dict, key: str) -> dict:
    payload = {**payload, "clientKey": key}
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(url, json=payload)
        return r.json()


async def _poll(settings, task_id: str, timeout_s: int = 150) -> dict | None:
    for _ in range(timeout_s // 3):
        await asyncio.sleep(3)
        r = await _post(RESULT, {"taskId": task_id}, settings.captcha_api_key)
        if r.get("status") == "ready":
            return r.get("solution")
        if r.get("status") == "failed":
            return None
    return None


def _normalize_cookies(sol: dict, url: str) -> list:
    """CapSolver returns cookies as a dict {cf_clearance: ...} or a list."""
    host = urlparse(url).hostname or ""
    domain = host[4:] if host.startswith("www.") else host

    raw = sol.get("cookies")
    if isinstance(raw, dict):
        cf = raw.get("cf_clearance")
        if cf:
            return [{"name": "cf_clearance", "value": cf, "domain": domain, "path": "/"}]
        return []
    if isinstance(raw, list):
        return raw
    return []


async def solve_cloudflare(settings, url: str, proxy: str, retries: int = 8) -> dict | None:
    """Solve a Cloudflare challenge. Returns {user_agent, cookies} or None.

    Retries a few times because rotating residential IPs are hit-or-miss:
    each attempt goes out through a fresh IP, so a pre-flagged IP is replaced.
    """
    if not settings.captcha_api_key:
        return None

    for _ in range(retries):
        task = {
            "type": "AntiCloudflareTask",
            "websiteURL": url,
            "proxy": proxy,
        }
        r = await _post(CREATE, {"task": task}, settings.captcha_api_key)
        if r.get("errorId") != 0:
            continue

        sol = await _poll(settings, r.get("taskId"))
        if not sol:
            continue

        cookies = _normalize_cookies(sol, url)
        if not cookies:
            continue

        return {
            "user_agent": sol.get("userAgent"),
            "cookies": cookies,
        }
    return None
