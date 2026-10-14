# DGN-PICKS — session handoff

Updated: 2026-10-14 (America/Guatemala). **MVP validation is complete; the reviewed
application is published and verified on Railway.** See the
[release checkpoint](docs/checkpoints/2026-10-14-mvp-validation-release.md).

## Verified release

Application source: `47a127af0220b98253a676f72829f082ae49692f`.
[GitHub CI](https://github.com/lkccomander/DGN-PICKS/actions/runs/38605399888): SUCCESS.
Direct Railway uploads from a clean archive of that commit:

- API: `e9da9532-a4a6-4bd0-af58-4b96e74212ee` — SUCCESS.
- Web: `d5de63fc-67a4-4f9c-80b6-f76c50cbd115` — SUCCESS.
- Public web and API health: HTTP 200; protected account/credit/admin reads: HTTP 401 anonymously.

Validation: **116 API tests, 29 desktop tests and 10 isolated browser scenarios**
passed in CI. Clean npm installation, generated-client check, lint, TypeScript,
production build and production dependency audit passed (zero vulnerabilities).
Disposable PostgreSQL 16 migration upgrade/downgrade/re-upgrade through `0014`
and repeated seeds passed. Read-only public desktop/mobile Playwright: **1 passed**.
The native Windows pywebview window remains outside this browser verification.

## Resulting behavior and data

- NCAA fixtures are visible alongside recorded schedules through a league filter.
- New accounts show the empty tracker. Pick deletion correctly returns HTTP 204;
  taken lines/prices remain unchanged after market movement and pending edits.
- Credits are virtual and non-monetary: zero initial balance, approved requests
  and auditable adjustments, retained history, 1,000-credit UTC monthly request
  cap, no purchase/transfer/withdrawal/redemption. Picks still use independent units.
- Users with picks or credit history must be deactivated instead of deleted.
- Gato's ten imported picks retain **4 wins / 6 losses**, unknown odds and null
  profit/ROI. All 13 original definitions are **unresolved/pending**; Malakai's
  side was not guessed. No production pick/history data was rewritten.

## Remaining work

- Obtain original-card dates/jornada or opponents and Malakai Toney's side before
  grading those 13 definitions; keep unknown taken odds null.
- Define automatic credit stake/debit/settlement accounting as a separate milestone.
- NFL ingestion, a live odds provider, CLV, email verification and password-reset
  delivery remain future scope. CFBD/MLB schedule adapters already exist.

## Deployment context

Frontend: https://dgnweb-production.up.railway.app/
API: https://dgn-picks-production.up.railway.app

Always commit/push reviewed source to GitHub, deploy the same committed application
code directly to Railway and verify the services. Record source SHA/deployment IDs.
In WSL, invoke `@railway/cli/bin/railway.exe` directly; the Windows GitHub CLI
credential supports workflow updates, unlike the current WSL OAuth credential.
Preserve unrelated `.claude/skills` working-tree changes.
