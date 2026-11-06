# Doxhund 🐾
> **The scent-hound that hunts down and deletes your public records.**

Doxhund is a lightweight, zero-knowledge automated privacy shield. It monitors public data brokers, maps your exposed personal identifiable information (PII) on a visual "Doxx Radar", and automatically files CCPA/CPRA deletion requests across 75+ public people-search registries.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Privacy: Zero-Knowledge](https://img.shields.io/badge/Privacy-Zero--Knowledge%20AES--256-blue.svg)](#security--privacy-architecture)
[![Cloud: 100% Automated](https://img.shields.io/badge/Human--Free-100%25%20Code-green.svg)](#why-doxhund)

---

## Why Doxhund?
* **Zero Human Eyes:** Legacy services like DeleteMe employ overseas call center contractors to manually review your raw spreadsheets and legal documents. Doxhund runs on 100% automated code, so zero humans ever see your data.
* **Client-Side Zero-Knowledge Encryption:** Your profile is encrypted with AES-256 inside your browser before it ever transmits to our servers. Central databases hold strictly ciphertext.
* **Continuous 30-Day Auto-Shield:** Data brokers re-ingest voter rolls and public deeds every few months. Doxhund re-scans every 30 days and auto-purges re-listed records.
* **Open Source Scrapers:** Our data broker catalogs and opt-out modules are open-source and publicly auditable.

---

## Status (Nov 2026)

- ✅ **Step 1 - Recon API:** `engine/api.py` exposes `POST /api/scan`, which queries public broker search endpoints and returns *redacted* record previews. Ships in `demo` mode out of the box (no network/proxy needed); `live` mode drives Playwright scrapers.
- ✅ **Step 2 - Client-side vault:** AES-256-GCM + PBKDF2 in `web/js/vault.js` (browser-side). Demo at `web/vault.html`. Passkey unlock planned as a later plug-in.
- 🔜 **Step 3 - Playwright opt-out workers** (pending).
- 🔜 **Step 4 - Cloudflare email routing** (pending).

## System Architecture

```
[CLIENT BROWSER: static HTML + Web Crypto API (vault in Step 2)]
  ├── "Sniff Bar" Recon Search
  ├── Client-side AES-256 Key Derivation
  └── Real-time Doxx Radar Visualization
           │
           ▼ (TLS)
[CLOUDFLARE EDGE & API GATEWAY]
  ├── Cloudflare Pages (Global Static Edge)
  └── Cloudflare Email Workers (Disposable Alias Link Handlers)
           │
           ▼ (Just-in-Time Decryption)
[HEADLESS AUTOMATION CLUSTER]
  ├── Python / Playwright Async Scrapers
  ├── Rotating Residential Proxies
  └── Autonomous Self-Healing Scraper Engine
```

## Directory Structure
* `index.html`: Single-page static frontend (deployed on Cloudflare Pages).
* `catalog/brokers.json`: Structured definitions for data broker endpoints, request formats, and opt-out selectors.
* `engine/`: Python FastAPI recon API, scrapers, and redaction helpers.
  * `engine/api.py` - FastAPI app (`/health`, `POST /api/scan`).
  * `engine/recon.py` - orchestrator + PII redaction.
  * `engine/scrapers.py` - per-broker Playwright scrapers (lazy-imported).
  * `engine/config.py` - env-driven settings.
* `web/`, `workers/`: planned (frontend refactor / Cloudflare Email routing).

## Getting Started (Recon API)

```bash
# 1. Create a venv and install deps (Python 3.11+)
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Run the API (demo mode by default - no network required)
uvicorn engine.api:app --host 0.0.0.0 --port 8000

# 3. Test it
curl -X POST http://127.0.0.1:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","city_state":"Springfield, IL"}'
```

Configuration lives in `.env` (see `.env.example`). Set `DOXHUND_MODE=live`,
a `DOXHUND_PROXY_URL`, and a `DOXHUND_CAPTCHA_API_KEY` (plus `playwright install
chromium`) to run real broker recon. Cloudflare-fronted brokers additionally
require a rotating residential proxy and a CAPTCHA solver.

## License
MIT License. Free to inspect, verify, and run.
