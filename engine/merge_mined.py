#!/usr/bin/env python3
"""Merge the enriched mined brokers (catalog/_mined_enriched.json) into the
main catalog (catalog/brokers.json). Mined entries are marked tier='long_tail'
to distinguish them from the actionable IntelTechniques-sourced brokers.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "catalog" / "brokers.json"
MINED = REPO / "catalog" / "_mined_enriched.json"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main() -> None:
    cat = json.loads(OUT.read_text(encoding="utf-8"))
    mined = json.loads(MINED.read_text(encoding="utf-8"))

    existing = cat.get("brokers", [])
    seen_ids = {e["id"] for e in existing}
    seen_domains = {e.get("domain") for e in existing if e.get("domain")}

    added = 0
    for m in mined.get("brokers", []):
        name = m.get("name", "")
        domain = m.get("domain", "")
        s = slug(name)
        if not name:
            continue
        if s in seen_ids or (domain and domain in seen_domains):
            continue
        opt = m.get("opt_out_url") or ""
        existing.append({
            "id": s,
            "name": name,
            "domain": domain,
            "category": "people_search",
            "active": True,
            "recon_supported": False,
            "opt_out_url": opt,
            "website_url": f"https://{domain}" if domain else "",
            "request_method": "web_form" if opt else "unknown",
            "verification": "none",
            "captcha_required": False,
            "typical_sla_days": None,
            "contact": "",
            "source": m.get("source", "EasyOptOuts (mined) + enrichment"),
            "tier": "long_tail",
        })
        seen_ids.add(s)
        if domain:
            seen_domains.add(domain)
        added += 1

    cat["brokers"] = existing
    cat["version"] = "2.1.0"
    OUT.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"merged: added={added} total={len(existing)}")


if __name__ == "__main__":
    main()
