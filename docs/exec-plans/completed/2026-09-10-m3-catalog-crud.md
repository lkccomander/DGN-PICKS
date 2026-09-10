# M3 data-management API

## Purpose

Complete the M3 data-management API with catalog CRUD, append-only odds
history, and pick creation/grading.

## Scope / Non-scope

- In scope: team, player, game, market, and selection CRUD; append-only odds
  history; pick creation, retrieval, and grading; validation and safe deletion.
- Non-scope: production authentication and live odds-provider integration.

## Progress

- [x] Catalog request schemas and routes mounted under `/api/v1`.
- [x] Foreign-key validation and dependent-record deletion protection.
- [x] Append-only odds snapshot creation with duplicate protection.
- [x] Pick detail and one-way grading with taken-price profit calculation.
- [x] Contract tests and API documentation.

## Validation

- Python compilation passes for all touched modules and tests.
- `git diff --check` passes.
- Full pytest execution remains blocked by the local SQLAlchemy import hang
  before collection in this WSL session.

## Decision Log

- Reuse the development write boundary from the Users CRUD slice.
- Historical odds observations are never updated or overwritten.
- Grading is one-way from pending; the stored taken line and price are used for
  profit calculations.

## Outcomes & Retrospective

M3 data-management API is complete without schema changes. Remaining MVP work
is environment/deployment validation and browser smoke testing.
