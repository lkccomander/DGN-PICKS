# Compact sportsbook dashboard

## Purpose

Apply the user's Pinnacle-inspired visual direction to the deployed DGN-PICKS dashboard.

## Scope / Non-scope

Restyle the existing frontend with compact sans-serif typography, navigation, tabular picks, a game sidebar, and responsive layouts. Keep the existing Railway API contract and decimal handling. No provider integration, seed changes, migration, wagering, or copied third-party code/assets.

## Progress

Landing-page composition updated to an original DGN-PICKS sportsbook-style board based on the user's supplied layout reference. The page now uses a utility header, primary navigation, sports rail, promotional hero, market board, games slate, bet slip, and tracked-picks drawer.

- [x] Read product, architecture, branding, and plan instructions; inspect existing UI.
- [x] Open supplied reference; text browser receives only a JavaScript shell.
- [x] Implement compact dashboard and filters.
- [ ] Validate desktop/mobile rendering and loading/error/empty states. (Source-level checks pass; frontend lint/build and browser rendering remain pending because Node is unavailable in the current WSL1 shell.)
- [x] Commit the dashboard integration; push and deployment check remain pending because deployment DNS is unavailable from this environment.

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
- 2026-09-10: Serve the dashboard read model through a same-origin Next.js route. The route aggregates the existing read-only FastAPI calls server-side, preserving their contract while avoiding browser-to-API cross-origin failures.
- 2026-09-14: Recompose the landing page around the supplied sportsbook-style information hierarchy using original DGN-PICKS components, copy, colors, and CSS. Do not reuse the reference site's branding, imagery, exact layout, or assets.

## Outcomes & Retrospective

Implemented the compact board UI in `apps/web/src/app/page.tsx` and `globals.css`: original sportsbook-style landing composition, sports navigation rail, utility/auth header, promo hero, searchable/result-filtered picks, date/team/conference/game-status/market-availability filters, aligned market selections, concurrent market/history loading, opening/current line values, SVG movement traces, cancellable refreshes, and numeric normalization for Decimal-shaped API values. Backend pytest was previously passing; frontend lint/build and browser checks remain pending in the current Node-unavailable environment.
