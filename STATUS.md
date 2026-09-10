# DGN-PICKS — session handoff

Updated: 2026-09-10 UTC — API suite green; final frontend/deployment validation open.
Global project checklist and session handoff.

## Workflow and deployments

- Workflow: GitHub → Railway. The user does not require a separate local application environment.
- Frontend: https://dgnweb-production.up.railway.app/
- API: https://dgn-picks-production.up.railway.app
- GitHub: https://github.com/lkccomander/DGN-PICKS
- Branch: `main`; local commit `6431dd2` contains the completed market-movement dashboard and is one commit ahead of `origin/main`.
- Latest pushed commit: `3a1e15a docs: close M3 data management plan`.
- Do not equate a pushed commit with a verified Railway deployment.

## Global checklist

### M1 — Bootstrap foundation

- [x] Monorepo structure, developer commands, environment example, and ignore rules.
- [x] Next.js web shell with DGN-PICKS branding.
- [x] FastAPI app and `/api/health` endpoint.
- [x] PostgreSQL Compose service and Alembic foundation.
- [x] Frontend lint and production build.
- [x] API test suite: `39 passed`.
- [~] Docker Compose migration upgrade/downgrade verification — N/A for the current GitHub → Railway workflow; deferred unless a local DB environment is requested.

### M2 — Domain, deterministic seed, and API v1

- [x] SQLAlchemy domain models and migrations.
- [x] Decimal odds/profit/ROI calculations.
- [x] Deterministic fixture provider and normalization boundary.
- [x] Seed users: `gato`, `daran`, `noch`.
- [x] API v1 routes for users, games, markets/history, picks, analytics, and seed.
- [x] API test suite passing locally.
- [x] Audit 13 Gato definitions versus 7 currently stored picks; 6 definitions remain explicitly unresolved.
- [x] Confirm unresolved Malakai Toney behavior without guessing.
- [x] Verify seed idempotency and ownership with an integration test.
- [ ] Verify migrations against PostgreSQL.
- [ ] Verify API v1 and seed behavior on Railway.

### Dashboard frontend

- [x] Compact sportsbook-style layout and DGN brand stripe.
- [x] Search and result filters for picks.
- [x] Game status filters.
- [x] Decimal-shaped API value normalization.
- [x] Loading, error, and empty-state components.
- [ ] Desktop/mobile browser smoke checks.
- [ ] Verify deployed frontend against the live API.

### M3 — CRUD and data management

- [x] Define development-only write boundary for initial write operations.
- [x] User CRUD/API contract slice with ownership-safe deletion.
- [x] CRUD for teams, players, games, markets, and selections.
- [x] Append/read-only history operations for odds snapshots.
- [x] Pick create/read/grade operations preserving taken price.
- [x] CRUD/API contract tests and documentation.

## Current status

- API v1 routes and the initial dashboard are committed and pushed; the Users CRUD extension is committed locally in `a4bc03c`.
- M3 user CRUD slice is implemented: read detail,
  create, update, and delete routes; writes require `DGN_API_WRITE_MODE=development`,
  `DGN_API_WRITE_KEY`, and `X-DGN-Write-Key`; users with picks cannot be deleted.
- M3 catalog CRUD is implemented and committed in `c4a64cc`: Teams, Players, Games, Markets, and
  Selections routes are mounted under `/api/v1`, use the development write
  boundary, validate references, and block deletion when dependent records exist.
- M3 odds and pick lifecycle API is implemented and committed in `ecd0190`: odds snapshots append
  through `/markets/{id}/history` with duplicate protection; pick creation is
  write-protected; pending picks can be retrieved and graded once through
  `/picks/{id}/grade` while preserving the taken line and price.
- The dashboard now fetches all game markets and persisted histories concurrently,
  and renders market selections with opening/current values and a compact line
  movement trace.
- PostgreSQL URL normalization and frontend CORS fixes were pushed; subsequent API checks succeeded.
- Last user-provided Railway results showed 4 games, 7 pending picks, 7 units risked, and zero profit. These are historical observations, not a fresh live check at handoff.
- `GET /api/v1/picks?user=gato` previously returned 500. Migration `0006_backfill_pick_timestamps` was pushed in `b882360` to repair missing timestamps.
- The frontend subsequently crashed on Decimal strings passed to `.toFixed()`. Commit `18b3eae` converts summary values to numbers. Its successful production rendering has not yet been independently verified.
- M1 is complete for the current workflow; local Docker-backed migration verification is deferred.
- M2 implementation is deployed; seed audit is complete. The API suite passes locally (`56 passed`) and the migration chain generates valid offline SQL through `0006_backfill_pick_timestamps`; live PostgreSQL/Railway verification remains open.
- The compact dashboard is deployed; browser smoke checks remain open.

## Active task: compact sportsbook-style frontend

User reference: https://www.pinnacle.com/en/football/ncaa/matchups/#all

Use original DGN-PICKS CSS inspired by a compact sportsbook board. Preserve navy/blue/red branding and the blue → white → red → white → blue stripe. Do not copy Pinnacle code, assets, text, trademarks, or its exact layout.

Execution plan: [Compact dashboard](docs/exec-plans/active/2026-09-08-compact-dashboard.md).

Completed:

- Read the product spec, architecture, branding, plan rules, and React best-practices skill.
- Inspected the current frontend and opened the reference URL; the text browser exposed only its JavaScript shell.
- Created and maintained the active execution plans.
- Compact section navigation, aligned pick columns, searchable picks, result filters, and game-status filters.
- Cancellable concurrent dashboard refreshes.
- Numeric normalization for summary and pick Decimal-shaped API values.
- Aggregate summary labeled as `All users`.

## Next steps

1. Verify Alembic migrations and API v1/seed behavior through Railway when DNS/credentials are available.
2. Run desktop/mobile browser smoke checks against the deployed frontend.
3. Push the dashboard integration, then complete deployment and browser smoke validation.

## Known follow-up work

- Game responses currently expose team IDs, not team names; do not invent name mappings in CSS/UI work.
- Seed audit result: 13 Gato definitions, 7 stored picks, and 6 explicitly unresolved definitions. Do not invent missing opponents, dates, odds, team names, or the Malakai Toney side.
- No live odds provider is connected. Use deterministic fixtures until that milestone is explicitly taken on.
- `apps/api/alembic.ini` has incomplete logging configuration for direct Alembic CLI use; `railway-alembic.ini` works for offline SQL generation.

## Working tree at pause

- Users CRUD is committed in `a4bc03c`, catalog CRUD in `c4a64cc`, odds/pick lifecycle in `ecd0190`, and market-movement dashboard integration in `6431dd2`; only `6431dd2` remains to be pushed.
- Existing untracked `DGN-PICKS.code-workspace` and `logs/` belong to the user; keep them out of release commits.
- `logs/railwaystatus.md` is an older dashboard report and is not proof of the latest deployment's state.

## Validation tooling

Windows Node.js is available at `C:\Program Files\nodejs`, but the WSL1-to-Windows bridge currently fails before npm starts. API pytest passes locally (`56 passed`); Docker-backed migrations, frontend lint/build, browser checks, and Railway smoke checks remain pending.
