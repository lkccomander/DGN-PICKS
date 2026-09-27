# AGENTS.md — DGN-PICKS

## Source of truth
Read before non-trivial changes:
1. `docs/product-specs/001-local-mvp.md`
2. `ARCHITECTURE.md`
3. `docs/design-docs/branding.md`
4. `PLANS.md`

## Rules
- Build milestone by milestone.
- Keep the repo runnable after each milestone.
- Use a modular monorepo; no microservices in MVP.
- Do not copy Pinnacle code, assets, text, trademarks, or exact layouts. Visual inspiration only.
- Brand name: `DGN-PICKS`.
- Brand stripe: blue, white, red, white, blue.
- Use deterministic local fixtures before any live odds provider.
- Normalize provider payloads at the provider boundary.
- Odds history is append-oriented; never overwrite historical snapshots.
- Every pick belongs to a user.
- Seed users: `gato`, `daran`, `noch`.
- All provided initial demo picks belong to `gato`.
- Store timestamps in UTC.
- Keep secrets out of source control.
- Add/update tests for domain-rule changes.
- Update Decision Log when architecture/product semantics change.

## Publication workflow
- User preference: always use GitHub for source/version history and direct Railway deployment for releases.
- Commit and push the reviewed changes to GitHub, then deploy the same committed application code directly to Railway and verify the deployed services.
- Record the source commit and Railway deployment IDs; a successful GitHub push alone does not verify deployment.
