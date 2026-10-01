# MVP validation — 2026-09-28

## Purpose
Complete the remaining isolated MVP acceptance checks and repair failures found by them.

## Scope / Non-scope
Cover clean dependency installation, CI, PostgreSQL migrations and deterministic seeds,
registration/login/account protection, owned pick management and stored prices,
desktop controls, responsive states, and release verification. Preserve unrelated
worktree changes. Pick-result research, production sports-data changes, virtual
tokens, live providers, and CLV are outside this milestone.

## Progress
- [x] Read the source documents and current handoff; user selected MVP validation.
- [x] Inspect remote CI: both synchronized runs fail at clean npm installation.
- [ ] Repair the lockfile and verify a fresh dependency installation.
- [ ] Verify migrations and seed repeatability on disposable PostgreSQL.
- [ ] Complete account, pick, responsive, and desktop browser acceptance.
- [ ] Run API, desktop, contract, lint, type, build, and CI checks.
- [ ] Reconcile milestone evidence, publish through GitHub and Railway, verify release.

## Implementation plan
1. Repair the incomplete web lockfile without changing requested dependency versions.
2. Run an isolated PostgreSQL/API/web/desktop stack with test credentials.
3. Add meaningful browser coverage for previously unverified supported journeys.
4. Fix reproduced failures, include acceptance in CI, and run required checks.
5. Record dated evidence, close satisfied plans, and publish the reviewed code.

## Validation
Fresh npm ci; full PostgreSQL migration cycle and repeated seed; API pytest;
desktop unit tests; generated-client drift; web lint/types/build; Playwright
desktop/mobile account, pick history, failure states, and desktop control flows;
remote GitHub workflow and deployed health/public behavior.

## Surprises & Discoveries
- WSL sandbox startup remains unavailable; commands require the escalation path.
- GitHub runs 36287249905 and 36286908705 failed before tests because package-lock.json
  lacks required transitive @emnapi dependencies.

## Decision Log
- Acceptance mutations use a disposable loopback test stack. Production Gato data
  and unresolved historical facts remain intact.

## Outcomes & Retrospective
In progress.
