"""Per-broker recon scrapers (Playwright, lazy-imported).

Each scraper navigates a broker's public search UI headlessly and returns a
standardized, REDACTED result dict. Raw PII is blurred via ``engine.recon``
helpers before it leaves worker memory, so responses never contain plaintext.

Live mode requires:
  1. ``playwright install chromium``
  2. ``DOXHUND_PROXY_URL`` (rotating residential proxy) for Cloudflare-fronted brokers
  3. ``DOXHUND_CAPTCHA_API_KEY`` (CapSolver/2Captcha) for challenge pages

Without a proxy/captcha, Cloudflare-fronted brokers (FastPeopleSearch,
TruePeopleSearch, Spokeo) will return status ``"blocked"``. The selectors
below are best-effort and MUST be re-verified against each live site before
production use.
"""
from typing import Any, Callable, Dict

from engine.recon import blur_text


def _split_name(name: str) -> tuple:
    parts = name.strip().split()
    first = parts[0] if parts else ""
    middle = " ".join(parts[1:-1]) if len(parts) > 2 else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, middle, last


def _result(broker: str) -> Dict[str, Any]:
    return {
        "broker": broker,
        "status": "error",
        "matches": 0,
        "exposed": False,
        "addresses": [],
        "phones": [],
        "relatives_count": 0,
        "detail": "",
    }


def _blocked(title: str) -> bool:
    t = (title or "").lower()
    return any(
        k in t
        for k in (
            "just a moment",
            "attention required",
            "access denied",
            "challenge",
            "robot",
            "captcha",
            "verify",
        )
    )


async def _new_context(settings, playwright):
    # Use the installed Google Chrome via channel (no separate Chromium download).
    # In production (Docker) this should use Playwright's bundled Chromium instead.
    browser = await playwright.chromium.launch(headless=True, channel="chrome")
    kw: Dict[str, Any] = {
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1280, "height": 800},
    }
    if settings.proxy_url:
        from urllib.parse import urlparse

        p = urlparse(settings.proxy_url)
        proxy_cfg = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
        if p.username:
            proxy_cfg["username"] = p.username
            proxy_cfg["password"] = p.password or ""
        kw["proxy"] = proxy_cfg
    context = await browser.new_context(**kw)
    return browser, context


async def _apply_solution(browser, settings, url, solution):
    """Build a fresh context with solved cf_clearance cookies + UA, then navigate."""
    from urllib.parse import urlparse

    kw: Dict[str, Any] = {}
    if solution.get("user_agent"):
        kw["user_agent"] = solution["user_agent"]
    if settings.proxy_url:
        p = urlparse(settings.proxy_url)
        kw["proxy"] = {
            "server": f"{p.scheme}://{p.hostname}:{p.port}",
            "username": p.username,
            "password": p.password or "",
        }
    ctx = await browser.new_context(**kw)
    for c in solution.get("cookies", []):
        try:
            await ctx.add_cookies(
                [
                    {
                        "name": c.get("name"),
                        "value": c.get("value"),
                        "domain": c.get("domain"),
                        "path": c.get("path", "/"),
                        "secure": c.get("secure", False),
                        "httpOnly": c.get("httpOnly", False),
                        "sameSite": c.get("sameSite", "Lax"),
                    }
                ]
            )
        except Exception:
            pass
    page = await ctx.new_page()
    await page.goto(
        url, wait_until="domcontentloaded",
        timeout=settings.request_timeout_s * 1000,
    )
    return ctx, page


async def scan_fastpeoplesearch(name: str, city_state: str, settings) -> Dict[str, Any]:
    from playwright.async_api import async_playwright
    from engine import captcha

    res = _result("FastPeopleSearch")
    first, _m, last = _split_name(name)
    slug_name = f"{first}-{last}".lower().replace(" ", "-")
    slug_city = city_state.lower().replace(" ", "-").replace(",", "")
    url = f"https://www.fastpeoplesearch.com/name/{slug_name}_{slug_city}"
    try:
        async with async_playwright() as p:
            browser, ctx = await _new_context(settings, p)
            page = await ctx.new_page()
            await page.goto(
                url, wait_until="domcontentloaded",
                timeout=settings.request_timeout_s * 1000,
            )

            if _blocked(await page.title()):
                solution = await captcha.solve_cloudflare(settings, url, settings.proxy_url)
                if solution and solution.get("cookies"):
                    await ctx.close()
                    ctx, page = await _apply_solution(browser, settings, url, solution)

            if _blocked(await page.title()):
                res["status"] = "blocked"
                res["detail"] = "Cloudflare challenge (solver failed or datacenter IP flagged)."
                await browser.close()
                return res

            cards = await page.query_selector_all(
                ".people-list .card, .card, [class*='result']"
            )
            res["matches"] = len(cards)
            res["exposed"] = len(cards) > 0
            if not cards:
                res["status"] = "no_records"
                res["detail"] = "No result cards matched (selectors may need updating)."
            else:
                res["status"] = "ok"
                for card in cards[:3]:
                    for sel in (".address", "[itemprop='streetAddress']", ".street-address"):
                        el = await card.query_selector(sel)
                        if el:
                            raw = (await el.inner_text()).strip()
                            if raw:
                                res["addresses"].append(
                                    {"address": blur_text(raw), "status": "EXPOSED"}
                                )
                            break
            await browser.close()
    except Exception as e:
        res["status"] = "error"
        res["detail"] = f"{type(e).__name__}: {e}"
    return res


async def scan_nuwber(name: str, city_state: str, settings) -> Dict[str, Any]:
    from playwright.async_api import async_playwright

    res = _result("Nuwber")
    url = f"https://nuwber.com/search?name={name.replace(' ', '%20')}"
    try:
        async with async_playwright() as p:
            browser, ctx = await _new_context(settings, p)
            page = await ctx.new_page()
            await page.goto(
                url, wait_until="domcontentloaded",
                timeout=settings.request_timeout_s * 1000,
            )
            if _blocked(await page.title()):
                res["status"] = "blocked"
                res["detail"] = "Challenge / bot wall detected."
                await browser.close()
                return res
            cards = await page.query_selector_all(
                "[class*='person'], [class*='result'], .card"
            )
            res["matches"] = len(cards)
            res["exposed"] = len(cards) > 0
            res["status"] = "ok" if cards else "no_records"
            if not cards:
                res["detail"] = "No result cards matched (selectors may need updating)."
            await browser.close()
    except Exception as e:
        res["status"] = "error"
        res["detail"] = f"{type(e).__name__}: {e}"
    return res


SCRAPERS: Dict[str, Callable] = {
    "fastpeoplesearch": scan_fastpeoplesearch,
    "nuwber": scan_nuwber,
    # pending: truepeoplesearch, radaris, spokeo, clustrmaps
}


async def run(
    broker: Dict[str, Any], name: str, city_state: str, settings
) -> Dict[str, Any]:
    bid = broker.get("id") or "unknown"
    fn = SCRAPERS.get(bid)
    if fn is None:
        r = _result(str(broker.get("name") or bid))
        r["status"] = "pending"
        r["detail"] = "Scraper not yet implemented."
        return r
    return await fn(name, city_state, settings)
