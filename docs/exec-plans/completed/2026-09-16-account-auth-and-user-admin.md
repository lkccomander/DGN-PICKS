# Account authentication and user administration

## Purpose

Complete the production account lifecycle and expose user CRUD in the authenticated admin dashboard.

## Scope / Non-scope

- In scope: persisted user email/profile credentials, password hashing, public registration, user login sessions, authenticated user pick ownership, admin user CRUD, database migration, tests, and the web join/admin flows.
- Non-scope: email verification, password reset email delivery, social login, multi-tenant organizations, real-money payments, and public user deletion.

## Progress

- [x] Add credential fields and migration.
- [x] Add registration/login and authenticated user identity.
- [x] Enforce user ownership for pick mutations.
- [x] Add admin Users tab and connect Join form.
- [x] Validate API, web build, and deployment configuration.

## Implementation plan

1. Keep HTTP routes thin; put password hashing and account authentication in focused user/auth helpers.
2. Preserve the configured operator login and admin/editor catalog boundary.
3. Add a `user` session role for account holders; only admin/editor may mutate catalog and user records.
4. Allow account holders to create and manage only their own pending picks.
5. Keep seeded users compatible with nullable credentials until they register credentials through an admin-supported path.

## Validation

- API tests for registration, duplicate usernames/emails, login, invalid credentials, role boundaries, and user CRUD.
- API tests for user-owned pick mutation boundaries.
- Web production build.
- Migration SQL / PostgreSQL validation where available.

## Surprises & Discoveries

- The existing Join screen only performs client-side validation.
- The existing User model has no email or password fields; configured admin credentials are global API credentials, not user accounts.

## Decision Log

- Use Python's standard-library `scrypt` password hashing to avoid adding a native dependency.
- Store only password hashes; never return credential fields in API responses.
- Keep public registration separate from protected admin user CRUD.

## Outcomes & Retrospective

Implementation is complete. Python syntax validation and the Windows Node production build pass. Full pytest execution remains blocked in the current WSL environment because pytest/FastAPI are not installed there; deployment and live migration verification remain the release follow-up.

## Verified closeout — 2026-10-14

Closed by the [MVP validation/release checkpoint](../../checkpoints/2026-10-14-mvp-validation-release.md).
Final application source `47a127af0220b98253a676f72829f082ae49692f`: green GitHub CI,
116 API tests, 29 desktop tests, 10 isolated browser scenarios, clean install,
contract/lint/types/build/audit and PostgreSQL migration/seed checks. API/web were
deployed directly to Railway and verified; public desktop/mobile acceptance passed.
Native Windows pywebview graphics and original-card research are separate limits,
not claims of this acceptance. Earlier validation notes above are historical.
