# M2 Domain and Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the deterministic DGN-PICKS domain, fixture provider, seed flow, and API v1 contract described in the approved M2 design.

**Architecture:** Keep the FastAPI backend as a modular monolith. SQLAlchemy models and domain services live under focused domain packages; provider adapters produce normalized DTOs; route modules expose Pydantic contracts under `/api/v1`. A transactional seed service persists stable fixture data and never mutates historical odds snapshots.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, pytest, httpx.

## Global Constraints

- Use a modular monolith; no microservices.
- Use deterministic local fixtures before any live odds provider.
- Normalize provider payloads at the provider boundary.
- Odds history is append-oriented; never overwrite historical snapshots.
- Every pick belongs to a user.
- Seed users are `gato`, `daran`, and `noch`; do not create `noche`.
- All 13 initial demo picks belong to `gato`.
- Preserve unresolved sports data; do not invent the Malakai Toney pick side, dates, opponents, or odds.
- Store timestamps in UTC and keep secrets out of source control.

---

### Task 1: SQLAlchemy base and domain models

**Files:**
- Create: `apps/api/src/dgn_picks_api/db/base.py`
- Create: `apps/api/src/dgn_picks_api/db/session.py`
- Create: `apps/api/src/dgn_picks_api/domains/users/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/teams/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/games/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/markets/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/odds/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/picks/models.py`
- Create: `apps/api/src/dgn_picks_api/domains/common/enums.py`
- Test: `apps/api/tests/test_models.py`

**Interfaces:**
- Produce `Base`, `engine`, `SessionLocal`, and typed model classes for User, Team, Player, Game, SportsbookSource, Market, Selection, OddsSnapshot, Pick, and PickLeg.
- Produce UTC-aware timestamp defaults and stable external-ID fields.
- Produce a uniqueness constraint for duplicate odds observations on `(selection_id, sportsbook_id, observed_at, source_event_id)`.

- [ ] Write model relationship and constraint tests for user-owned picks, stable external IDs, and duplicate snapshot prevention.
- [ ] Run the focused tests and confirm they fail before implementation.
- [ ] Implement typed SQLAlchemy models with enum-backed statuses and numeric odds fields.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Alembic migration and database wiring

**Files:**
- Modify: `apps/api/migrations/env.py`
- Modify: `apps/api/migrations/versions/0001_initial_schema.py`
- Modify: `apps/api/src/dgn_picks_api/db.py`
- Create: `apps/api/migrations/versions/0002_m2_domain_schema.py`
- Test: `apps/api/tests/test_migrations.py`

**Interfaces:**
- `migrations/env.py` imports `Base.metadata` as `target_metadata`.
- `SessionLocal` creates sessions from `DATABASE_URL`.
- Migration `0002_m2_domain_schema` upgrades and downgrades the full M2 domain schema.

- [ ] Add a migration test that checks upgrade creates all domain tables and downgrade removes the M2-only tables.
- [ ] Run the migration test against a local PostgreSQL service when available.
- [ ] Implement the Alembic metadata wiring and complete migration with indexes and foreign keys.
- [ ] Re-run migration tests and verify deterministic upgrade behavior.

### Task 3: Odds and pick calculation rules

**Files:**
- Create: `apps/api/src/dgn_picks_api/domains/odds/calculations.py`
- Create: `apps/api/src/dgn_picks_api/domains/odds/service.py`
- Create: `apps/api/src/dgn_picks_api/domains/picks/calculations.py`
- Test: `apps/api/tests/test_calculations.py`

**Interfaces:**
- `american_to_decimal(american_odds: int) -> Decimal`.
- `decimal_to_implied_probability(decimal_odds: Decimal) -> Decimal`.
- `profit_units(stake_units: Decimal, decimal_odds: Decimal | None, result: PickResult) -> Decimal | None`.
- `roi(total_profit_units: Decimal, total_units_risked: Decimal) -> Decimal | None`.

- [ ] Add tests for positive and negative American odds, implied probability, win/loss/push/void, missing odds, and zero risk.
- [ ] Implement Decimal-only calculations with no float conversion.
- [ ] Run the calculation suite and confirm all cases pass.

### Task 4: Provider contract and deterministic fixtures

**Files:**
- Create: `apps/api/src/dgn_picks_api/domains/providers/contracts.py`
- Create: `apps/api/src/dgn_picks_api/domains/providers/fixture.py`
- Create: `apps/api/src/dgn_picks_api/domains/providers/normalization.py`
- Create: `data/fixtures/ncaa_local.json`
- Test: `apps/api/tests/test_fixture_provider.py`

**Interfaces:**
- `FixtureProvider.list_games(date_range) -> list[NormalizedGame]`.
- `FixtureProvider.get_game(external_game_id) -> NormalizedGame`.
- `FixtureProvider.list_markets(external_game_id) -> list[NormalizedMarket]`.
- `FixtureProvider.list_props(external_game_id) -> list[NormalizedMarket]`.

- [ ] Test fixture coverage for four games, upcoming/final statuses, main markets, three prop categories, multiple snapshots, and settled QA outcomes.
- [ ] Implement JSON-backed deterministic fixture DTOs and provider methods.
- [ ] Add normalization validation that rejects missing required fields and unresolved pick sides.
- [ ] Run provider tests without network access.

### Task 5: Transactional idempotent seed service

**Files:**
- Create: `apps/api/src/dgn_picks_api/seed/data.py`
- Create: `apps/api/src/dgn_picks_api/seed/service.py`
- Create: `apps/api/src/dgn_picks_api/seed/report.py`
- Modify: `apps/api/src/dgn_picks_api/main.py`
- Test: `apps/api/tests/test_seed.py`

**Interfaces:**
- `seed_local_data(session: Session) -> SeedReport`.
- `SeedReport` exposes inserted/updated/duplicate/unresolved counts and unresolved definitions.

- [ ] Test first seed, repeated seed, exact user set, no `noche`, 13 Gato definitions, no Daran/Noch picks, and unresolved Malakai side.
- [ ] Implement transaction-scoped upserts by namespaced external IDs.
- [ ] Insert odds snapshots only when the deterministic duplicate key is absent.
- [ ] Keep unresolved input in the report and exclude it from playable pick creation.
- [ ] Run seed tests twice and compare persisted counts and reports.

### Task 6: API v1 routes and schemas

**Files:**
- Create: `apps/api/src/dgn_picks_api/api/v1/schemas.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/dependencies.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/users.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/games.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/markets.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/picks.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/analytics.py`
- Create: `apps/api/src/dgn_picks_api/api/v1/routes/dev.py`
- Modify: `apps/api/src/dgn_picks_api/main.py`
- Test: `apps/api/tests/test_api_v1.py`

**Interfaces:**
- Expose the approved `/api/v1` routes from the product spec.
- Use query filters `user`, `date`, and `conference`.
- Return HTTP 404 for unknown resources and HTTP 422 for invalid request bodies.
- `POST /api/v1/dev/seed` returns `SeedReport`.

- [ ] Write API tests for health, seed, user/game listing, market history, pick creation, taken-price preservation, filtering, and invalid references.
- [ ] Implement Pydantic request/response schemas and dependency-injected sessions.
- [ ] Implement route handlers as application-service calls, not inline SQL-heavy endpoints.
- [ ] Run API tests with a disposable database or transaction-isolated test session.

### Task 7: Developer commands, documentation, and validation

**Files:**
- Modify: `package.json`
- Modify: `README.md`
- Modify: `docs/exec-plans/active/2026-09-07-m2-domain-seed.md`
- Create: `scripts/seed_local.py`
- Move: `docs/exec-plans/active/2026-09-07-m2-domain-seed.md` to `docs/exec-plans/completed/2026-09-07-m2-domain-seed.md`

- [ ] Add `db:seed`, `test:api`, and migration commands with the correct Python module path.
- [ ] Document the fixture provider, seed report, unresolved pick behavior, and API v1 examples.
- [ ] Run Python compilation, pytest, Alembic upgrade/downgrade, Compose validation, and web lint/build where dependencies are available.
- [ ] Move the completed plan and commit the complete M2 milestone.

## Validation checklist

- [ ] `gato`, `daran`, and `noch` exist after seeding.
- [ ] `noche` does not exist.
- [ ] All 13 supplied definitions belong to `gato`.
- [ ] Malakai Toney side remains unresolved and unguessed.
- [ ] Odds snapshots remain immutable and duplicate-safe.
- [ ] Pick taken line and price remain unchanged after later snapshots.
- [ ] API v1 returns validated responses.
- [ ] Domain and API tests pass when dependencies are installed.

