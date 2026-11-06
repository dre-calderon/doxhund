#!/usr/bin/env python3
"""Parse IntelTechniques' Data Removal Workbook into catalog/brokers.json.

Reads a saved copy of inteltechniques.com/workbook.html, extracts each broker
block (Service / Website / Removal Link / Contact / Requirements), maps it to
the Doxhund catalog schema, merges with the existing curated entries, and
writes catalog/brokers.json.

Only factual fields (name, domain, opt-out URL, method, contact) are captured.
Michael Bazzell's prose "Notes" are intentionally NOT copied — link out to his
guide for that context.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SRC = os.getenv("DOXHUND_WORKBOOK_SRC", str(REPO / "catalog" / "workbook.md"))
OUT = REPO / "catalog" / "brokers.json"

SOURCE = "IntelTechniques Data Removal Guide (inteltechniques.com/workbook.html)"


def field(block: str, name: str) -> str:
    m = re.search(rf"^{re.escape(name)}:\s*(.+)$", block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def md_url(s: str) -> str:
    m = re.search(r"\((https?://[^)\s]+)\)", s)
    return m.group(1) if m else ""


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def derive_method(req: str) -> str:
    r = req.lower()
    if "fax" in r:
        return "fax"
    if "email submission" in r and "online" not in r:
        return "email"
    if "phone" in r and "online" not in r:
        return "phone"
    return "web_form"


def derive_verification(req: str) -> str:
    return "email_link" if "email verification" in req.lower() else "none"


def parse(text: str) -> list:
    blocks = re.split(r"\n(?=Service: )", text)
    entries = []
    for b in blocks:
        name = field(b, "Service")
        website = field(b, "Website")
        removal = field(b, "Removal Link")
        contact = field(b, "Contact")
        req = field(b, "Requirements")
        if not name or not website:
            continue
        website_url = md_url(website)
        removal_url = md_url(removal)
        if removal and removal.lower() in ("none", "embedded"):
            removal_url = ""
        domain = ""
        if website_url.startswith("http"):
            domain = urlparse(website_url).netloc.replace("www.", "")
        entries.append({
            "id": slug(name),
            "name": name,
            "domain": domain,
            "category": "people_search",
            "active": True,
            "recon_supported": False,
            "opt_out_url": removal_url,
            "website_url": website_url,
            "request_method": derive_method(req),
            "verification": derive_verification(req),
            "captcha_required": False,
            "typical_sla_days": None,
            "contact": contact,
            "source": SOURCE,
        })
    return entries


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC)
    text = src.read_text(encoding="utf-8")
    parsed = parse(text)

    existing = json.loads(OUT.read_text(encoding="utf-8"))
    cur = existing.get("brokers", [])

    seen_ids = {e.get("id") for e in cur}
    seen_domains = {e.get("domain") for e in cur if e.get("domain")}

    merged = list(cur)
    added = 0
    for p in parsed:
        if p["id"] in seen_ids or (p["domain"] and p["domain"] in seen_domains):
            continue
        merged.append(p)
        seen_ids.add(p["id"])
        if p["domain"]:
            seen_domains.add(p["domain"])
        added += 1

    result = {
        "version": "2.0.0",
        "name": "doxhund-broker-catalog",
        "description": (
            "Data broker opt-out endpoints, request methods, and selectors for "
            "Doxhund. Compiled from IntelTechniques' free Data Removal Guide "
            "and curated sources."
        ),
        "sources": [SOURCE],
        "brokers": merged,
    }

    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"parsed={len(parsed)} existing={len(cur)} added={added} total={len(merged)}")
    for e in merged[:4]:
        print("  -", e["name"], "|", e.get("opt_out_url") or "(no direct link)", "|", e["request_method"])
    print("  ...")


if __name__ == "__main__":
    main()
