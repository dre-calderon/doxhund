"""
Doxhund Recon Engine — Core Public Scanner (Fast & Ephemeral)
Scans target data broker search endpoints for public PII exposure.
Returns blurred preview metadata to power the Doxx Radar UI.
"""
import asyncio
import re
from typing import Dict, Any, List

def blur_text(text: str, visible_start: int = 2, visible_end: int = 2) -> str:
    """Masks sensitive PII string for secure client preview."""
    if not text or len(text) <= (visible_start + visible_end):
        return "***"
    return f"{text[:visible_start]}{'*' * (len(text) - visible_start - visible_end)}{text[-visible_end:]}"

def blur_phone(phone: str) -> str:
    """Masks phone number (702) 555-1234 -> (702) ***-**34"""
    clean = re.sub(r'\D', '', phone)
    if len(clean) == 10:
        return f"({clean[:3]}) ***-**{clean[-2:]}"
    return "***-***-****"

class ReconScanner:
    def __init__(self, proxy_url: str = None):
        self.proxy_url = proxy_url

    async def scan_profile(self, name: str, city_state: str) -> Dict[str, Any]:
        """
        Executes parallel reconnaissance across supported fast brokers.
        Returns aggregated match count and blurred exposure payload.
        """
        # Formatted query components
        parts = name.strip().split()
        first_name = parts[0] if parts else ""
        last_name = parts[-1] if len(parts) > 1 else ""

        # Placeholder demo response for initial pipeline wiring
        return {
            "query": {
                "name": name,
                "city_state": city_state
            },
            "total_records_found": 38,
            "status": "exposed",
            "brokers_detected": [
                {"name": "FastPeopleSearch", "matches": 1, "exposed": True},
                {"name": "TruePeopleSearch", "matches": 1, "exposed": True},
                {"name": "Radaris", "matches": 2, "exposed": True},
                {"name": "Spokeo", "matches": 1, "exposed": True},
                {"name": "Nuwber", "matches": 1, "exposed": True}
            ],
            "exposure_preview": {
                "addresses": [
                    {"address": blur_text(f"742 Evergreen Terrace, {city_state}"), "status": "EXPOSED"},
                    {"address": blur_text(f"1293 Maple Street, {city_state}"), "status": "EXPOSED"}
                ],
                "phones": [
                    {"phone": blur_phone("5555550142"), "type": "Wireless", "status": "EXPOSED"}
                ],
                "associates_count": 3
            }
        }

if __name__ == "__main__":
    scanner = ReconScanner()
    result = asyncio.run(scanner.scan_profile("Jane Doe", "Springfield, IL"))
    print("Doxhund Recon Scan Test Result:")
    import json
    print(json.dumps(result, indent=2))
