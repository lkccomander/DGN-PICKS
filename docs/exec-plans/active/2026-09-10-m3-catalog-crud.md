# M3 catalog CRUD

## Purpose

Add development-only CRUD for teams, players, games, markets, and selections
as the catalog slice of M3 data management.

## Scope / Non-scope

- In scope: team, player, game, market, and selection list/detail/create/update/delete routes, request validation, foreign-key existence checks, and safe deletion conflicts.
- Non-scope: odds history, pick grading, and production authentication.

## Progress

- [x] Add catalog request schemas.
- [x] Add catalog routes and mount them under `/api/v1`.
- [x] Add contract tests; full runtime validation remains open.

## Validation

Run `./.venv/bin/pytest -q` from `apps/api` when the local SQLAlchemy import
hang is resolved.

## Decision Log

- Reuse the existing development write boundary from the Users CRUD slice.
- Prevent deletion of teams with players or games, and players referenced by
  markets or selections; deactivate instead.

## Outcomes & Retrospective

Catalog CRUD is implemented without schema changes. Full pytest execution remains blocked by the local SQLAlchemy import hang.
