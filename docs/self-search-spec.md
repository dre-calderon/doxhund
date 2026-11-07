# Doxhund — "Search Yourself" & Browse Spec (v1.1 — shipped)

> Status: shipped on `main`. No quiz, no accounts, no PII intake, no auto-tab fan-out. The guided `wizard.html` (built on this flow) is also shipped.

## 1. Principles (non-negotiable)

1. **Zero PII intake.** No quiz, no signup, no profile, no server-side storage of names/addresses/phones.
2. **Ephemeral input only.** A user may type a name + city in *their own browser*; JavaScript builds URLs. The value never touches our server.
3. **No accounts.** Progress (checkbox state) lives in `localStorage` on the device only. No sync, no database.
4. **Defensive-only.** Self-lookup / self-removal. Deep-links delegate search to the broker so we never collect or display a stranger's records on our side.
5. **No overwhelming fan-out.** "Search Yourself" renders a list the user clicks *one at a time* — it does not auto-open tabs.

Any feature that transmits or stores PII on our side is rejected.

---

## 2. Two surfaces

### A. Browse (`browse.html`) — shipped

The full 349-broker catalog (343 active), static and public, **sorted by `leak_severity`**.

Each row:
- Broker name + domain
- Method chip (web form / email / fax / manual)
- `[ Search ]` — deep-link to the broker's own search (or `website_url` fallback)
- `[ Remove ]` — one-click opt-out (`opt_out_url` + `request_method`); "no link" shown where missing
- `localStorage` checkbox progress + progress bar

No input required. This is the zero-friction default.

### B. Search Yourself (`index.html`) — shipped

A single box: **name + city** (all client-side).

On submit, JavaScript:
1. Looks up brokers that have a `search_url_template`.
2. Fills the template with the name/city.
3. Renders a clean list — "Here's where your name may appear" — with a
   **Search** link (opens that broker's own results in a new tab) and a
   **Remove** link per row. The user clicks one at a time.

Nothing is sent to our backend. No tabs auto-open.

---

## 3. The honest gap (what "Search Yourself" can do today)

**25 of 349** brokers currently carry a `search_url_template` (was 6). The
rest have no pre-fillable GET name-search URL — some require POST+CSRF
(InfoTracer), some redirect (MyLife → That'sThem), some are dead (PeekYou).

**Implication:** Search Yourself is real for 25 brokers today and grows only
as `search_url_template` is enriched. That enrichment is the main work item,
not the UI.

---

## 4. Data model

- **`leak_severity`** — `address` / `phone` / `relatives` / `employment` /
  `social`. Drives the Browse sort. Currently keyword-inferred via
  `scripts/classify_severity.py`; top-50 deserves a manual eyeball.
- **`search_url_template`** — pre-fillable name-search URL. Placeholders:
  `{name}`, `{first_name}`, `{last_name}`, `{city_state}`, `{query}`.

---

## 5. Build order (done + remaining)

- ✅ `leak_severity` added to all 349 brokers.
- ✅ Browse view — static JS + catalog JSON, sorted, `[Search]` + `[Remove]`.
- ✅ Search Yourself box — client-side template fill, list-only (no auto-open).
- 🔜 Enrich `search_url_template` for more brokers (batch 2+).
- 🔜 Mine the ~67 active brokers still missing an `opt_out_url`.

No backend, no proxy, no stealth for the shipped surface. Pure static on
Cloudflare Pages.

---

## 6. Remaining open items

1. **`leak_severity` manual eyeball** on top ~50 brokers (inference, not gospel).
2. **`opt_out_url` mining** — ~67 active brokers show "no link" in Browse.
3. **`search_url_template` batch 3** — next 10+ highest-traffic brokers.
4. **Curate `opt_out_email`** — a verified opt-out address per email-method
   broker (29 brokers), for the wizard's `mailto:` step.
