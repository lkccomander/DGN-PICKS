# M3 catalog CRUD

## Purpose

Complete the M3 data-management API with catalog CRUD, append-only odds
history, and pick creation/grading.

## Scope / Non-scope

- In scope: team, player, game, market, and selection CRUD; append-only odds
  history; pick creation, retrieval, and grading; validation and safe deletion.
- Non-scope: production authentication and live odds-provider integration.

## Progress

- [x] Add catalog request schemas.
- [x] Add catalog routes and mount them under `/api/v1`.
- [x] Add contract tests; full runtime validation remains open.
- [x] Add append-only odds snapshot creation with duplicate protection.
- [x] Add pick detail and one-way grading with taken-price profit calculation.

## Validation

Run `./.venv/bin/pytest -q` from `apps/api` when the local SQLAlchemy import
hang is resolved.

## Decision Log

- Reuse the existing development write boundary from the Users CRUD slice.
- Prevent deletion of teams with players or games, and players referenced by
  markets or selections; deactivate instead.

## Outcomes & Retrospective

Catalog CRUD, odds history, and pick lifecycle are implemented without schema
changes. Full pytest execution remains blocked by the local SQLAlchemy import
hang.
