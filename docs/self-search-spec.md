# Doxhund — "Search Yourself" & Browse Spec (v1)

> Status: draft for review. No quiz, no accounts, no PII intake.

## 1. Principles (non-negotiable)

1. **Zero PII intake.** No quiz, no signup, no profile, no server-side storage of names/addresses/phones.
2. **Ephemeral input only.** A user may type a name + city in *their own browser*; JavaScript builds URLs and opens the broker's own page in a new tab. The value never touches our server.
3. **No accounts.** Progress (checkbox state) lives in `localStorage` on the device only. No sync, no database.
4. **Defensive-only.** Self-lookup / self-removal. Deep-links delegate search to the broker so we never collect or display a stranger's records on our side.

Any feature that transmits or stores PII on our side is rejected.

---

## 2. Two surfaces

### A. Browse (the master list)

The full 342-broker catalog, static and public, **sorted by leak severity**.

Each row:
- Broker name
- **"What it leaks" badge** (address · phone · relatives · employment · social)
- `[ Search ]` — deep-link to the broker's own search (see §3)
- `[ Remove ]` — one-click opt-out (form / mailto / fax, from `opt_out_url` + `request_method`)
- Method + typical SLA (from `verification` + `typical_sla_days`)

No input required. This is the zero-friction default.

### B. Search Yourself (Option A)

A single box: **name + city** (all client-side).

On submit, JavaScript:
1. Looks up brokers that have a `search_url_template`.
2. Fills the template with the name/city.
3. Opens up to N brokers in new tabs, alongside their `[ Remove ]` button.

Nothing is sent to our backend.

---

## 3. The honest gap (what "Search Yourself" can do today)

Only **6 of 342** brokers currently carry a `search_url_template`:

| Broker | Template |
|---|---|
| FastPeopleSearch | `/name/{name}_{city_state}` |
| TruePeopleSearch | `/results?name={name}&citystatezip={city_state}` |
| Radaris | `/p/{first_name}/{last_name}/` |
| Spokeo | `/{query}` |
| Nuwber | `/search?name={name}` |
| ClustrMaps | `/persons/{query}` |

The other 336 have no pre-fillable search URL. For those, "Search Yourself" can only:
- open the broker homepage, **or**
- open the opt-out page directly (147 have `opt_out_url`).

**Implication:** Option A is real today for ~6 brokers and degrades to "open homepage" for the rest. To make it feel good, we enrich `search_url_template` for the top 30–50 brokers by traffic/severity. That is the actual work item, not the UI.

---

## 4. Data model changes

1. **`leak_severity`** (new field on each broker) — one of `address` / `phone` / `relatives` / `employment` / `social` / `other`. Drives the Browse sort. Must be a manual pass (see §6); not derivable from the existing coarse `category` field (340/342 are just `people_search`).
2. **`search_url_template` enrichment** — add for top 30–50 brokers where a name-query URL exists.
3. Optional: `first_name` / `last_name` vs `query` vs `city_state` placeholder normalization so one fill function can serve all templates.

---

## 5. Build order

1. `leak_severity` manual pass on top ~50 brokers (the severity head of the list).
2. Browse view — static JS + catalog JSON, sorted by `leak_severity`, `[Search]` + `[Remove]` per row.
3. Search Yourself box — client-side template fill + tab-open, no backend.
4. Enrich `search_url_template` for top brokers (ongoing).

No backend, no proxy, no stealth for v1. Pure static on Cloudflare Pages.

---

## 6. Open decisions

1. **Severity taxonomy** — confirm the five buckets, or collapse to three (address / phone / everything-else)?
2. **How many tabs** does "Search Yourself" open at once (3 feels safe, 5 feels thorough)?
3. **Do the missing 26 OperationPrivacy brokers get merged** (8 confirmed net-new + Common page 2 + Job Sites) before or after this spec ships?
