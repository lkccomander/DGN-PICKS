> **Current update — 2026-09-26:** Remediation phases 1–3 and the Gato import are implemented in `32104bb` / `53c75c5`; API and web are deployed on Railway. See [STATUS.md](STATUS.md) and the [publication checkpoint](docs/checkpoints/2026-09-26-gato-publication.md). The original audit below remains historical.

## Current phase checklist

- [x] Phase 1: API privacy, revocable sessions, ownership, and eligibility fixes.
- [x] Phase 2: seed integrity, accurate analytics, and reversible quarantine; six synthetic production records archived.
- [x] Phase 3 implementation: web/account and desktop boundaries, dependencies, clients, and CI definition.
- [x] Current validation: 105 API tests, web lint/types/build, generated-client check, and PostgreSQL migration SQL through `0011`. Prior desktop suite: 18 passed.
- [x] Gato publication: ten owned picks imported; anonymous desktop/mobile browser acceptance passed against production.
- [x] Review all 13 original definitions and document missing event/date/side evidence.
- [ ] Grade the original definitions after those facts are supplied and official results are verified.
- [ ] Complete broader isolated authenticated/account/desktop browser acceptance and remediation closeout.
- [x] Synchronize GitHub through `cb58207` after the authentication update.
- [ ] Verify remote CI. Use GitHub source plus direct Railway deployment for releases, as required by the user.
- [ ] Future product work: virtual-token ledger, live-provider integration, and CLV.

# DGN-PICKS — Project audit, current state, and next steps

Audit date: **2026-09-24**
Source reviewed: **`main`, commit `01b3d7e`**, plus the current working tree.
Status: **Core MVP implementation exists; validation and account integration are unfinished.**

This checklist reconciles the code with the product specification, architecture,
branding, `PLANS.md`, `STATUS.md`, README, and active/completed execution plans.
Checked items mean the capability exists or the named check passed. Unchecked
items remain incomplete, failed, or unverified; they are not all missing code.

## 1. Current project state

- [x] Modular monorepo: Next.js/TypeScript web app, FastAPI/SQLAlchemy API,
  PostgreSQL migrations, and generated TypeScript API client.
- [x] NCAA game/market dashboard, game detail, props, snapshot history, movement
  visualization, pick tracking, and summary analytics are implemented.
- [x] Deterministic fixture provider and seed definitions are implemented.
- [x] Seed ownership is explicit: `gato`, `daran`, and `noch`; all 13 supplied
  pick definitions belong to Gato. The seed tests pass.
- [x] A fresh isolated seed produces six materialized picks and seven
  unmatched/unresolved definitions; Malakai Toney's side remains unresolved.
- [ ] Correct the six materialized Gato picks: they currently inherit QA fixture
  prices and matchups despite missing supplied odds/date/opponent metadata.
- [x] Public registration/login, signed sessions, catalog admin, and user-management
  screens exist. The account page is largely a static UI scaffold.
- [x] The desktop Ops Console includes Git/deployment tooling, graph viewing,
  user management, configuration, and local API lifecycle controls.
- [x] Railway API health and games endpoints respond HTTP 200; web `/`, `/join`,
  and `/admin` also respond HTTP 200 in this audit.
- [ ] Final MVP acceptance: API tests and frontend lint currently fail, the
  generated contract is stale, and important authenticated flows need repair.
- [ ] Virtual-token balances and ledger: planned, not implemented.
- [ ] Live odds provider and CLV: deferred future work.

## 2. Original milestone checklist

The product specification defines **M3 as the market board** and **M6 as
validation**. Later handoff documents reuse those labels for CRUD and auth.
The original numbering is retained here; added work is listed separately.

### M1 — Bootstrap: implemented; clean setup acceptance remains open

- [x] Repository structure, scripts, environment example, and ignore rules.
- [x] Next.js shell and DGN-PICKS branding assets.
- [x] FastAPI health endpoint, PostgreSQL Compose definition, Alembic foundation.
- [x] Current production web build and standalone TypeScript check pass.
- [ ] Repair the documented local migration command (`KeyError: 'formatters'`).
- [ ] Verify a clean dependency installation and migrations against disposable
  PostgreSQL, rather than relying only on an existing environment or offline SQL.

### M2 — Domain and seed: core implementation complete; integrity follow-up open

- [x] Users, teams, players, games, markets, selections, odds snapshots, and picks.
- [x] Decimal odds and settlement calculation functions.
- [x] Fixture provider and normalization boundary.
- [x] Seed definitions, repeatable seed behavior, user ownership, and unresolved
  Malakai handling have passing tests.
- [x] Migration chain reaches `0008_user_account_credentials` in offline
  PostgreSQL SQL generation using Railway's Alembic configuration.
- [ ] Reconcile the stale M2 active-plan checkboxes with the implementation.
- [ ] Close domain and authorization findings below before final acceptance.
- [ ] Complete fixture coverage: moneyline movement, a third prop category, and
  distinct settled QA win/loss/push examples are missing.

### M3 — Market board: implemented; full acceptance remains open

- [x] API-backed board, compact navigation, game status filtering, market display,
  and expandable game context.
- [x] Original dark DGN-PICKS design and blue → white → red → white → blue stripe.
- [ ] Check every promised date/conference/team/market-availability filter against
  actual behavior and update the acceptance checklist accordingly.
- [ ] Verify desktop/mobile layouts and loading, failure, and empty states in a
  real browser; HTTP 200 alone does not validate these states.

### M4 — Game detail and movement: implemented; browser acceptance open

- [x] Game detail, selections/props, historical observations, and movement UI.
- [x] Taken-price preservation is implemented independently of later snapshots.
- [ ] Complete the required browser journey: board → game → market → create pick
  → tracker → append a later snapshot → verify original taken values.

### M5 — Pick tracker: implemented; account integration and validation open

- [x] Pick creation, reading, pending stake/notes edits, pending deletion, and
  editor/admin grading operations.
- [x] API ownership checks and preservation of taken line/price.
- [x] Gato definition display and aggregate wins/losses/pushes/units/P&L/ROI UI.
- [ ] Align the web mutation proxy, API auth dependency, documentation, and E2E
  setup around one supported authentication flow.
- [ ] Repair the four failing pick tests and add HTTP-level coverage of the
  authenticated ownership boundary.
- [ ] Validate user-specific dashboard behavior and complete settlement/analytics
  acceptance, including incomplete-price data.

### M6 — Validation: not complete

- [x] Production build, TypeScript, desktop unit tests, and one mocked web CRUD
  browser test pass in this audit.
- [ ] API suite fully green.
- [ ] Frontend lint fully green.
- [ ] API schema and both generated clients synchronized.
- [ ] Dependency advisory findings addressed and rescanned.
- [ ] Fresh PostgreSQL bootstrap/upgrade and repeatable seed acceptance recorded.
- [ ] Full pick-price-preservation E2E and mobile/browser checks pass.
- [ ] Railway deployed commit, migration revision, auth configuration, and
  authenticated operations verified together.
- [ ] README, STATUS, product milestones, and execution plans synchronized.

## 3. Additional phases already implemented

### Catalog CRUD

- [x] Users, teams, players, games, markets, and selections API operations.
- [x] Append/read history routes and dependent-record deletion protections.
- [x] `/admin` catalog UI and server-side API proxy.
- [ ] Finish authenticated integration and error-path verification.

### Accounts and user administration

- [x] Credential migration, scrypt password hashes, registration/login endpoints,
  and user/admin/editor/viewer roles.
- [x] `/join`, `/account`, and the web Users tab.
- [x] Desktop user-management bridge and UI.
- [x] Mocked web Users create/search/edit/deactivate/delete/error flow passes.
- [ ] Production registration/login and authorized mutation smoke tests.
- [ ] Account privacy, lifecycle, and role behavior verified end to end.
- [ ] Close the active account-auth plan after its remaining criteria pass.

### Ops Console configuration

- [x] User-scoped Windows configuration persistence and secret redaction.
- [x] Connection check and controls for API processes started by the console.
- [x] User bridge/configuration unit tests: **14 passed**.
- [ ] Native desktop/browser and Windows lifecycle acceptance still needs an
  explicit verification record; mocked unit tests do not prove every OS behavior.

## 4. Confirmed audit findings

### A1 — High: dependency updates are required

- [ ] Address `npm audit --omit=dev` results: **five affected packages, one
  critical and four high**, including Next.js, Playwright-related packages,
  PostCSS, and sharp. `apps/web/package.json` pins Next.js to `16.1.6`.
- [ ] Upgrade deliberately, review the lockfile, rerun build/lint/browser tests,
  and rescan. The audit service offered Next.js `16.3.6` at audit time.

The maintainers identify critical issues affecting Windows-hosted servers and
AVIF image optimization, with fixes for these advisories in `16.3.3`.
Applicability depends on the hosting platform and enabled features; this audit
did not establish exploitability of the Railway deployment. Sources:
[Windows-hosted server advisory](https://github.com/vercel/next.js/security/advisories/GHSA-p293-qw3h-jr36),
[AVIF optimization advisory](https://github.com/vercel/next.js/security/advisories/GHSA-2xp9-vwfh-vxw4).

### A2 — High: public user endpoints expose account profile fields

- [ ] Separate public user-selector fields from private account/admin responses.
- [ ] Require appropriate authorization before returning email and country.

`apps/api/src/dgn_picks_api/api/v1/routes/users.py:15` and `:24` expose list/detail
routes without authentication; `api/v1/schemas.py:13` includes email and country
in their shared response model. An anonymous in-process request returned
**HTTP 200 with both synthetic profile fields**. No real account details were
collected for this reproduction.

### A3 — High: deactivation does not invalidate existing user access

- [ ] Bind user sessions to the persisted account ID and check current account
  activity at the authenticated boundary.
- [ ] Define/test password-change and account-deletion session invalidation too.

`api/v1/auth.py:37` issues eight-hour tokens; `current_identity` at line 46 checks
the signature/expiry but not the current database account. Pick creation checks
that the username exists without checking `active`. A user token issued before
deactivation still created a pick with **HTTP 201** in an isolated database.
Disabling an account therefore does not currently stop an existing session.

### A4 — High: product seed picks inherit invented fixture metadata

- [ ] Keep unknown product-seed odds/date/opponent metadata unresolved.
- [ ] Keep QA game/price examples distinct from the 13 supplied product picks.
- [ ] Plan a deliberate correction for already-materialized demo picks; preserve
  historical observations and do not silently rewrite taken values.

`apps/api/src/dgn_picks_api/seed/service.py:213` copies snapshot odds into Gato's
seed picks even though none of the 13 source definitions supplies odds. The
matching process also attaches product picks to synthetic fixture games;
fixture players are assigned to the game's home team at line 111. Fresh seeding
confirmed **all six stored Gato picks have fixture odds**. The product spec
explicitly forbids inventing those missing facts. Passing idempotency and
ownership tests do not cover this requirement.

### A5 — High: documented development pick flow no longer matches API auth

- [ ] Resolve the mismatch between
  `apps/api/src/dgn_picks_api/api/v1/dependencies.py:57`,
  `apps/web/src/app/api/development/picks/route.ts:45`,
  and `apps/web/e2e/dashboard.spec.ts:25`.

The web proxy/test still supports a development write key, but pick create,
update, and delete require a bearer session. An in-process HTTP reproduction
returned **503** with only development configuration and **401** with auth
configured but only the documented write key. This is a real integration gap,
separate from the direct-call unit-test failures.

### A6 — Medium: four API tests fail after the auth dependency change

- [ ] Update `apps/api/tests/test_picks_api.py:139` and the update/delete cases
  around lines 162–185 to provide an explicit identity or exercise dependency
  injection through an HTTP test client.

These tests call route functions directly and receive the default FastAPI
`Depends` object as the identity, producing `TypeError: 'Depends' object is not
subscriptable`. **67 tests pass; four fail.** This failure alone does not prove
that authenticated HTTP requests crash.

### A7 — Medium: checked-in API contract and clients are stale

- [ ] Regenerate `packages/api-client/openapi.json`,
  `packages/api-client/src/index.ts`, and
  `apps/web/src/lib/generated-api-client.ts` from the current FastAPI app.
- [ ] Add a check that regeneration leaves no diff.

A read-only comparison against `app.openapi()` and the generator found all
three artifacts out of sync. Missing changes include registration schemas/path,
user email/country/password fields, and the changed pick authorization headers.
The successful TypeScript build does not prove contract freshness.

### A8 — Medium: frontend lint fails

- [ ] Fix the reported React effect/state and Next internal-link errors in
  `apps/web/src/app/account/page.tsx`, `admin/page.tsx`, `join/page.tsx`, and the
  dashboard page; review hook-dependency warnings as part of the same pass.

The configured ESLint command exits nonzero. The production build and TypeScript
check pass independently, so they cannot be used as evidence that lint passed.

### A9 — Medium: local migration entrypoint is broken

- [ ] Add valid logging configuration or guard logging initialization in the
  local Alembic setup.
- [ ] Re-run both the documented command and an actual disposable PostgreSQL
  upgrade after the fix.

`apps/api/migrations/env.py:8` unconditionally loads logging configuration, but
`apps/api/alembic.ini` lacks the logging sections. The documented configuration
fails even with `upgrade head --sql`, before touching a database. The separate
`railway-alembic.ini` successfully generates SQL through revision `0008`.

### A10 — Medium: fixture acceptance is incomplete

- [ ] Add deterministic moneyline movement and at least a third prop category.
- [ ] Add separate QA settled win, loss, and push examples without assigning fake
  picks to Daran/Noch or confusing them with Gato's supplied picks.

`apps/api/src/dgn_picks_api/domains/providers/fixture.py:13` contains four games,
but only spread, total, passing-yards, and receiving-yards market types. There
are **two prop categories, no moneyline market, and no settled picks** after a
fresh seed. These are explicit section 10 fixture requirements still missing.

### A11 — Medium: account UI makes unsupported financial/verification claims

- [ ] Remove mock cash balances and unsupported verification claims.
- [ ] Remove out-of-scope deposit/withdrawal/payment/casino affordances.
- [ ] Populate supported account fields from authenticated account data; show
  paper-credit balances only after the ledger exists.
- [ ] Validate session state instead of treating token presence as proof of login.

`apps/web/src/app/account/page.tsx:21` hardcodes `USD 0.93`; line 25 says the user
is fully verified while profile fields are read-only placeholders and Save is
disabled. The dashboard header at `page.tsx:245` repeats the cash balance and
deposit controls. These are presentation claims, not implemented payments or
verification, and conflict with the paper-credit-only scope. The local-storage
UI gate is not evidence of an API authorization bypass.

### A12 — Medium: API accepts picks for closed markets and final games

- [ ] Define whether retrospective tracking is supported, and distinguish it
  explicitly from placing a new prediction.
- [ ] Enforce the chosen rule in `domains/picks/service.py:15` and cover it at
  the HTTP boundary; UI-only restrictions are insufficient.

The board only offers Track on open markets (`apps/web/src/app/page.tsx:323`),
but an authenticated API request for a closed market on a final game returned
**HTTP 201** in the isolated reproduction. The product docs do not fully specify
retrospective entry, so this needs a recorded policy decision, not an assumed
blanket ban on historical pick tracking.

### A13 — Medium: incomplete outcomes are represented as numeric ROI

- [ ] Define/report pending exposure separately from the denominator used for
  settled ROI, including unknown-price picks.
- [ ] Return an explicit unavailable value when the documented calculation
  prerequisites are absent; test all-pending and mixed incomplete datasets.

`apps/api/src/dgn_picks_api/api/v1/routes/analytics.py:17` adds every stake to
risked units and treats uncomputable profit as zero contribution. Two pending
picks returned **profit 0 and ROI 0**, although the product spec says not to
calculate profit/ROI for picks lacking required results/prices. Reconcile this
behavior with the intended reporting semantics before calling analytics accepted.

### A14 — Medium: desktop Git mutations lack a request-origin boundary

- [ ] Require a per-session request token and validate Origin/Host on privileged
  desktop routes; reject invalid/non-JSON mutation payloads.
- [ ] Apply the boundary consistently to Git, graph refresh, configuration, and
  local process controls, while retaining localhost binding.

`ext-tools/app.py:149` accepts a missing JSON payload, applies default commit and
branch values, and queues Git work. A Flask-client form POST with a foreign
Origin and no authentication returned **HTTP 200** and requested the worker.
The worker was mocked, so **no Git operation ran**. This confirms the missing
application-level check; a browser exploit was not tested and browser localhost
network protections may affect reachability.

### A15 — Medium: handoff documents are stale and inconsistent

- [ ] Replace historical test counts (59/62/65) and old deployment references
  with dated evidence; do not infer the deployed SHA from the local branch.
- [ ] Reconcile the original M1–M6 labels with the later CRUD/auth labels.
- [ ] Update the M2 plan's unchecked implemented tasks; keep genuinely unverified
  acceptance tasks open.
- [ ] Reconcile local-MVP/Compose requirements with the later GitHub → Railway
  workflow and record any accepted scope change in the Decision Log.
- [ ] Remove stale environment blockers only where a current check supersedes
  them; build and one browser test now run, but full E2E is still outstanding.

## 5. Validation evidence from this audit

| Check | Result | What it establishes |
| --- | --- | --- |
| API pytest | **67 passed, 4 failed** | Current suite is not green; failures are in direct pick-route calls. |
| TypeScript `tsc --noEmit --incremental false` | **Pass** | Web source type-checks. |
| Next production build | **Pass** | Current web source compiles and emits production routes. |
| Web ESLint | **Fail** | Existing lint errors remain. |
| Desktop `unittest test_users_api test_configuration -v` | **14 passed** | Mocked bridge/configuration behavior; existing Windows venv used. |
| Playwright Users test on temporary localhost web server | **1 passed, 1 skipped** | Web CRUD UI passes with intercepted API responses; desktop case skipped. |
| Playwright test discovery | **3 tests in 2 files** | One pick-history test plus web/desktop Users tests are configured. |
| Full pick-history browser E2E | **Not run** | Local seeded API/PostgreSQL stack and corrected auth flow still required. |
| Local Alembic offline upgrade | **Fail** | `KeyError: 'formatters'`. |
| Railway Alembic offline upgrade | **Pass** | SQL generation through `0008`; no live DB migration claimed. |
| Runtime OpenAPI/generated-client comparison | **Fail** | Schema and both client copies differ from generated output. |
| Isolated account/auth checks | **Findings confirmed** | Anonymous profile fields exposed; an inactive user's existing token still creates picks. |
| Isolated seed/domain checks | **Findings confirmed** | Six Gato picks inherit fixture odds; two prop categories/no moneyline/no settled QA; closed/final pick creation succeeds; all-pending ROI is numeric zero. |
| Desktop mutation-boundary check | **Finding confirmed** | Foreign-origin form request queues Git worker; worker mocked, no Git operation executed. |
| `npm audit --omit=dev` | **5 affected packages** | One critical/four high; feature-specific exposure needs assessment. |
| Railway HTTP availability | **Pass** | API health/games and web `/`, `/join`, `/admin` return 200. |
| Production authenticated writes / deployed SHA / DB revision | **Not verified** | Remain deployment acceptance tasks. |

Build tooling warned that a parent `C:\\Projects\\pnpm-lock.yaml` caused workspace
root inference outside this repository. Set an explicit Next workspace/tracing
root during tooling cleanup so builds do not depend on neighboring projects.

## 6. What is next — ordered execution checklist

### Phase A — Stabilize the existing implementation

- [ ] Create a focused execution plan for the audit fixes.
- [ ] Address dependency advisories, public profile exposure, session invalidation,
  and the desktop mutation boundary.
- [ ] Correct seed/QA separation and unsupported account-page claims.
- [ ] Align pick authentication across API, proxy, UI, tests, and documentation.
- [ ] Repair failing pick tests and frontend lint.
- [ ] Regenerate the API contract/client and add a drift check.
- [ ] Add CI gates for API tests, lint, types, client drift, build, and selected
  E2E tests; no tracked GitHub Actions workflow was found.
- [ ] Fix the local Alembic entrypoint and clean up environment/setup instructions.
- [ ] Resolve remaining domain-rule discrepancies with tests and explicit
  Decision Log entries where semantics change.

Exit criterion: current supported flows behave consistently; API tests, lint,
type-check, build, and contract checks pass.

### Phase B — Close MVP validation and active plans

- [ ] Bootstrap a disposable PostgreSQL database and apply the full migration chain.
- [ ] Seed twice and verify stable counts, exact seed-user names, Gato ownership,
  13 preserved definitions, and unresolved data handling.
- [ ] Verify no unknown product-seed odds/opponents/dates were inferred; complete
  moneyline/prop/settled-QA fixture requirements.
- [ ] Run the required pick-history E2E with working authentication.
- [ ] Add browser acceptance for registration/login, role/ownership restrictions,
  logout/expired sessions, and registered-user pick creation.
- [ ] Complete desktop and mobile visual/interaction checks.
- [ ] Verify desktop Users and configuration/lifecycle flows in the supported OS.
- [ ] Verify Railway's deployed SHA, migration head, auth configuration, and one
  authorized account/catalog/pick operation with controlled test data.
- [ ] Record evidence and close the compact-dashboard, pick-management, M2,
  and account-auth plans only after their remaining criteria pass.
- [ ] Synchronize `STATUS.md`, README, `PLANS.md`, and product progress.

Exit criterion: the original M6 acceptance checklist is complete and the handoff
identifies exactly which version was verified.

### Phase C — Proposed future scope: decide virtual-token rules first

- [ ] Define starting balance, grants, stake reservation/debit, insufficient
  balance behavior, pending stake edits/deletion, and win/loss/push/void settlement.
- [ ] Define correction/reversal behavior, rounding, concurrency, and idempotency.
- [ ] Record the agreed rules before adding an append-oriented token ledger.
- [ ] Implement models/migrations/services, account balance/history UI, and
  transaction/settlement tests.
- [ ] Keep tokens non-redeemable paper credits with no cash-out or monetary value.

The existing Decision Log records this product direction, but its accounting
rules and implementation scope remain unresolved. This audit proposes it as a
future planning candidate, not an authorized implementation milestone. Existing
account or balance-looking UI is not evidence of a ledger.

### Phase D — Deferred expansion

- [ ] Take on a live provider only as an explicit milestone, using the existing
  normalization boundary and preserving immutable snapshots.
- [ ] Define closing observations and CLV calculations before building CLV UI.
- [ ] Expand ingestion observability and operating documentation with that scope.
- [ ] Revisit password reset/email verification separately; the current spec
  explicitly excludes them from the account milestone.

## 7. Scope and limits

This was a repository-wide source/documentation audit with selected executable
checks, read-only deployment requests, and a dependency advisory scan. It did not
perform production mutations, inspect production secrets, prove a deployed
commit/database revision, execute full PostgreSQL acceptance, or validate every
browser viewport. Python dependency vulnerability scanning and a historical Git
secret scan were not performed. Findings above should not be read as a security
certification.

This task adds this recap only; the listed application fixes remain next steps.
Pre-existing `.claude/skills` working-tree changes belong to the user.

## 8. Source documents

- [Product specification and Decision Log](docs/product-specs/001-local-mvp.md)
- [Architecture](ARCHITECTURE.md)
- [Branding](docs/design-docs/branding.md)
- [Planning rules](PLANS.md)
- [Previous session handoff](STATUS.md)
- [README and setup guidance](README.md)
- [Active execution plans](docs/exec-plans/active/)
- [Completed execution plans](docs/exec-plans/completed/)
- [Ops Console documentation](ext-tools/README.md)
