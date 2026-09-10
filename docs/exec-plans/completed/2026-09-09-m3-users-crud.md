# M3 users CRUD/API contract

## Purpose

Implement an isolated, migration-free CRUD slice for users and make the
development write boundary explicit.

## Scope / Non-scope

- In scope: user list/detail/create/update/delete, validation, ownership-safe deletion, and protected development seed writes.
- Non-scope: authentication, production admin roles, teams/games/markets CRUD, odds history writes, pick grading, frontend changes, and deleting users who own picks.

## Progress

- [x] Development-only write dependency using environment configuration.
- [x] User request schemas and CRUD routes.
- [x] Protected `/api/v1/dev/seed`.
- [x] Route/domain contract tests.
- [ ] Production admin/auth boundary (later M3 slice).

## API contract

- `GET /api/v1/users` and `GET /api/v1/users/{id}` are read-only.
- Mutations require `DGN_API_WRITE_MODE=development`, a non-empty `DGN_API_WRITE_KEY`, and matching `X-DGN-Write-Key`.
- Duplicate usernames return `409`; users with picks cannot be deleted and should be deactivated instead.

## Validation

- `git diff --check` passes.
- The project virtualenv is present, but pytest hangs during SQLAlchemy import before collection in this WSL session; no test result is claimed here.

## Decision Log

- Soft deactivation is the safe lifecycle operation once a user owns picks; hard deletion is limited to users with no picks.
- Until real authentication exists, development writes are disabled by default and require an environment-provided key.

## Outcomes & Retrospective

Users CRUD is implemented and isolated from migrations. Production admin/auth remains intentionally out of scope for this first M3 slice.
