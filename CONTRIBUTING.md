# Contributing to Doxhund

Doxhund is a defensive privacy tool. Read `ONBOARDING.md` first — it defines
the vision, the trust story, and the build order.

## Ground rules

1. **Defensive only.** This is a self-lookup / self-removal tool. Do not add
   offensive OSINT, "look up anyone," or doxxing features — they would destroy
   the brand's trust. If a change could be used to investigate *other people*,
   it does not belong here.
2. **Surgical edits.** Make focused, verifiable changes. Don't rewrite files
   wholesale or reformat unrelated code.
3. **Verify before merging.** Run the tests and a smoke check; don't ship
   unverified work.

## How to contribute

1. **Fork** the repo (don't push directly to `main`).
2. Create a branch off `main`.
3. Make your changes and commit them.
4. Open a **pull request** against `howdy-beep/doxhund`.

A maintainer reviews and merges. Nothing deploys to production until it's
merged into `main`.

## Secrets

Never commit real credentials. Add new variables to `.env.example` (blank), not
to `.env`. `.env` is gitignored.
