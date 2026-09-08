# DGN-PICKS — session handoff

Updated: 2026-09-08 UTC (September 7 in Costa Rica).
Session paused at the user's request. Resume here next session after reading the source-of-truth documents in AGENTS.md.

## Workflow and deployments

- Workflow: GitHub → Railway. The user does not require a separate local application environment.
- Frontend: https://dgnweb-production.up.railway.app/
- API: https://dgn-picks-production.up.railway.app
- GitHub: https://github.com/lkccomander/DGN-PICKS
- Branch: `main`, matching the local `origin/main` reference at `18b3eae`.
- Latest pushed commit: `18b3eae fix: normalize analytics values in dashboard`.
- Do not equate a pushed commit with a verified Railway deployment.

## Current status

- API v1 routes and the initial dashboard are committed and pushed.
- PostgreSQL URL normalization and frontend CORS fixes were pushed; subsequent API checks succeeded.
- Last user-provided Railway results showed 4 games, 7 pending picks, 7 units risked, and zero profit. These are historical observations, not a fresh live check at handoff.
- `GET /api/v1/picks?user=gato` previously returned 500. Migration `0006_backfill_pick_timestamps` was pushed in `b882360` to repair missing timestamps.
- The frontend subsequently crashed on Decimal strings passed to `.toFixed()`. Commit `18b3eae` converts summary values to numbers. Its successful production rendering has not yet been independently verified.
- Full frontend lint/build and backend pytest were not successfully run during the earlier implementation work. Prior Python compilation was syntax validation only.

## Active task: compact sportsbook-style frontend

User reference: https://www.pinnacle.com/en/football/ncaa/matchups/#all

Use original DGN-PICKS CSS inspired by a compact sportsbook board. Preserve navy/blue/red branding and the blue → white → red → white → blue stripe. Do not copy Pinnacle code, assets, text, trademarks, or its exact layout.

Execution plan: [Compact dashboard](docs/exec-plans/active/2026-09-08-compact-dashboard.md).

Completed this session:

- Read the product spec, architecture, branding, plan rules, and React best-practices skill.
- Inspected the current frontend and opened the reference URL; the text browser exposed only its JavaScript shell.
- Created the active execution plan.

Implemented in the current working tree, not yet committed or pushed:

- Compact section navigation, aligned pick columns, searchable picks, result filters, and game-status filters.
- Cancellable concurrent dashboard refreshes.
- Numeric normalization for summary and pick Decimal-shaped API values.
- Aggregate summary remains presented without implying it is only Gato's data.

## Next session

1. Run frontend lint/build and browser checks for desktop, mobile, and loading/error/empty states; Node/npm is currently blocked by the WSL bridge.
2. Verify Railway frontend/API responses after deployment, including picks and analytics.
3. Review seed correctness separately; do not invent team-name mappings.
4. Commit scoped changes and push through the established GitHub → Railway workflow only after validation.

## Known follow-up work

- Game responses currently expose team IDs, not team names; do not invent name mappings in CSS/UI work.
- Audit seed correctness separately. There are 13 Gato definitions but only 7 stored picks reported. The seed service currently has no explicit guard rejecting the unresolved Malakai Toney side and copies fixture odds into matched picks. Do not repeat the earlier claim that all 7 picks are resolved without checking them against the product spec.
- No live odds provider is connected. Use deterministic fixtures until that milestone is explicitly taken on.

## Working tree at pause

- No tracked application-code changes relative to `18b3eae`.
- New handoff documentation and compact-dashboard plan remain uncommitted.
- Existing untracked `DGN-PICKS.code-workspace` and `logs/` belong to the user; keep them out of release commits.
- `logs/railwaystatus.md` is an older dashboard report and is not proof of the latest deployment's state.

## Validation tooling

The Linux shell has no `node` executable available through PATH. Windows Node.js exists at `C:\Program Files\nodejs`, and browser installations exist under `C:\Users\lkcco\AppData\Local\ms-playwright`. Tool probes did not establish a working lint/build/browser command before the pause. Resume that verification rather than claiming checks passed.
