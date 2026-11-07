# Contributing to Doxhund

Doxhund is a defensive, manual-first privacy tool. Read `ONBOARDING.md`
first — it defines the vision, the trust story, and the build order.

## Ground rules

1. **Defensive only.** This is a self-lookup / self-removal tool. Do not add
   offensive OSINT, "look up anyone," or doxxing features — they would destroy
   the brand's trust. If a change could be used to investigate *other people*,
   it does not belong here.
2. **No PII intake.** Do not add quizzes, signup flows, profiles, or any
   server-side storage of names/addresses/phones. Ephemeral client-side input
   (a name typed in the browser to build a link) is the maximum allowed.
3. **Surgical edits.** Make focused, verifiable changes. Don't rewrite files
   wholesale or reformat unrelated code.
4. **Verify before merging.** Run the tests and a smoke check; don't ship
   unverified work. For catalog data, load-test URLs with a fictional name
   ("Jane Doe") and skip rather than guess.

## How to contribute

1. **Fork** the repo (don't push directly to `main`).
2. Create a branch off `main`.
3. Make your changes and commit them.
4. Open a **pull request** against `howdy-beep/doxhund`.

A maintainer reviews and merges. Nothing deploys to production until it's
merged into `main`.

## Catalog conventions (`catalog/brokers.json`)

- `search_url_template` uses exactly these placeholders: `{name}`,
  `{first_name}`, `{last_name}`, `{city_state}`, `{query}`.
- Never invent a `search_url_template` — visit the site, confirm the URL
  pattern loads real results for a fictional name, then add it. A 404
  template is worse than a missing one.
- `leak_severity` is one of: `address`, `phone`, `relatives`, `employment`,
  `social`. Re-run `scripts/classify_severity.py` after bulk edits to
  regenerate it.

## Secrets

Never commit real credentials. Add new variables to `.env.example` (blank), not
to `.env`. `.env` is gitignored.
