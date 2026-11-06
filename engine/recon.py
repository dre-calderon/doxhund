"""Doxhund Recon Engine — orchestrates parallel broker recon.

Runs reconnaissance across supported data brokers and returns REDACTED preview
metadata (no plaintext PII ever leaves worker memory). In ``demo`` mode it
returns a clearly-labeled synthetic preview so the frontend/API can be wired
and tested without network, proxy, or captcha dependencies.
"""
import asyncio
import re
from typing import Any, Dict, List

from engine.config import Settings, load_brokers


def blur_text(text: str, visible_start: int = 2, visible_end: int = 2) -> str:
    """Masks sensitive PII string for secure client preview."""
    if not text or len(text) <= (visible_start + visible_end):
        return "***"
    return f"{text[:visible_start]}{'*' * (len(text) - visible_start - visible_end)}{text[-visible_end:]}"


def blur_phone(phone: str) -> str:
    """Masks phone number (555) 555-0142 -> (555) ***-**42"""
    clean = re.sub(r"\D", "", phone)
    if len(clean) == 10:
        return f"({clean[:3]}) ***-**{clean[-2:]}"
    return "***-***-****"


def _split_name(name: str) -> tuple:
    parts = name.strip().split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, last


def _demo_payload(name: str, city_state: str) -> Dict[str, Any]:
    """Synthetic, clearly-labeled preview for UI wiring and tests.

    Contains fictional data only — never real PII.
    """
    return {
        "query": {"name": name, "city_state": city_state},
        "total_records_found": 0,
        "status": "demo",
        "mode": "demo",
        "disclaimer": (
            "Demo preview: no brokers were queried. "
            "Set DOXHUND_MODE=live to run real recon."
        ),
        "brokers_detected": [],
        "exposure_preview": {
            "addresses": [
                {"address": blur_text(f"742 Evergreen Terrace, {city_state}"), "status": "SAMPLE"}
            ],
            "phones": [
                {"phone": blur_phone("5555550142"), "type": "Wireless", "status": "SAMPLE"}
            ],
            "associates_count": 0,
        },
    }


def _aggregate(name: str, city_state: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(r.get("matches", 0) for r in results)
    exposed = any(r.get("exposed") for r in results)
    addresses: List[Dict[str, Any]] = []
    phones: List[Dict[str, Any]] = []
    relatives = 0
    for r in results:
        addresses.extend(r.get("addresses", []))
        phones.extend(r.get("phones", []))
        relatives += r.get("relatives_count", 0)

    if exposed:
        status = "exposed"
    elif total == 0:
        status = "clean"
    else:
        status = "partial"

    return {
        "query": {"name": name, "city_state": city_state},
        "total_records_found": total,
        "status": status,
        "mode": "live",
        "disclaimer": None,
        "brokers_detected": [
            {
                "name": r.get("broker"),
                "matches": r.get("matches", 0),
                "exposed": r.get("exposed", False),
                "status": r.get("status"),
                "detail": r.get("detail"),
            }
            for r in results
        ],
        "exposure_preview": {
            "addresses": addresses[:6],
            "phones": phones[:4],
            "associates_count": relatives,
        },
    }


class ReconScanner:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def scan_profile(self, name: str, city_state: str) -> Dict[str, Any]:
        if self.settings.mode == "demo":
            return _demo_payload(name, city_state)

        from engine import scrapers

        brokers = [b for b in load_brokers() if b.get("recon_supported")]
        brokers = brokers[: self.settings.max_brokers_per_scan]

        results = await asyncio.gather(
            *(scrapers.run(b, name, city_state, self.settings) for b in brokers),
            return_exceptions=True,
        )

        cleaned: List[Dict[str, Any]] = []
        for b, r in zip(brokers, results):
            if isinstance(r, BaseException):
                cleaned.append(
                    {
                        "broker": b.get("name", b.get("id")),
                        "status": "error",
                        "matches": 0,
                        "exposed": False,
                        "detail": f"{type(r).__name__}: {r}",
                    }
                )
            else:
                cleaned.append(r)

        return _aggregate(name, city_state, cleaned)


if __name__ == "__main__":
    import json

    scanner = ReconScanner(Settings(mode="demo"))
    result = asyncio.run(scanner.scan_profile("Jane Doe", "Springfield, IL"))
    print("Doxhund Recon Scan Test Result:")
    print(json.dumps(result, indent=2))
