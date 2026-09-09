# DGN-PICKS

NCAA College Football picks, lines, props, and line-movement tracker.

## Deployment

The active workflow is **GitHub → Railway**. Railway is the deployment environment; a local runtime is not required for normal project use.

| Service | Railway URL |
|---|---|
| Frontend | https://dgnweb-production.up.railway.app/ |
| API | https://dgn-picks-production.up.railway.app |

These URLs are deployment references. No live Railway verification is claimed here.

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
- **API v1:** route modules and schemas are mounted under `/api/v1`; automated API tests pass, while Railway smoke validation remains pending.
- **Frontend dashboard:** connected dashboard implementation is present; production smoke validation remains pending.
- **Live odds provider:** intentionally not connected. Deterministic local fixtures remain the source for MVP data.

## API v1 usage

Use the Railway API base URL:

```text
https://dgn-picks-production.up.railway.app/api/v1
```

Available route shapes:

- `GET /users?user=gato`
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

Push documentation and implementation changes to GitHub; Railway then deploys from the configured repository. This documentation does not claim that the Railway endpoints, migrations, or API v1 routes have been live-verified from the current environment.
