# ARCHITECTURE.md — DGN-PICKS

## Overview
Local-first NCAA College Football picks, game-lines, props, and line-movement tracker.

```text
Browser
  -> Next.js + TypeScript
  -> FastAPI + Python
  -> PostgreSQL
       -> domains: users, teams, players, games, markets, odds, props, picks
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
