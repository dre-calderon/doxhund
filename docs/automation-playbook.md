# Doxhund — Automation Playbook

> How to automate the opt-outs (and at least the scans) without breaking the
> zero-knowledge trust story. Written for the LLMs and contributors working on
> this repo. Read `ONBOARDING.md` first — this assumes the vision, the trust
> story, and the "three channels" framing.

## The two ladders — don't conflate them

Data-broker removal is really **two separate automation problems**:

1. **Scans (recon)** — "does broker X have a record on this person?" Auto-navigate
   the broker's people-search and return a *redacted* "record exists" preview.
   **Already scaffolded** in `engine/`.
2. **Removals (opt-out)** — "remove this person's record from broker X."
   Auto-submit the opt-out. **Not built yet** — but the catalog data is ready to
   drive it.

The manual-first site (`index.html`, `wizard.html`, `browse.html`) is the free
front door. The automated layer is the paid upsell. **Same catalog, same fields.**

## Scan automation (already scaffolded in `engine/`)

- `engine/api.py` — FastAPI `POST /api/scan` (+ `/health`), CORS, in-memory rate
  limiter, optional Turnstile gate.
- `engine/recon.py` — `ReconScanner` orchestrator + `blur_text()` (server-side
  PII redaction). Raw PII is blurred **before** it leaves worker memory.
- `engine/scrapers.py` — per-broker Playwright scrapers returning redacted dicts.
- `engine/captcha.py` — CapSolver client (`AntiCloudflareTask` → a `cf_clearance`
  cookie + matching user-agent).
- `engine/config.py` — env-driven settings (`DOXHUND_` prefix; secrets in `.env`).

To go live it needs: `playwright install chromium`, `DOXHUND_PROXY_URL` (rotating
residential), `DOXHUND_CAPTCHA_API_KEY`. Without proxy + captcha, Cloudflare-
fronted brokers return status `"blocked"` — honest, not broken.

**Redaction is the whole point.** Never return plaintext PII to the client.
Blur server-side (asterisks) so a "record exists" preview is emotionally
effective without ever transmitting the record. `filter: blur()` is NOT
redaction — the plaintext is still in the DOM.

## Removal automation — three channels, three difficulties

| Channel | What | Difficulty | Needs |
|---|---|---|---|
| **2. Email** | auto-send "remove me" to the broker's opt-out address | Easy — no stealth | `opt_out_email` + a mail sender |
| **3. Legal letters** | CCPA/DPO formal request via email | Easy — no stealth | `opt_out_email` + a letter template |
| **1. Forms** | browser-automation of the opt-out web form | **Hard** — Cloudflare + anti-detection | Playwright/Patchright + residential IPs + CapSolver |

Build order is deliberate: **channels 2+3 first** (they need zero anti-detection
and cover every broker with an `opt_out_email`), then channel 1 last. Do not sink
into the anti-detection arms race before the email + letter channels ship.

## The catalog drives everything

| Field | Powers |
|---|---|
| `search_url_template` | scan deep-links (auto-navigate to a name-search) |
| `opt_out_url` | form removal — channel 1 |
| `opt_out_email` | email removal — channels 2 + 3 |
| `request_method` | which channel applies |
| `recon_supported` | which brokers have a working scraper |
| `captcha_required` | which need a CAPTCHA solve |
| `leak_severity` / `leak_note` | prioritization (address-first) |

## Cheap, high-leverage automation wins (build these first)

1. **Pre-filled removal form URLs** — some brokers accept query params in their
   opt-out form (name/email pre-filled). Turn `opt_out_url` into a one-click
   submit deep-link where the broker supports it. Zero stealth, big UX win.
2. **Disposable email aliases** — brokers harvest the email you submit on an
   opt-out form and re-target it. Never expose a real user email; route through
   Cloudflare Email Routing and auto-click the confirmation link in a worker.
3. **Scheduled re-scan cron** — re-run the recon scanner every ~30 days to
   detect re-indexing. This is the ongoing value that justifies a subscription.
4. **mailto: batch composer** — the wizard already composes one draft at a time;
   a "compose all" that opens N drafts is a free, zero-intake improvement.

## Zero-knowledge guardrails (do NOT break these)

- **Client-side AES-256 vault** (`web/js/vault.js`, Web Crypto) — PII is
  encrypted in-browser before transmission; the server stores ciphertext only.
- **Just-in-time decryption** — the worker decrypts in RAM only long enough to
  fill a form, then clears it.
- **Disposable aliases** — the customer's real email is never exposed to brokers.
- **No human eyes, defensive-only** — self-removal only, never "look up anyone".
- **"No logs" is a lie** for a removal tool (recurring opt-outs require identity
  params). Say "zero-knowledge encrypted vault", never "no logs".

## Existing code map

- `engine/` — recon (scan) scaffolding: `api.py`, `recon.py`, `scrapers.py`,
  `captcha.py`, `config.py`.
- `web/js/vault.js` — client-side AES-256-GCM vault (future paid layer).
- `catalog/brokers.json` — the data that drives everything.
- **Nothing yet implements removal (channels 1–3) — that is the open work.**
