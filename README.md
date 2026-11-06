# Doxhund 🐾
> **The scent-hound that hunts down and deletes your public records.**

Doxhund is a lightweight, zero-knowledge automated privacy shield. It continuously monitors public data brokers, maps your exposed personal identifiable information (PII) on a visual "Doxx Radar", and automatically files CCPA/CPRA deletion requests across 75+ public people-search registries.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Privacy: Zero-Knowledge](https://img.shields.io/badge/Privacy-Zero--Knowledge%20AES--256-blue.svg)](#security--privacy-architecture)
[![Cloud: 100% Automated](https://img.shields.io/badge/Human--Free-100%25%20Code-green.svg)](#why-doxhund)

---

## Why Doxhund?
* **Zero Human Eyes:** Legacy services like DeleteMe employ overseas call center contractors to manually review your raw spreadsheets and legal documents. Doxhund runs on 100% automated code—zero humans ever see your data.
* **Client-Side Zero-Knowledge Encryption:** Your profile is encrypted with AES-256 inside your browser before it ever transmits to our servers. Central databases hold strictly ciphertext.
* **Continuous 30-Day Auto-Shield:** Data brokers re-ingest voter rolls and public deeds every few months. Doxhund re-scans every 30 days and auto-purges re-listed records.
* **Open Source Scrapers:** Our data broker catalogs and opt-out modules are open-source and publicly auditable.

---

## System Architecture

```
[CLIENT BROWSER: Next.js + Web Crypto API]
  ├── "Sniff Bar" Recon Search
  ├── Client-side AES-256 Key Derivation
  └── Real-time Doxx Radar Visualization
           │
           ▼ (Encrypted Payload over TLS)
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

---

## Directory Structure
* `catalog/`: Structured JSON definitions for data broker endpoints, request formats, and opt-out selectors.
* `engine/`: Python recon scrapers and headless Playwright execution modules.
* `web/`: Next.js frontend, Tailwind dark-mode UI, and Web Crypto vault.
* `workers/`: Cloudflare Email routing workers for automated confirmation-link clicking.

---

## License
MIT License. Free to inspect, verify, and run.
