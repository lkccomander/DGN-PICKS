# MVP validation and direct Railway release — 2026-10-14

Local date: October 14, America/Guatemala. Application source:
`47a127af0220b98253a676f72829f082ae49692f` (includes `cbd7ab3`).

## Publication evidence

Reviewed source was committed and pushed to GitHub before direct Railway uploads.
[GitHub CI run 38605399888](https://github.com/lkccomander/DGN-PICKS/actions/runs/38605399888)
completed successfully for this exact application commit.

Both services were uploaded directly from a clean Git archive of that commit;
no working-tree changes, local environments or dependency folders were uploaded.
Archive SHA256: `f5eb24bcd73d32c9d3a759659f0491ee106aa741ebaae233b4851eabb77235f2`.

| Service | Direct Railway deployment | Verified status | URL |
|---|---|---|---|
| API | `e9da9532-a4a6-4bd0-af58-4b96e74212ee` | SUCCESS | https://dgn-picks-production.up.railway.app |
| Web | `d5de63fc-67a4-4f9c-80b6-f76c50cbd115` | SUCCESS | https://dgnweb-production.up.railway.app/ |

GitHub autodeploys also exist in this project; the IDs above identify the required
**direct uploads**, not those automatic deployments. Later documentation-only
commits do not change the application code covered by this release.

The WSL GitHub credential lacked workflow scope. The existing Windows GitHub CLI
credential already had that scope and completed the pushes without changing
account permissions or Git configuration.

## Validation

- API: **116 passed** in CI, including ownership, revocable sessions, immutable
  pick prices, odds/ROI rules, unresolved definitions and virtual-credit rules.
- Desktop: **29 passed**.
- Browser: **10 passed together** in CI against isolated PostgreSQL/API/built
  Next/Flask. The public import test is intentionally skipped there and runs
  separately against production.
- Clean `npm ci`, generated-client consistency, lint, standalone TypeScript,
  production build and production dependency audit passed; audit found zero
  vulnerabilities. Locked patches include Next/ESLint 16.3.8, sharp 0.35.5 and
  source-map-js 1.2.2.
- Disposable PostgreSQL 16: upgrade through `0014`, full downgrade to base and
  re-upgrade passed. Repeated seed preserved all 13 unresolved definitions and
  created no invented product picks.
- Production: web and API health return HTTP 200. Public user projections omit
  email, country, balance and password hashes; account/credit/admin reads reject
  anonymous access with HTTP 401.
- Read-only production Playwright: **1 passed**, covering all ten imported Gato
  rows without authentication on 1440px and 390px viewports. No production test
  writes were made.
- Public credit page offers virtual-credit requests and no monetary payment
  methods. The private mobile account screenshot passed the no-overflow check.

## Resulting behavior

The market board again displays NCAA fixtures with a real league filter while
retaining recorded MLB schedules. Original unresolved Gato definitions display
Unresolved/pending rather than fabricated losses. New accounts see an empty
tracker. Pick deletion forwards HTTP 204 correctly and removes the row.

The user confirmed non-monetary virtual credits. New accounts start at zero;
approvals and auditable manual adjustments append to the retained ledger.
Pending/approved requests share a 1,000-credit UTC monthly cap. Concurrent
approvals cannot double-credit a request; owner locks serialize quota checks.
Users with request or ledger history receive HTTP 409 on deletion and must be
deactivated instead, retaining that history. USD, payment methods and fictional
account verification were removed. Picks remain in units independently of credits.

## Data and limits

Gato retains ten active imported picks: **4 wins, 6 losses**, all without known
odds. Profit and ROI remain null. All **13 original definitions** remain
unresolved/pending, including Malakai Toney's unspecified side. No historical
pick terms, results, prices or odds observations were rewritten by this work.

The native Windows pywebview window was not graphically tested; its Flask UI was
exercised in Chromium and desktop behavior covered by unit tests. PostgreSQL
migration reversal was tested on disposable data, not as a production restore
rehearsal. Temporary test servers were stopped after verification.

Original-card dates/opponents and Malakai's side still need authoritative facts.
Automatic credit staking/settlement, NFL ingestion, live odds, CLV, email
verification and password-reset delivery remain separate future work.
