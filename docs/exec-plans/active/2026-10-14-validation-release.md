# Validation and release — 2026-10-14

## Purpose
Repair clean-install CI, complete the remaining isolated account/pick/desktop
acceptance, reconcile current documentation, and publish the reviewed application
through GitHub and direct Railway deployment.

## Scope / Non-scope
Three parallel agents own dependency/CI repair, isolated acceptance, and
read-only release/documentation audit. The coordinator reviews integration and
owns commit, GitHub push, direct Railway deployment and final verification.
Preserve unrelated `.claude/skills` work. No production sports-data mutations or
invented prices/results. The user confirmed virtual credits without real money: remove monetary UI language,
retain request/ledger history, and keep pick units independent of credit accounting.

## Progress
- [x] Read product specification, architecture, branding and plans.
- [x] Verify initial GitHub CI failure and current production data/API contract.
- [x] Record current Railway deployments and implementation divergence.
- [x] Repair lockfile and verify clean dependency installation and checks.
- [x] Complete isolated account, owned-pick/stored-price and desktop acceptance.
- [x] Reconcile final local milestone evidence and open items.
- [ ] Commit reviewed changes and push to GitHub; verify remote CI.
- [ ] Deploy the same committed application directly to Railway.
- [ ] Record source SHA, service deployment IDs and public verification.

## Implementation plan
1. Repair the web lockfile and investigate generated-client drift without an
   unrequested dependency migration.
2. Exercise supported authenticated browser and desktop journeys against
   disposable local services; repair reproduced issues and add meaningful tests.
3. Update STATUS and source documents from dated evidence. Keep historical
   checkpoints historical and unresolved product/data decisions explicit.
4. Integrate agent changes, run necessary checks, review diff and preserve
   unrelated user work. Publish via GitHub, then Railway, and verify services.

## Validation
Final API suite: 115 passed. Desktop unit suite: 29 passed. Clean npm installation,
production audit (zero vulnerabilities), generated-client consistency, lint,
standalone TypeScript and the production build passed.
Disposable PostgreSQL 16 fresh upgrade/head, downgrade/base, and re-upgrade/head
all passed through revision `0014`; seed repeatability preserved 13 unresolved
definitions and produced no invented product picks. Ten built-app browser scenarios passed against isolated PostgreSQL: registration,
private account/login/logout/revocation at 1440px/390px, actual signed-session
expiry, loading/failure/retry/empty states at both sizes, NCAA fixtures/unresolved
definitions, owned pick edits/deletion and immutable taken price after movement,
web/desktop user CRUD, and credit request/desktop approval/one ledger entry/own
balance. Nine passed together; the multi-app credit case passed separately with
its 60-second timeout. CI will verify the complete suite together. Remote CI and
release verification remain pending.

Clean npm installation; API domain tests; desktop tests; generated-client check;
web lint/types/build; isolated browser acceptance; remote GitHub CI; Railway
service success and public health/web/API behavior. Record actual outcomes and
limits as agents complete their work; open checklist items are not acceptance.

## Surprises & Discoveries
- Built-app browser acceptance exposed an empty tracker hidden for new accounts,
  ambiguous route-announcer alert selectors, and a DELETE proxy building an
  invalid body for HTTP 204. Correct the UI/response and assert actual values,
  empty state, 204, record removal and mobile overflow.
- Security advisories required compatible Next/ESLint 16.3.8, sharp 0.35.5 and
  source-map-js 1.2.2 patches in addition to repairing missing lockfile entries.
- Initial CI run `38596352550` on `afd7219c25e18fd1992234fc8db5d56fc617a60a`
  failed at clean npm installation. Previous STATUS referenced September checks.
- Live API uses `/api/v1/analytics/summary`, not the stale specification's
  `/api/v1/analytics/picks-summary`; contract documentation corrected.
- Gato IDs 8–17 are now settled (4 wins, 6 losses), all without known odds.
  Profit/ROI remain null. The original 13 seed definitions still exist.
- Deposits and ledger are implemented and publicly exposed in OpenAPI, while
  accepted product semantics defer balances and prohibit monetary deposits.
- Railway's npm shim fails under WSL; invoking the installed Windows binary
  directly permits authenticated read-only inspection.

## Decision Log
- 2026-10-14: Restore NCAA fixtures to the board alongside recorded MLB schedules
  with an explicit league filter. The accidental MLB-only board hid the MVP data.
- 2026-10-14: Original seed definitions without authoritative event facts are
  pending/unresolved, never losses. Correct projection and UI without mutating
  the ten imported, settled picks or the historical database records.
- 2026-10-14: Use disposable local acceptance data; production grading remains
  unchanged. Missing odds remain null.
- 2026-10-14: User confirmed non-monetary virtual credits. Keep existing ledger/history
  and legacy identifiers; new accounts start at zero. Preserve the 1,000-credit
  monthly request cap, approval/rejection and auditable adjustments. No monetary
  methods, transfer/redemption or automatic pick settlement.

## Outcomes & Retrospective
In progress. Baseline production API deployment:
`577580c7-c231-49a3-ac78-ffdce6b05685`; web:
`7bacf90e-f97b-4dff-8e00-22afc4080bfe`, both SUCCESS and linked to source
`afd7219c25e18fd1992234fc8db5d56fc617a60a`. Final release evidence remains open.
