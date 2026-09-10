# DGN-PICKS — session handoff

Updated: 2026-09-10 UTC — Railway deployment verified; final frontend/browser validation remains open.
Global project checklist and session handoff.

## Workflow and deployments

- Workflow: GitHub → Railway. The user does not require a separate local application environment.
- Frontend: https://dgnweb-production.up.railway.app/
- API: https://dgn-picks-production.up.railway.app
- GitHub: https://github.com/lkccomander/DGN-PICKS
- Branch: `main`; see `git log -1 --oneline` for the latest validation release.
- Do not equate a pushed commit with a verified Railway deployment.

## Global checklist

### M1 — Bootstrap foundation

- [x] Monorepo structure, developer commands, environment example, and ignore rules.
- [x] Next.js web shell with DGN-PICKS branding.
- [x] FastAPI app and `/api/health` endpoint.
- [x] PostgreSQL Compose service and Alembic foundation.
- [ ] Frontend lint and production build — pending Windows PowerShell validation.
- [x] API test suite: `39 passed`.
- [~] Docker Compose migration upgrade/downgrade verification — N/A for the current GitHub → Railway workflow; deferred unless a local DB environment is requested.

### M2 — Domain, deterministic seed, and API v1

- [x] SQLAlchemy domain models and migrations.
- [x] Decimal odds/profit/ROI calculations.
- [x] Deterministic fixture provider and normalization boundary.
- [x] Seed users: `gato`, `daran`, `noch`.
- [x] API v1 routes for users, games, markets/history, picks, analytics, and seed.
- [x] API test suite passing locally.
- [x] Audit 13 Gato definitions versus 6 stored picks; 7 definitions remain explicitly unmatched or unresolved.
- [x] Confirm unresolved Malakai Toney behavior without guessing.
- [x] Verify seed idempotency and ownership with an integration test.
- [ ] Verify migrations against PostgreSQL.
- [x] Verify API v1 and seed behavior on Railway.

### Dashboard frontend

- [x] Compact sportsbook-style layout and DGN brand stripe.
- [x] Search and result filters for picks.
- [x] Game status filters.
- [x] Decimal-shaped API value normalization.
- [x] Loading, error, and empty-state components.
- [ ] Desktop/mobile browser smoke checks.
- [x] Verify deployed frontend responds HTTP 200 and its bundle contains the market board/filter integration.

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
  movement trace. It also exposes date, team, conference, and status filters
  backed by the `/teams` and `/games` API responses, plus market-availability
  filtering for open, suspended, and closed markets.
- PostgreSQL URL normalization and frontend CORS fixes were pushed; subsequent API checks succeeded.
- Last user-provided Railway results showed 4 games, 7 pending picks, 7 units risked, and zero profit. These are historical observations, not a fresh live check at handoff.
- `GET /api/v1/picks?user=gato` previously returned 500. Migration `0006_backfill_pick_timestamps` was pushed in `b882360` to repair missing timestamps.
- The frontend subsequently crashed on Decimal strings passed to `.toFixed()`. Commit `18b3eae` converts summary values to numbers. Its successful production rendering has not yet been independently verified.
- M1 is complete for the current workflow; local Docker-backed migration verification is deferred.
- M2 implementation is deployed; seed audit is complete. The API suite passes locally (`56 passed`) and the migration chain generates valid offline SQL through `0006_backfill_pick_timestamps`.
- The compact dashboard is deployed; browser smoke checks remain open.
- Railway verification completed after the latest push: API health, teams, games,
  analytics, and frontend all returned HTTP 200; the API smoke check reported 8
  teams, 4 games, and 7 pending picks. The deployed JS bundle contains the
  market availability and movement UI.
- Added `scripts/smoke_api.py`, a dependency-free read-only check for health,
  teams, games, and analytics endpoints.
- The web app now uses `packages/api-client`, generated from the API OpenAPI
  document. It displays the six stored Gato picks alongside seven explicitly
  unmatched/unresolved seed definitions, so all 13 supplied definitions remain
  visible without guessed opponents, odds, or sides.
- A local-only Next proxy enables the create-pick UI only when explicit
  development variables are set; it keeps `DGN_API_WRITE_KEY` out of the
  browser bundle. Playwright covers the resulting taken-price lifecycle.
- `apps/api/requirements.txt` now matches the FastAPI upper bound in
  `pyproject.toml`; the full API suite passes with `58 passed`.

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

1. Run `npm run lint:web` and `npm run build:web` from Windows PowerShell.
2. Run `npm run test:e2e` against the documented local API/PostgreSQL stack.
3. Run desktop/mobile browser smoke checks against the deployed frontend.
4. Verify the Railway pre-deploy migration against PostgreSQL when database access is available.

## Known follow-up work

- Game responses currently expose team IDs, not team names; do not invent name mappings in CSS/UI work.
- Seed audit result: 13 Gato definitions, 6 stored picks, and 7 explicitly unmatched or unresolved definitions. Do not invent missing opponents, dates, odds, team names, or the Malakai Toney side.
- No live odds provider is connected. Use deterministic fixtures until that milestone is explicitly taken on.
- `apps/api/alembic.ini` has incomplete logging configuration for direct Alembic CLI use; `railway-alembic.ini` works for offline SQL generation.

## Working tree at pause

- Users CRUD is committed in `a4bc03c`, catalog CRUD in `c4a64cc`, odds/pick lifecycle in `ecd0190`, final dashboard/smoke integration in `8403b7e`, and Railway verification in `ebcd1bf`; `main` is synchronized with `origin/main`.
- Existing untracked `DGN-PICKS.code-workspace` and `logs/` belong to the user; keep them out of release commits.
- `logs/railwaystatus.md` is an older dashboard report and is not proof of the latest deployment's state.

## Validation tooling

Windows Node.js is available at `C:\Program Files\nodejs`, but the WSL1-to-Windows bridge does not return reliable npm exit codes. API pytest passes locally (`58 passed`); offline migration SQL and Railway HTTP/API smoke checks pass. Frontend lint/build, Playwright execution, Docker-backed migration verification, and browser viewport checks remain pending.
