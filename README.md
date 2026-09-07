# DGN-PICKS

Local-first NCAA College Football picks, lines, props, and line-movement tracker.

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

## First task
Bootstrap Milestone 1 only. Do not connect a real odds provider yet.
## Local development

Milestone 1 provides a Next.js web shell, a FastAPI health endpoint, and a PostgreSQL-backed migration foundation. It intentionally does not connect to a live odds provider.

1. Install web dependencies with `npm install --prefix apps/web`.
2. Start PostgreSQL with `npm run db:up`.
3. Run migrations with `npm run db:migrate`.
4. Start the API with `npm run api` or the web app with `npm run dev:web`.
5. Run checks with `npm run lint:web` and `npm run test:api`.

The API health check is available at `http://localhost:8000/api/health`.
