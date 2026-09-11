# DGN-PICKS

NCAA College Football picks, lines, props, and line-movement tracker.

## Deployment

The active workflow is **GitHub → Railway**. Railway is the deployment environment; a local runtime is not required for normal project use.

| Service | Railway URL |
|---|---|
| Frontend | https://dgnweb-production.up.railway.app/ |
| API | https://dgn-picks-production.up.railway.app |

Verified on 2026-09-10: both services deployed successfully from `main`; the API
healthcheck and dashboard returned HTTP 200.

## Baseline stack
- Next.js + TypeScript
- FastAPI + Python
- PostgreSQL
- SQLAlchemy + Alembic
- pytest
- Playwright
- deterministic fixture/seed data

## Codex reading order
1. `AGENTS.md`
2. `docs/product-specs/001-local-mvp.md`
3. `ARCHITECTURE.md`
4. `PLANS.md`
5. `docs/design-docs/branding.md`

## Current milestone status

- **M1 foundation:** complete — web shell, FastAPI health endpoint, PostgreSQL migration foundation, developer commands, and deterministic fixture direction. API tests pass; Docker-backed migration verification still requires Docker Desktop WSL integration.
- **M2 domain/seed:** implementation is present — domain models, migrations, calculations, fixture provider, seed definitions/service, and seed report. Seed coverage audit remains active.
- **API v1:** route modules and schemas are mounted under `/api/v1`; 59 API tests and Railway smoke/migration validation pass.
- **Frontend dashboard:** connected dashboard implementation is deployed; its production build and HTTP smoke check pass.
- **Live odds provider:** intentionally not connected. Deterministic local fixtures remain the source for MVP data.

## API v1 usage

Use the Railway API base URL:

```text
https://dgn-picks-production.up.railway.app/api/v1
```

Available route shapes:

- `GET /users?user=gato`
- `GET /users/{id}`
- `POST /users` (development write boundary)
- `PATCH /users/{id}` (development write boundary)
- `DELETE /users/{id}` (development write boundary; users with picks cannot be deleted)
- `GET /teams?conference=SEC&active=true`
- `POST /teams`, `PATCH /teams/{id}`, `DELETE /teams/{id}` (development write boundary)
- `GET /players?team_id={id}&active=true`
- `POST /players`, `PATCH /players/{id}`, `DELETE /players/{id}` (development write boundary)
- `POST /games`, `PATCH /games/{id}`, `DELETE /games/{id}` (development write boundary)
- `GET /markets?game_id={id}`
- `POST /markets`, `PATCH /markets/{id}`, `DELETE /markets/{id}` (development write boundary)
- `GET /markets/{id}/history`
- `POST /markets/{id}/history` (development write boundary; append-only)
- `POST /markets/{id}/selections` (development write boundary)
- `GET /selections/{id}`
- `PATCH /selections/{id}`, `DELETE /selections/{id}` (development write boundary)
- `GET /picks/{id}`
- `PATCH /picks/{id}/grade` (development write boundary)
- `GET /games?date=YYYY-MM-DD&conference=SEC`
- `GET /games/{game_id}`
- `GET /games/{game_id}/markets`
- `GET /markets/{market_id}/history`
- `GET /picks?user=gato&date=YYYY-MM-DD`
- `POST /picks`
- `GET /analytics/summary`
- `POST /dev/seed`

The development seed endpoint is idempotent and reports unresolved input. The Malakai Toney 72.5 receiving-yards definition remains unresolved because its Over/Under side was not supplied; it must not be guessed.

## Validation and handoff

Push documentation and implementation changes to GitHub; Railway then deploys from the configured repository. Consult `STATUS.md` for the latest verification evidence and optional browser/E2E follow-up.

For a read-only deployed API smoke check, run `python scripts/smoke_api.py` or provide another origin with `python scripts/smoke_api.py --base-url https://example.invalid`.

## Local E2E validation

The Playwright test uses a local development API and Next server. It never
sends the API write key to the browser: Next's local-only proxy keeps that key
server-side. With PostgreSQL migrated and the API seeded, set the local values
from `.env.example`, start the API and web server, then run:

```powershell
$env:E2E_API_URL = "http://127.0.0.1:8000"
$env:E2E_WEB_URL = "http://127.0.0.1:3000"
$env:DGN_API_WRITE_KEY = "replace-with-a-local-secret"
npm --prefix apps/web exec playwright install chromium
npm run test:e2e
```

The test selects a game, opens its detail, tracks an open selection, appends a
later odds snapshot through the local development boundary, and verifies the
pick still displays its stored taken line and price.
