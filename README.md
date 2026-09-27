# DGN-PICKS

NCAA College Football picks, lines, props, and line movement tracker. DGN-PICKS is an analytics and prediction tracking product; picks use units and the app does not take or pay money.

## Current project state

The audit and remediation checklist is in [PROJECT-RECAP.md](PROJECT-RECAP.md) and [the continuation checkpoint](docs/checkpoints/2026-09-24-remediation.md). Local code changes for API privacy and sessions, seed accuracy, archived legacy demo data, analytics, desktop request protections, the account UI, and generated API clients have been recorded in the current branch. The most recent recorded results are 84 API tests, 18 desktop tests, frontend lint/type/build, and execution of generated migration SQL through revision `0009_audit_integrity` on disposable PostgreSQL 18. The later browser acceptance and final documentation verification are pending. This does not establish deployed behavior.

The last deployment snapshot in the repository was verified on 2026-09-10. Recheck the live services before treating their status as current.

| Service | Railway URL |
|---|---|
| Frontend | https://dgnweb-production.up.railway.app/ |
| API | https://dgn-picks-production.up.railway.app |

## Stack and structure

- Next.js + TypeScript: `apps/web`
- FastAPI + SQLAlchemy + Alembic: `apps/api`
- Generated OpenAPI client: `packages/api-client`
- Deterministic provider fixtures: `data/fixtures`
- Desktop operations console: `ext-tools`

The API is a modular monolith. The deterministic local fixture provider remains the MVP data source; no live odds provider is connected.

## Local configuration

Copy `.env.example` to the ignored root `.env`, replace the placeholders, and export those values into your shell before starting the services. The Python API does not automatically load that file. In Bash, use `set -a; . ./.env; set +a`. Never use the example credentials outside a disposable local environment. The API reads `DATABASE_URL` and `DGN_AUTH_*`; the Next.js server uses `DGN_API_INTERNAL_URL` to reach the API, and that value stays server-side.

Install API dependencies with `python -m pip install -e apps/api` and web dependencies with `npm ci --prefix apps/web`. Start PostgreSQL, then run the following from the repository root against a fresh disposable local database:

```sh
npm run db:migrate
python scripts/verify_seed.py
```

The seed verification inserts deterministic local users and fixtures and is intended for that disposable database. In separate terminals, run `npm run api` and `npm run dev:web` from the repository root.

The optional `DGN_API_WRITE_MODE=development` plus `DGN_API_WRITE_KEY` boundary is for catalog setup only when API authentication is not configured. It is disabled by default. Pick creation, edits, grading, and deletion use signed bearer sessions. The web app does not have a development-key pick-write switch.

## Accounts and API access

- `GET /api/v1/users` and `GET /api/v1/users/{id}` are public projections; they omit email and country.
- `GET /api/v1/admin/users` and `/api/v1/admin/users/{id}` include private fields and require an `admin` or `editor` bearer session.
- `GET /api/v1/auth/account` returns the authenticated account's own profile.
- Registration and login are `POST /api/v1/auth/register` and `POST /api/v1/auth/login`. User sessions are checked against the current account and are invalidated when an account is deactivated/reactivated or its password changes.
- Authenticated users create and manage their own pending picks. Editors/admins can manage catalog resources. A new prediction is accepted only for an open market on a scheduled or live game.
- API write authorization must be configured with `DGN_AUTH_SECRET`, `DGN_AUTH_USERNAME`, and `DGN_AUTH_PASSWORD`; operator access can use role `admin` or `editor`. A `viewer` session is read-only.

The `/admin` web console uses the protected admin API proxy. Public user listings never expose contact fields.

## Picks, seeds, and analytics

Seed users are `gato`, `daran`, and `noch`. The 13 original Gato definitions remain visible as unresolved product input until authoritative event, side, and taken-price details are available. QA outcome examples are separate fixtures and do not create product picks. Existing strict matches to the old invented demo picks can be reported by the quarantine script; it is dry-run by default and requires an explicit `--apply` to archive records.

Odds snapshots are append-oriented and a pick retains its taken line and price. Analytics reports pending exposure separately. Settled ROI uses priced, settled stake; if settled price data is incomplete, profit and ROI are unavailable rather than guessed.

DGN-PICKS currently tracks picks in units. It does not keep or promise a token balance/ledger, real-money balance, deposits, withdrawals, or redemption. Virtual token accounting, email verification, password reset delivery, a live odds provider, and CLV remain future work.

## Local browser acceptance

The Playwright pick flow writes test data. Run it only against a disposable database and loopback API/web origins. Provide the isolated operator credentials as `E2E_OPERATOR_USERNAME` and `E2E_OPERATOR_PASSWORD`, plus `E2E_API_URL` and `E2E_WEB_URL`, then run `npm run test:e2e` from `apps/web`. It registers a unique test account and adds fixture history; reset the disposable database after the run.

Other checks are described in `.github/workflows/validate.yml`. Use [STATUS.md](STATUS.md) and the [checkpoint](docs/checkpoints/2026-09-24-remediation.md) for current evidence and next steps.

## Project rules

Read [AGENTS.md](AGENTS.md), the [product specification](docs/product-specs/001-local-mvp.md), [architecture](ARCHITECTURE.md), [brand guide](docs/design-docs/branding.md), and [plan index](PLANS.md) before substantial changes. Record changes to product semantics in the spec's Decision Log.


## Importing supplied picks

Editors/admins can preview a verified manifest using `POST /api/v1/admin/pick-imports` and apply it with `?apply=true`. The CLI equivalent is `python scripts/import_pick_manifest.py --manifest data/imports/gato-2026-09-26.json` (add `--apply` to commit). An owner/batch/item key prevents duplicate imports. The operation preserves supplied lines and source evidence, leaves missing odds unknown, records actual ingestion time separately from the stated date, and never manufactures odds history. Imported markets stay closed because a supplied historical pick is not a current offered price. See [Gato's source review](docs/data-reviews/2026-09-26-gato-picks.md).
