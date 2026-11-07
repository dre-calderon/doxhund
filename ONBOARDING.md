# Doxhund — Orientation

## The one-line vision

**A one-stop shop for personal privacy — a free community resource where
everything can be done by hand, and you only pay if you want the bot to do
it for you.**

## The pitch

An open-source, zero-knowledge privacy engine that helps people find where
their personal data is publicly exposed and remove it. Free for everyone;
automation is the *optional* paid layer, never the gate.

## What "one-stop shop" means (the scope)

Data-broker removal is the core, but the product is broader — a hub for the
things a privacy-conscious person actually needs:

- **Data-broker opt-outs** (342 brokers, direct links)
- **Credit freeze + Do-Not-Call + breach check** (already in the free toolkit)
- **Pre-filled forms, one-click `mailto:` removals, copy-paste CCPA/CPRA letters**
- **Guides** (searchable removal checklist, `guide.html`)
- Later: email-breach lookup, car-privacy, and other self-lookup tools

## The business model (free-first, automation is the upsell)

| Tier | What you get | Cost |
|---|---|---|
| **Free (the whole point)** | Everything, done manually: direct links, pre-filled fields, letter templates, checklist | $0 |
| **Paid** | The bot does the repetitive parts (auto-scan + auto-remove + re-scan loop) | subscription |

Copy the **OperationPrivacy** model but do it *well*: zero friction for manual
opt-outs. Direct links, pre-filled fields, copy-paste letters — cut every step
that isn't strictly necessary.

## The core insight (this is the roadmap)

Data-broker removal is **three channels**, not one:

1. **Public opt-out FORMS** → browser automation (hard: Cloudflare / bot-walls)
2. **Templated removal EMAILS** → just auto-send "remove me" (no stealth needed)
3. **Legal-force CCPA/DPO LETTERS** → formal requests (no stealth needed)

The hard part (stealth + residential proxies) only matters for channel 1,
which is ~⅓ of removals. The other ⅔ (email + letters) is automatable TODAY.

**Build order:**
1. **Manual-first friction reduction** — direct links, pre-filled URLs,
   `mailto:` templates, copy-paste letter generator, a "enter your info once →
   get your click-by-click removal list" wizard. *(The real meat. $0, static,
   no backend.)*
2. **Email + legal-letter automation** — send templated removals. *(No
   Cloudflare wall to fight — highest-value automation, done first.)*
3. **Form automation** — the genuinely hard part. Deferred. When needed:
   Patchright + sticky residential IPs.

## The trust story (non-negotiable — do NOT break this)

- **Zero-knowledge:** PII encrypted client-side (AES-256), servers see
  ciphertext only.
- **No human eyes:** 100% automated. (DeleteMe uses call-center contractors;
  we don't.)
- **Open source & auditable.**
- **DEFENSIVE ONLY.** This is a self-lookup / self-removal tool. It is NOT an
  OSINT/doxxing toolkit. No "look up anyone" features. No backdoors. Shipping
  offensive tooling would kill the brand overnight.

## Current state (honest)

**DONE (on `main`):**
- Static frontend + free toolkit (`guide` / `freeze` / `request` / `leak` /
  `archive` + Do-Not-Call) — live on Cloudflare Pages.
- 342-broker catalog (`catalog/brokers.json`) with opt-out endpoints,
  `request_method`, `contact`, `verification`.
- AES-256-GCM vault (`web/js/vault.js`) + 5 passing Node tests.
- Recon API (`engine/api.py`) — demo/live modes, rate-limit, auth gate,
  Turnstile, server-side redaction.
- Security hardening pass (auth, IP trust, error scrubbing).

**NOT DONE / broken:**
- Scan button hardcodes `API_BASE = 'http://127.0.0.1:8000'`
  (`index.html:239`) — dead on the live site until the API is edge-hosted.
- Live recon is FLAKY (~⅓ dead rotating IPs + Cloudflare fingerprint-blocks
  headless Chrome).
- Only 2 scrapers implemented (`fastpeoplesearch`, `nuwber`) of 342.
- The friction-reduction wizard + email/letter automation is NOT built yet.
- No DB yet.

## Tech stack

- **Frontend / toolkit:** static HTML + JS on Cloudflare Pages (no build, $0).
- **Backend / scrapers:** Python FastAPI + Playwright (not on the Mac long-term;
  destined for a VPS).
- **Vault:** Web Crypto AES-GCM (client-side).
- **Secrets:** gitignored `.env` (see `.env.example`).

## Repo

- Remote: https://github.com/howdy-beep/doxhund
- Local: `/Users/abdul/hermes/apps/doxhund`

## Where to help first

Build the **manual friction-reduction wizard**: take `catalog/brokers.json`,
and produce — for each broker — a direct opt-out link, a pre-filled form URL
where the site supports it, a `mailto:` template, or a copy-paste CCPA letter,
sorted by "easiest first." Pure static JS + the existing JSON. No backend, no
proxy, no stealth. Then layer email/letter automation on top.
