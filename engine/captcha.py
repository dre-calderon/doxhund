"""CapSolver client for solving Cloudflare challenge pages (best-effort).

Uses CapSolver's AntiCloudflareTask, which returns a ``cf_clearance`` cookie
and a matching user-agent. Applying those in a fresh browser context lets the
scraper pass the "checking your browser" interstitial on Cloudflare-fronted
brokers. Returns None cleanly on any failure so scrapers can fall back to a
honest "blocked" status.
"""
import asyncio

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


async def solve_cloudflare(settings, url: str, proxy: str) -> dict | None:
    """Solve a Cloudflare challenge. Returns {user_agent, cookies} or None."""
    if not settings.captcha_api_key:
        return None

    task = {
        "type": "AntiCloudflareTask",
        "websiteURL": url,
        "proxy": proxy,
    }
    r = await _post(CREATE, {"task": task}, settings.captcha_api_key)
    if r.get("errorId") != 0:
        return None

    sol = await _poll(settings, r.get("taskId"))
    if not sol:
        return None

    return {
        "user_agent": sol.get("userAgent"),
        "cookies": sol.get("cookies") or [],
    }
