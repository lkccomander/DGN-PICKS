# Compact sportsbook dashboard

## Purpose

Apply the user's Pinnacle-inspired visual direction to the deployed DGN-PICKS dashboard.

## Scope / Non-scope

Restyle the existing frontend with compact sans-serif typography, navigation, tabular picks, a game sidebar, and responsive layouts. Keep the existing Railway API contract and decimal handling. No provider integration, seed changes, migration, wagering, or copied third-party code/assets.

## Progress

Paused at the user's request. See [STATUS.md](../../../STATUS.md) for the full handoff. The attempted page/CSS replacement was rejected by patch validation; no frontend edits were applied.

- [x] Read product, architecture, branding, and plan instructions; inspect existing UI.
- [x] Open supplied reference; text browser receives only a JavaScript shell.
- [x] Implement compact dashboard and filters.
- [ ] Validate desktop/mobile rendering and loading/error/empty states. (Frontend lint/build and backend pytest completed; browser rendering and Railway smoke check remain pending.)
- [x] Commit and push through the established GitHub → Railway workflow; check deployment.

## Implementation plan

1. Replace oversized hero with a compact NCAA board heading.
2. Add navigation rail and table columns for the already available pick fields.
3. Retain concurrent API reads and numeric normalization, add cancellable refresh and presentation filters.
4. Apply DGN navy/blue/red tokens and the blue-white-red-white-blue stripe below the wordmark.

## Validation

Frontend lint/build completed through the Windows Node runtime. Backend pytest passes (`39 passed`). Browser rendering, Compose-backed migration checks, and Railway smoke checks remain pending. Railway remains the runtime target; any local preview is temporary test infrastructure.

## Surprises & Discoveries

The games API exposes only team IDs. Keep those as honest fallbacks; do not invent names or odds for this styling task. Analytics is aggregate across users, so label its scope explicitly.

## Decision Log

- 2026-09-08: Use original DGN-PICKS CSS with sportsbook-style density and tabular values. Preserve distinct branding; no Pinnacle CSS, assets, or exact layout copied.
- 2026-09-08: Keep this milestone presentational and preserve the existing API calculations and data.

## Outcomes & Retrospective

Implemented the compact board UI in `apps/web/src/app/page.tsx` and `globals.css`: section navigation, searchable/result-filtered picks, game-status filters, aligned selection/line/risk/status columns, cancellable refreshes, and numeric normalization for Decimal-shaped API values. Frontend lint/build completed through PowerShell; backend pytest and browser checks are still pending.
