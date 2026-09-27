# ARCHITECTURE.md — DGN-PICKS

## Overview
Local-first NCAA College Football picks, game-lines, props, and line-movement tracker.

```text
Browser
  -> Next.js + TypeScript
  -> FastAPI + Python
  -> PostgreSQL
       -> domains: users, token ledger, teams, players, games, markets, odds, props, picks
       -> provider boundary
            -> FixtureProvider (MVP)
            -> real provider adapter (future)
```

## Repository boundaries
- `apps/web`: UI.
- `apps/api`: API, domain logic, persistence, ingestion.
- `packages/api-client`: generated OpenAPI client/types.
- `data/fixtures`: deterministic external-style fixture payloads.
- `data/seeds`: deterministic app seed definitions.
- `docs`: product/design/execution docs.
- `infra/local`: local infrastructure.

## Critical invariants
1. `OddsSnapshot` is historical and append-oriented.
2. A Pick preserves the line/price taken at creation time.
3. Every Pick has `user_id`.
4. Provider-specific IDs/names never leak into core UI/domain without normalization.
5. Decimal odds are canonical for calculations.
6. Timestamps persist in UTC.
7. Virtual tokens are non-monetary paper credits; they cannot be deposited,
   withdrawn, transferred, or redeemed.
8. Token balance changes should be auditable and append-oriented through a token
   ledger rather than unexplained direct balance edits.


## Authentication and data visibility
- Public `/api/v1/users` responses contain public profile fields only; private profile data is available to editors/admins under `/api/v1/admin/users` and to the account owner under `/api/v1/auth/account`.
- User sessions bind to a persisted user ID and session version and are validated against the current active account. Account deactivation/reactivation and password changes revoke prior sessions.
- Pick writes require signed bearer sessions. User role can only access its own picks; admin/editor roles can perform permitted management operations. The development API write key is only a local catalog setup fallback when API session signing is not configured.
- Archived legacy demo picks retain their original record terms and references, but are excluded from ordinary pick operations and analytics.

## MVP calculation and seed semantics
- The 13 supplied Gato picks are unresolved product definitions until the missing event, side, or taken-price facts are supplied. They are never completed by matching QA fixtures.
- Pending exposure is separate from settled risk. ROI uses settled stake with known taken odds. Incomplete settled price data makes profit/ROI unavailable rather than treating unknown results as zero.
- MVP stakes are units. Virtual token balances and ledger are future work; no monetary balance or redemption exists.
