# DGN-PICKS — session handoff

Updated: 2026-09-08 UTC — session paused for sleep.
Global project checklist and session handoff.

## Workflow and deployments

- Workflow: GitHub → Railway. The user does not require a separate local application environment.
- Frontend: https://dgnweb-production.up.railway.app/
- API: https://dgn-picks-production.up.railway.app
- GitHub: https://github.com/lkccomander/DGN-PICKS
- Branch: `main`, matching the local `origin/main` reference at `a94eeab`.
- Latest pushed commit: `a94eeab test: lock deterministic seed behavior`.
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

- [ ] Define admin/development boundary for write operations.
- [ ] CRUD for users, teams, players, games, markets, and selections.
- [ ] Append/read-only history operations for odds snapshots.
- [ ] Pick create/read/grade operations preserving taken price.
- [ ] CRUD/API contract tests and documentation.

## Current status

- API v1 routes and the initial dashboard are committed and pushed.
- PostgreSQL URL normalization and frontend CORS fixes were pushed; subsequent API checks succeeded.
- Last user-provided Railway results showed 4 games, 7 pending picks, 7 units risked, and zero profit. These are historical observations, not a fresh live check at handoff.
- `GET /api/v1/picks?user=gato` previously returned 500. Migration `0006_backfill_pick_timestamps` was pushed in `b882360` to repair missing timestamps.
- The frontend subsequently crashed on Decimal strings passed to `.toFixed()`. Commit `18b3eae` converts summary values to numbers. Its successful production rendering has not yet been independently verified.
- M1 is complete for the current workflow; local Docker-backed migration verification is deferred.
- M2 implementation is deployed; seed audit is complete, while migration verification and Railway smoke checks remain open.
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

1. Verify Alembic migrations and API v1/seed behavior through Railway.
2. Run desktop/mobile browser smoke checks against the deployed frontend.
3. Close M2 after those checks.
4. Start M3 CRUD: write boundary, domain CRUD, odds history, and pick grading.

## Known follow-up work

- Game responses currently expose team IDs, not team names; do not invent name mappings in CSS/UI work.
- Seed audit result: 13 Gato definitions, 7 stored picks, and 6 explicitly unresolved definitions. Do not invent missing opponents, dates, odds, team names, or the Malakai Toney side.
- No live odds provider is connected. Use deterministic fixtures until that milestone is explicitly taken on.

## Working tree at pause

- Application, API, tests, and status changes are committed through `a94eeab`.
- Existing untracked `DGN-PICKS.code-workspace` and `logs/` belong to the user; keep them out of release commits.
- `logs/railwaystatus.md` is an older dashboard report and is not proof of the latest deployment's state.

## Validation tooling

Windows Node.js is available at `C:\Program Files\nodejs`; frontend lint/build pass through PowerShell. Docker is not currently available inside this WSL distro, but that is not required for the current workflow. API tests pass with the project virtual environment; browser checks remain pending.
