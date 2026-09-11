# DGN-PICKS — session handoff

Updated: 2026-09-10 UTC — production deployment verified for API and web; browser E2E remains optional follow-up.
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
- [x] Frontend production build — verified with `npm run build` on Windows Node.js.
- [x] API test suite: `59 passed`.
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
- [x] Verify migrations against Railway PostgreSQL.
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

- `main` is deployed successfully at commit `dd55a7c` to both Railway services.
- API health is live at `/api/health`; production serves 13 Gato definitions,
  six materialized picks, and Malakai Toney as `unresolved` (without inventing
  an Over/Under side).
- The web build is self-contained under Railway's `/apps/web` root: its generated
  OpenAPI client is written into the app at generation time. The production
  dashboard responds HTTP 200.
- The API test suite passes locally (`59 passed`); the Next.js production build
  passes; the Alembic chain produces PostgreSQL SQL through revision
  `0007_remove_malakai_seed_pick`.
- M3 writes remain explicitly development-only and the live production API has
  no browser-exposed write secret.

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

1. Run `npm run test:e2e` against the documented local API/PostgreSQL stack when a local database and development write key are available.
2. Run desktop/mobile browser smoke checks against the deployed frontend.

## Known follow-up work

- Game responses currently expose team IDs, not team names; do not invent name mappings in CSS/UI work.
- Seed audit result: 13 Gato definitions, 6 stored picks, and 7 explicitly unmatched or unresolved definitions. Do not invent missing opponents, dates, odds, team names, or the Malakai Toney side.
- No live odds provider is connected. Use deterministic fixtures until that milestone is explicitly taken on.
- `apps/api/alembic.ini` has incomplete logging configuration for direct Alembic CLI use; `railway-alembic.ini` works for offline SQL generation.

## Working tree at pause

- Latest deployment fix is `dd55a7c`; `main` is synchronized with `origin/main`.
- Existing untracked `DGN-PICKS.code-workspace` and `logs/` belong to the user; keep them out of release commits.
- `logs/railwaystatus.md` is an older dashboard report and is not proof of the latest deployment's state.

## Validation tooling

Windows Node.js is available at `C:\Program Files\nodejs`. API pytest passes locally (`59 passed`); offline migration SQL, Railway migration, Railway HTTP/API smoke checks, and the Next.js production build pass. Playwright execution, Docker-backed migration verification, and browser viewport checks remain pending.
