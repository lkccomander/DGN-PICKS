# Checkpoint — audit remediation

> Historical checkpoint. The later [2026-09-26 publication checkpoint](2026-09-26-gato-publication.md) supersedes deployment status and validation counts below. API/web are now deployed and the strict legacy quarantine was applied; broader browser acceptance remains open.

Created 2026-09-24; resumed 2026-09-26. Implementation remains in progress.

## Scope and repository state

- [x] Audit recorded in [PROJECT-RECAP.md](../../PROJECT-RECAP.md), findings A1–A15.
- [x] User authorized implementation of the findings.
- [x] Local checkpoint preserves the remediation work in progress.
- [x] README, `.env.example`, product decisions, architecture notes, and recap were reconciled on 2026-09-26.
- [ ] Final acceptance and deployment are unfinished.
- Production has not been modified by this remediation. No push or deployment was performed.
- Preserve unrelated `.claude/skills/setup-matt-pocock-skills` deletions/symlink; excluded from the checkpoint commit.

## Phase 1 — API privacy and authorization

- [x] Public user projections omit email/country; private admin/account reads require bearer authentication.
- [x] User sessions bind to account ID, username, active state, and session version.
- [x] Disabling/reactivating accounts or changing passwords invalidates old sessions; deleted accounts fail authentication.
- [x] Operator sessions invalidate when configured credentials/role change.
- [x] Pick proxies require bearer sessions; ordinary users can manage only their own pending picks.
- [x] New predictions require open markets on scheduled/live games.
- [x] Repair direct-route tests and add HTTP regressions.

## Phase 2 — seed and analytics integrity

- [x] Preserve all 13 original Gato definitions as unresolved; stop inventing fixture-backed product picks.
- [x] Add migration `0009_audit_integrity` for session versions and recoverable pick archival.
- [x] Add `scripts/quarantine_legacy_seed.py`: dry-run default, explicit `--apply`, strict six-record legacy manifest, ambiguous records reported for review.
- [x] Exclude archived picks from regular reads, mutations, and analytics; preserve taken terms/history.
- [x] Add moneyline observations, third prop category, and separate QA settlement examples.
- [x] Separate pending exposure from settled ROI; show unavailable P/L and ROI as null.
- [ ] Production migration/quarantine have not been executed.

## Phase 3 — web, desktop, tooling

- [x] Account page reads real protected profile data; remove fabricated cash/verification claims.
- [x] Repair React hydration/lint issues and role-aware grading controls; restore team/conference filters.
- [x] Desktop enforces loopback Host, matching Origin, process CSRF token, JSON mutation payloads.
- [x] Update web and desktop private user reads and bearer proxies.
- [x] Upgrade Next.js to 16.3.6 and Playwright to 1.63.0; install reported zero vulnerabilities.
- [x] Regenerate OpenAPI and both TypeScript clients; add generator `--check`.
- [x] Add CI workflow with PostgreSQL, API/desktop checks, contract validation, build, audit and browser test.
- [x] Update stored-price browser test for authenticated isolated accounts and stable market selectors.
- [ ] Run the updated browser suite; CI workflow itself has not run remotely.

## Verified evidence at pause

- API suite: **84 passed**, before the final unused-variable/import cleanup in `seed/service.py`.
- Desktop suite: **18 passed**.
- Web lint: **0 errors, 0 warnings**; standalone TypeScript check passed.
- Next.js 16.3.6 production build passed.
- The last web checks preceded the final `/join` network-error handling and username-input changes; rerun them before release. The 2026-09-26 continuation updated documentation only and ran no tests.
- OpenAPI/client regeneration completed; run `--check` during final verification.
- All Alembic-generated upgrade SQL executed successfully on a disposable PostgreSQL 18 database; its head was `0009_audit_integrity`.
- This confirms SQL execution, not a completed online Alembic upgrade/downgrade cycle or verification of an existing production database.
- Temporary PostgreSQL server was stopped. The isolated SQLite API started for browser testing was also stopped at pause.
- No updated browser acceptance test completed during remediation; do not reuse the audit's older browser result as proof of these changes.

## Resume here — ordered checklist

1. [ ] Review the final `/join` edit; run current API/desktop, web lint/type/build, and generated-client checks before release.
2. [ ] Run Playwright against a disposable seeded API/database and built web server. Set `E2E_API_URL`, `E2E_WEB_URL`, `E2E_OPERATOR_USERNAME`, and `E2E_OPERATOR_PASSWORD` to isolated test values. The pick test rejects non-loopback origins.
3. [ ] On this Windows machine, use `E2E_BROWSER_CHANNEL=chromium`: full Chromium revision 1243 is installed, while matching headless-shell was absent. Set `E2E_DESKTOP_URL` to a temporary desktop Flask server to include its browser test.
4. [ ] Cover `/join, protected `/account`, invalid-session behavior, and desktop/mobile viewports; fix any failures.
5. [ ] Review CI end to end: API pytest clears operator auth environment for legacy development-key tests; PostgreSQL migration/seed and browser checks use isolated configured auth. Desktop browser coverage needs its server/environment added if desired in CI.
7. [x] Reconcile README, `.env.example`, product Decision Log, architecture notes, and PROJECT-RECAP. The original audit remains as a historical snapshot.
6. [ ] Update active plan with final evidence; move to completed only when local acceptance is finished.
7. [ ] Prepare deployment checklist: database backup, migration 0009, old-session re-login, quarantine dry run/review before explicit apply, auth/private-user smoke tests, browser checks. Deployment/data changes remain separate unfinished work.

## Environment notes

- WSL sandbox failed with a bubblewrap host mount alias; commands required the normal escalation path.
- API Python: `apps/api/.venv/bin/python`; desktop Python: `ext-tools/.venv/Scripts/python.exe`.
- Windows Node: `C:\Program Files\nodejs\node.exe`; run web commands with working directory `apps/web`.
- Docker Desktop daemon was unavailable. The migration test used an isolated native PostgreSQL 18 cluster on a temporary port.
- Capturing `pg_ctl start` output through Python pipes caused a timeout because the server inherited handles; use a server log and non-pipe output for a future disposable runner.
- An optional local API runner remains at `/tmp/dgn-remediation-api.py`; it creates a temporary SQLite database and synthetic test credentials. It is outside Git and may disappear. Prefer a repository test runner/CI for reproducibility.
- No live provider, token accounting, CLV, email verification, or password-reset delivery was added.
