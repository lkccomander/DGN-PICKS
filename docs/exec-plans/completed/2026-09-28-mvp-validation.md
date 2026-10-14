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
- [x] Repair the lockfile and verify a fresh dependency installation.
- [x] Verify migrations and seed repeatability on disposable PostgreSQL.
- [x] Complete account, pick, responsive, and desktop browser acceptance.
- [x] Run API, desktop, contract, lint, type, build, and CI checks.
- [x] Reconcile milestone evidence, publish through GitHub and Railway, verify release.

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
Completed by the October 14 closeout below.

## Verified closeout — 2026-10-14

Closed by the [MVP validation/release checkpoint](../../checkpoints/2026-10-14-mvp-validation-release.md).
Final application source `47a127af0220b98253a676f72829f082ae49692f`: green GitHub CI,
116 API tests, 29 desktop tests, 10 isolated browser scenarios, clean install,
contract/lint/types/build/audit and PostgreSQL migration/seed checks. API/web were
deployed directly to Railway and verified; public desktop/mobile acceptance passed.
Native Windows pywebview graphics and original-card research are separate limits,
not claims of this acceptance. Earlier validation notes above are historical.
