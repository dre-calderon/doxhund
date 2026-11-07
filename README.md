# Doxhund 🐾
> **The scent-hound that helps you find — and delete — your own public records.**

Doxhund is a free, open-source, manual-first privacy resource. It maps the
public data brokers that may hold your records, gives you one-click deep-links
to see what each site has on you, and hands you the removal link right next to
it. **Nothing you type ever leaves your browser. There are no accounts, no
signup, and no stored personal data.** Automation is a possible future paid
layer — never the gate.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Privacy: No PII Stored](https://img.shields.io/badge/Privacy-No%20PII%20Stored-blue.svg)](#principles)
[![Manual-first](https://img.shields.io/badge/Free-100%25%20Manual-green.svg)](#what-doxhund-is)

---

## What Doxhund is

Two surfaces, both free, both zero-storage:

1. **Search Yourself** (`index.html`) — type a name + city *in your own
   browser*. Doxhund fills each broker's search URL and shows you a clean
   list of "where your name may appear," each with a **Search** link (opens
   that site's own results in a new tab) and a **Remove** link. You click
   one at a time. Nothing is sent to us.
2. **Browse** (`browse.html`) — the full **342-broker** catalog, sorted by
   what actually leaks (home address → phone → relatives → employment →
   social). Check off what you've removed; progress is stored in your
   browser's `localStorage` only.

## Principles (non-negotiable)

- **No PII intake.** No quiz, no signup, no profile, no server-side storage
  of names/addresses/phones. Ephemeral input never leaves the browser.
- **Defensive only.** Self-lookup / self-removal. This is not an OSINT or
  "look up anyone" tool, and it never will be.
- **Manual-first.** Everything is free to do by hand. Automation (auto-scan +
  auto-remove) is an *optional* future paid layer.
- **Open source & auditable.** The broker catalog and logic are public.

## The catalog

`catalog/brokers.json` holds **342 brokers**. Key fields:

| Field | Meaning | Coverage |
|---|---|---|
| `leak_severity` | what the site exposes (address / phone / relatives / employment / social) | 342/342 |
| `search_url_template` | pre-fillable name-search URL (powers "Search Yourself") | 16 |
| `opt_out_url` | direct removal link | 147 |
| `request_method` | web_form / email / fax / unknown | 342/342 |

The `search_url_template` count is the main growth lever — every broker with
one shows up in the "Search Yourself" list automatically.

## Directory structure

- `index.html` — homepage + "Search Yourself" launcher (static, client-side).
- `browse.html` — the full broker directory, sorted by `leak_severity`.
- `guide.html`, `freeze.html`, `request.html`, `leak.html`, `archive.html` — free toolkit.
- `catalog/brokers.json` — the master broker registry.
- `scripts/classify_severity.py` — (re)assigns `leak_severity` by keyword inference.
- `engine/` — FastAPI recon API + Playwright scrapers (dormant; backend for
  the future paid automation layer, not required to use the site).
- `web/` — client-side AES-256 vault (dormant; a future paid-layer primitive).
- `docs/` — specs.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`ONBOARDING.md`](ONBOARDING.md).
The highest-value contribution right now is adding verified `search_url_template`
entries and filling in the ~195 missing `opt_out_url`s.

## License

MIT License. Free to inspect, verify, and run.
