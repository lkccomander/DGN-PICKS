# Pick management GUI

## Purpose

Complete the development-only pick-management slice required by the MVP: create, read, edit, grade, and delete tracked picks from the dashboard.

## Scope / Non-scope

Scope is the existing `gato` dashboard, FastAPI pick contract, and same-origin Next.js mutation proxy. Edits are limited to pending stake and notes; taken line/price, ownership, and market references remain immutable. Production authentication/admin roles and catalog management are out of scope.

## Progress

- [x] Add pending-pick update and delete domain operations with ownership checks.
- [x] Add development-only API routes and generated OpenAPI client updates.
- [x] Add dashboard edit, grade, and delete controls while keeping the write key server-side.
- [x] Add API contract tests for update/delete ownership and pending-only rules.
- [ ] Run browser E2E and desktop/mobile smoke checks when the local DB/write-key stack and working Node runtime are available.

## Implementation plan

1. Reuse the existing development write boundary and same-origin proxy.
2. Keep historical odds and taken-price fields append/immutable by design.
3. Refresh the read model after every successful mutation.

## Validation

Focused pick API tests pass (`11 passed`); Python compilation passes; OpenAPI client generation passes. Full API and frontend build checks remain to be run through the available project runtimes. Browser checks remain pending.

## Surprises & Discoveries

The dashboard already had create/read and only needed the missing update/delete/grade presentation. The WSL1 environment cannot start the Windows Node bridge, so frontend validation is environment-limited in this session.

## Decision Log

- 2026-09-12: Pending picks only may be edited or deleted. This avoids rewriting settled accounting and preserves the meaning of a recorded result.
- 2026-09-12: The browser calls same-origin Next routes; the API write key remains server-only.

## Outcomes & Retrospective

The dashboard now supports the complete development-only pick lifecycle for pending picks and grading, with explicit constraints around historical price preservation. Production admin/auth remains a separate milestone.
