# DGN-PICKS — session handoff

Updated: 2026-09-26. **Publishing the requested Gato card; import code and migration validation passed.**

Use the [checkpoint](docs/checkpoints/2026-09-24-remediation.md) for recorded evidence and remaining acceptance steps.
The [project recap](PROJECT-RECAP.md) preserves the original audit; its baseline failures should not be mistaken for current remediation results.

## Completed locally

- [x] API privacy, revocable sessions, ownership, and new-pick eligibility fixes.
- [x] Accurate unresolved seed definitions, reversible quarantine tooling, and settled analytics.
- [x] Desktop request boundary and protected account UI.
- [x] Dependency updates, regenerated clients, and CI implementation.
- [x] API: 105 passing tests; desktop: 18 passing tests from the remediation checkpoint.
- [x] Current web lint, TypeScript, and production build passed.
- [x] Migration SQL through `0011_restore_pick_leg_snapshot` executed on disposable PostgreSQL 18; server stopped.
- [x] Ten-entry Gato manifest rehearsed with owner/line/unknown-price preservation and repeatability.

## Next session

- [ ] Recheck final edits and run updated browser acceptance on an isolated database.
- [x] Reconcile documentation, environment examples, architecture, and product Decision Log.
- [ ] Complete the [active remediation plan](docs/exec-plans/active/2026-09-24-audit-remediation.md).
- [ ] Prepare and verify deployment separately; no remediation deployment or production quarantine has occurred.

The earlier documentation-only continuation ran no tests. The subsequent Gato import work ran the checks recorded above.

## Deployment context

The workflow is GitHub → Railway. Local verification does not establish deployed behavior.
Frontend: https://dgnweb-production.up.railway.app/
API: https://dgn-picks-production.up.railway.app

The last audit inspected base commit `01b3d7e`. Preserve unrelated `.claude/skills` worktree changes.
No live odds provider is connected; fixtures remain deterministic.
