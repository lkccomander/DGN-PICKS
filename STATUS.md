# DGN-PICKS — session handoff

Updated: 2026-10-14 (America/Guatemala). **Production is available; the remaining
MVP acceptance and CI/release work is in progress.** Current work is tracked in
[validation and release](docs/exec-plans/active/2026-10-14-validation-release.md).
September publication evidence remains in the
[Gato checkpoint](docs/checkpoints/2026-09-26-gato-publication.md).

## Verified baseline

- GitHub `main` source: `afd7219c25e18fd1992234fc8db5d56fc617a60a`.
- [CI run 38596352550](https://github.com/lkccomander/DGN-PICKS/actions/runs/38596352550)
  failed during `npm ci`; clean-install repair and a green replacement run remain
  required. September test/build claims are historical, not current release proof.
- Public API `/api/health` returns `{"status":"ok","service":"dgn-picks-api"}`.
- Public `/api/v1/picks?user=gato` contains ten active picks, IDs 8–17.
  `/api/v1/analytics/summary?user=gato` reports **4 wins, 6 losses, zero pending**,
  10 unpriced settled picks, and null profit/ROI. Missing odds remain unknown.
- `/api/v1/seed/pick-definitions?user=gato` preserves all 13 original definitions.
  Missing original event facts and Malakai Toney's side remain separate from the
  settled September 26 card; do not match them to QA fixtures.
- Railway baseline source is `afd7219c25e18fd1992234fc8db5d56fc617a60a`.
  API deployment `577580c7-c231-49a3-ac78-ffdce6b05685` and web deployment
  `7bacf90e-f97b-4dff-8e00-22afc4080bfe` are SUCCESS. PostgreSQL is SUCCESS.
  This is existing production evidence, not proof of the upcoming release.

## Implemented scope and current validation

Market board, persisted odds history, tracker, user ownership, account privacy,
revocable sessions and Ops Console features are implemented. CFBD and MLB schedule
adapters exist; NFL ingestion is pending. No live odds provider or CLV is verified.

The user confirmed **virtual credits without real money** on October 14. New
accounts start at zero; approved requests and auditable manual adjustments append
to the existing ledger. The 1,000-credit monthly request cap uses UTC months.
Historical entries and legacy identifiers are retained. Picks remain in units,
independently of credits. USD, payment methods and fictional account verification
were removed. Credits cannot be purchased, transferred, withdrawn or redeemed.

Validation recorded this session:
- API: 115 tests passed, including virtual credits and unresolved-definition regressions.
- Desktop: 29 tests passed.
- PostgreSQL 16: fresh upgrade through `0014`, full downgrade to base and re-upgrade
  passed on a disposable loopback database; repeated seed preserved 13 unresolved
  definitions without invented product picks.
- Clean web installation passed (354 packages). Production dependency audit: zero
  vulnerabilities. Next/ESLint 16.3.8, sharp 0.35.5 and source-map-js 1.2.2 are locked.
- Generated-client consistency, web lint, standalone TypeScript and production
  build passed. Built-app browser acceptance passed all ten scenarios. GitHub CI and release
  verification are in progress. Browser checks use the built Next app against isolated PostgreSQL.
- Fixed the MLB-only board, unresolved definitions falsely labelled losses, hidden
  empty trackers, mobile account overflow, and the pick DELETE proxy's invalid
  HTTP 204 body. Historical production pick records were not changed.

## Next steps

- [x] Repair the lockfile and run clean installation, contract/lint/type/build checks.
- [x] Complete isolated registration, protected account, owned pick creation/editing,
  stored-price history, desktop-console and virtual-credit acceptance (10 scenarios).
- [x] Reconcile USD/deposit semantics as user-authorized non-monetary credits.
- [ ] Obtain original-card date/jornada or opponents and Malakai Toney's side before
  grading those 13 historical definitions. Keep unknown taken odds null.
- [ ] Verify final local checks and green GitHub CI for the reviewed source commit.
- [ ] Deploy that commit directly to Railway and record new deployment IDs and
  verification. Close only milestones supported by evidence.

## Deployment context

Frontend: https://dgnweb-production.up.railway.app/
API: https://dgn-picks-production.up.railway.app

Release workflow: commit and push reviewed changes to GitHub, deploy the same
committed application code directly to Railway, then verify the services and
record the commit/deployment IDs. Railway inspection works by invoking the
installed `@railway/cli/bin/railway.exe` directly in this WSL environment.
Preserve unrelated `.claude/skills` worktree changes.
