"""Doxhund recon API (FastAPI).

Run from the repo root with a venv active:

    uvicorn engine.api:app --host 0.0.0.0 --port 8000

Live mode additionally requires ``playwright install chromium`` and a proxy.
"""
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.config import get_settings
from engine.recon import ReconScanner

settings = get_settings()

app = FastAPI(title="Doxhund Recon API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class _RateLimiter:
    """In-memory sliding-window rate limiter (no external deps)."""

    def __init__(self, limit: int, window_s: int):
        self.limit = limit
        self.window_s = window_s
        self._hits: dict = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        dq = self._hits[key]
        while dq and now - dq[0] > self.window_s:
            dq.popleft()
        if len(dq) >= self.limit:
            return False
        dq.append(now)
        return True


_limiter = _RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_s)


def _client_ip(request: Request) -> str:
    # Prefer Cloudflare's cf-connecting-ip (trusted at the edge), then
    # x-forwarded-for's leftmost client entry, then the socket peer.
    cf = request.headers.get("cf-connecting-ip")
    if cf:
        return cf.strip()
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _require_key(authorization: str | None = Header(default=None)) -> None:
    """Tier-1 API-key gate. Open when no key is configured (dev mode)."""
    if not settings.api_key:
        return
    expected = f"Bearer {settings.api_key}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    return


async def _verify_turnstile(token: str) -> bool:
    """Optional Cloudflare Turnstile site-verify. No-op unless configured."""
    if not settings.turnstile_secret:
        return True
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": settings.turnstile_secret, "response": token},
            )
            return bool(r.json().get("success"))
    except Exception:
        return False


class ScanRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    city_state: str = Field(..., min_length=2, max_length=120)
    cf_turnstile: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.mode}


@app.post("/api/scan", dependencies=[Depends(_require_key)])
async def scan(req: ScanRequest, request: Request):
    if not _limiter.allow(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and retry.")
    if settings.mode == "live":
        # Fail closed: live mode must have a Turnstile secret and a passing token.
        if not settings.turnstile_secret:
            raise HTTPException(
                status_code=503,
                detail="Turnstile not configured for live mode",
            )
        if not await _verify_turnstile(req.cf_turnstile or ""):
            raise HTTPException(status_code=403, detail="Turnstile verification failed.")
    # Demo mode stays open (no turnstile gate).
    scanner = ReconScanner(settings)
    return await scanner.scan_profile(req.name, req.city_state)
