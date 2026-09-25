# DGN-PICKS — session handoff

Updated: 2026-09-24. **Paused at the user’s request; remediation is in progress.**

Read the [checkpoint](docs/checkpoints/2026-09-24-remediation.md) first when resuming.
The [project recap](PROJECT-RECAP.md) preserves the original audit; its baseline failures should not be mistaken for current remediation results.

## Completed locally

- [x] API privacy, revocable sessions, ownership, and new-pick eligibility fixes.
- [x] Accurate unresolved seed definitions, reversible quarantine tooling, and settled analytics.
- [x] Desktop request boundary and protected account UI.
- [x] Dependency updates, regenerated clients, and CI implementation.
- [x] API: 84 passing tests; desktop: 18 passing tests.
- [x] Web lint, TypeScript, and production build passed before the last small registration edit.
- [x] Migration SQL through `0009_audit_integrity` executed on disposable PostgreSQL 18; server stopped.

## Next session

- [ ] Recheck final edits and run updated browser acceptance on an isolated database.
- [ ] Finish documentation/environment reconciliation and product Decision Log.
- [ ] Complete the [active remediation plan](docs/exec-plans/active/2026-09-24-audit-remediation.md).
- [ ] Prepare and verify deployment separately; no remediation deployment or production quarantine has occurred.

## Deployment context

The workflow is GitHub → Railway. Local verification does not establish deployed behavior.
Frontend: https://dgnweb-production.up.railway.app/
API: https://dgn-picks-production.up.railway.app

The last audit inspected base commit `01b3d7e`. Preserve unrelated `.claude/skills` worktree changes.
No live odds provider is connected; fixtures remain deterministic.
