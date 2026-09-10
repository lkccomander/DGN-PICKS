# M3 catalog CRUD

## Purpose

Add development-only CRUD for teams and players as the first catalog slice of
M3 data management.

## Scope / Non-scope

- In scope: team and player list/detail/create/update/delete routes, request
  validation, foreign-key existence checks, and safe deletion conflicts.
- Non-scope: games, markets, selections, odds history, pick grading, and
  production authentication.

## Progress

- [x] Add team and player request schemas.
- [x] Add catalog routes and mount them under `/api/v1`.
- [x] Add contract tests; documentation and full runtime validation remain open.

## Validation

Run `./.venv/bin/pytest -q` from `apps/api` when the local SQLAlchemy import
hang is resolved.

## Decision Log

- Reuse the existing development write boundary from the Users CRUD slice.
- Prevent deletion of teams with players or games, and players referenced by
  markets or selections; deactivate instead.

## Outcomes & Retrospective

To be completed when this slice is finished.
